import unittest
import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.complaint import Complaint, ComplaintStatus, ComplaintPriority
from app.models.complaint_history import ComplaintStatusHistory
from app.models.notice import Notice
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.core.security import hash_password, verify_password
from app.services import complaint_service, category_service, notice_service, notification_service
from app.services.storage_service import storage_service
from fastapi import HTTPException


class TestAPIHardening(unittest.TestCase):
    
    def setUp(self):
        """Create database session and start a transaction."""
        self.db = SessionLocal()
        self.db.begin_nested()
        
        self.unique_id = str(uuid.uuid4())[:8]
        
        # Setup mock test data
        self.category = Category(
            name=f"Plumbing Test {self.unique_id}",
            description="Plumbing issues description",
            is_active=True
        )
        self.db.add(self.category)
        
        self.resident = User(
            name=f"Resident Hardening {self.unique_id}",
            email=f"resident_hard_{self.unique_id}@test.com",
            password_hash=hash_password("password123"),
            phone="1122334455",
            flat_no="707",
            role=UserRole.RESIDENT
        )
        self.db.add(self.resident)
        
        self.admin = User(
            name=f"Admin Hardening {self.unique_id}",
            email=f"admin_hard_{self.unique_id}@test.com",
            password_hash=hash_password("adminpassword"),
            phone="9988776655",
            flat_no=None,
            role=UserRole.ADMIN
        )
        self.db.add(self.admin)
        
        self.db.flush()

    def tearDown(self):
        """Rollback all database insertions/changes during tests."""
        self.db.rollback()
        self.db.close()

    def test_password_truncation(self):
        """Verify password hashing works and passwords truncate correctly."""
        passwd = "a" * 80  # exceeds 72 limit
        hashed = hash_password(passwd)
        self.assertTrue(verify_password(passwd, hashed))
        self.assertTrue(verify_password("a" * 72, hashed))  # Should verify since it truncates at 72

    def test_file_type_and_size_validation(self):
        """Verify uploaded file type and size restrictions."""
        # Valid files
        storage_service.validate_file("image/png", 1024 * 1024)
        storage_service.validate_file("image/jpeg", 5 * 1024 * 1024)
        
        # Invalid mime type
        with self.assertRaises(HTTPException) as ctx:
            storage_service.validate_file("application/pdf", 1024)
        self.assertEqual(ctx.exception.status_code, 400)
        
        # Invalid size limit (exceeds 5MB)
        with self.assertRaises(HTTPException) as ctx:
            storage_service.validate_file("image/png", 5 * 1024 * 1024 + 1)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_category_duplicate_validation(self):
        """Verify duplicate categories are rejected with ValueError."""
        # Create duplicate category name
        from app.schemas.category import CategoryCreate
        req = CategoryCreate(name=self.category.name, description="Duplicate category name")
        with self.assertRaises(ValueError):
            category_service.create_category(self.db, req)

    def test_complaint_workflow_and_forbidden_reopening(self):
        """Verify complaint status transition matrix and history audit counts."""
        complaint = complaint_service.create_complaint(
            db=self.db,
            category_id=self.category.id,
            description="Testing complaint flow validation logic.",
            photo_url="/uploads/mock.png",
            resident_id=self.resident.id
        )
        
        # Verify initial history (old_status=None, new_status=OPEN)
        history = complaint.status_history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].old_status, None)
        self.assertEqual(history[0].new_status, ComplaintStatus.OPEN)
        
        # Valid Transition: OPEN -> IN_PROGRESS
        from app.schemas.complaint import ComplaintStatusUpdate
        upd1 = ComplaintStatusUpdate(status="IN_PROGRESS", note="Assigned worker A")
        complaint_service.update_complaint_status(self.db, complaint.id, upd1, self.admin.id)
        self.assertEqual(complaint.status, ComplaintStatus.IN_PROGRESS)
        self.assertEqual(len(complaint.status_history), 2)
        
        # Valid Transition: IN_PROGRESS -> RESOLVED
        upd2 = ComplaintStatusUpdate(status="RESOLVED", note="Issue solved")
        complaint_service.update_complaint_status(self.db, complaint.id, upd2, self.admin.id)
        self.assertEqual(complaint.status, ComplaintStatus.RESOLVED)
        self.assertIsNotNone(complaint.resolved_at)
        
        # Forbidden Transition: RESOLVED -> OPEN (cannot reopen)
        upd3 = ComplaintStatusUpdate(status="OPEN", note="Reopen it please")
        with self.assertRaises(ValueError):
            complaint_service.update_complaint_status(self.db, complaint.id, upd3, self.admin.id)
            
        # Forbidden Transition: RESOLVED -> IN_PROGRESS
        upd4 = ComplaintStatusUpdate(status="IN_PROGRESS", note="Back to active")
        with self.assertRaises(ValueError):
            complaint_service.update_complaint_status(self.db, complaint.id, upd4, self.admin.id)

    def test_complaint_priority_locking(self):
        """Verify priority updates are disallowed once resolved."""
        complaint = complaint_service.create_complaint(
            db=self.db,
            category_id=self.category.id,
            description="Testing priority locks on resolved states.",
            photo_url=None,
            resident_id=self.resident.id
        )
        
        # Can update priority while open
        from app.schemas.complaint import ComplaintPriorityUpdate, ComplaintStatusUpdate
        p_upd = ComplaintPriorityUpdate(priority="HIGH")
        complaint_service.update_complaint_priority(self.db, complaint.id, p_upd, self.admin.id)
        self.assertEqual(complaint.priority, ComplaintPriority.HIGH)
        
        # Resolve the complaint
        upd = ComplaintStatusUpdate(status="RESOLVED", note="done")
        complaint_service.update_complaint_status(self.db, complaint.id, upd, self.admin.id)
        
        # Cannot update priority on resolved complaint
        with self.assertRaises(ValueError):
            complaint_service.update_complaint_priority(self.db, complaint.id, p_upd, self.admin.id)

    def test_overdue_detection_and_escalation_rules(self):
        """Verify overdue math and priority escalation based on configured settings."""
        complaint = complaint_service.create_complaint(
            db=self.db,
            category_id=self.category.id,
            description="Testing overdue and escalation setting triggers.",
            photo_url=None,
            resident_id=self.resident.id
        )
        # Check not overdue initially
        self.assertFalse(complaint_service.is_complaint_overdue(complaint))
        
        # Set back by 8 days
        complaint.created_at = datetime.now(timezone.utc) - timedelta(days=8)
        self.db.flush()
        # Verify now marked as overdue
        self.assertTrue(complaint_service.is_complaint_overdue(complaint))
        
        # Test Escalation Math
        # LOW -> MEDIUM after LOW_TO_MEDIUM_DAYS (3)
        # Reset priority to LOW
        complaint.priority = ComplaintPriority.LOW
        complaint.created_at = datetime.now(timezone.utc) - timedelta(days=4)
        self.db.flush()
        escalated = complaint_service.escalate_priority_if_needed(self.db, complaint)
        self.assertTrue(escalated)
        self.assertEqual(complaint.priority, ComplaintPriority.MEDIUM)
        
        # MEDIUM -> HIGH after MEDIUM_TO_HIGH_DAYS (5)
        complaint.created_at = datetime.now(timezone.utc) - timedelta(days=6)
        self.db.flush()
        escalated = complaint_service.escalate_priority_if_needed(self.db, complaint)
        self.assertTrue(escalated)
        self.assertEqual(complaint.priority, ComplaintPriority.HIGH)

    def test_important_notice_bulk_notifications_and_smart_ordering(self):
        """Verify important notice bulk triggers and smart ordering (important first)."""
        # Create notice 1 - regular
        from app.schemas.notice import NoticeCreate
        req_reg1 = NoticeCreate(title="Reg A", content="Content A", is_important=False)
        notice_service.create_notice(self.db, req_reg1, self.admin.id)
        
        # Create notice 2 - important (should trigger notifications for all residents)
        req_imp = NoticeCreate(title="Imp B", content="Content B", is_important=True)
        notice_service.create_notice(self.db, req_imp, self.admin.id)
        
        # Create notice 3 - regular recent
        req_reg2 = NoticeCreate(title="Reg C", content="Content C", is_important=False)
        notice_service.create_notice(self.db, req_reg2, self.admin.id)
        
        # Check notices list (Important first, then newer regular notices first)
        db_notices = notice_service.get_notices(self.db)
        notices = [n for n in db_notices if n.created_by == self.admin.id]
        
        self.assertEqual(len(notices), 3)
        self.assertEqual(notices[0].is_important, True)
        self.assertEqual(notices[0].title, "Imp B")
        self.assertEqual(notices[1].title, "Reg C")  # Reg C was created after Reg A, so Reg C is second
        self.assertEqual(notices[2].title, "Reg A")
        
        # Check notification bulk entry for the resident
        recipient_notifications = self.db.query(Notification).filter(
            Notification.recipient_id == self.resident.id
        ).all()
        self.assertTrue(len(recipient_notifications) >= 1)
        self.assertEqual(recipient_notifications[0].type, NotificationType.IMPORTANT_NOTICE)

    def test_delete_notice_cascades_safely_ondelete_set_null(self):
        """Verify notice deletion leaves notifications intact via SET NULL."""
        from app.schemas.notice import NoticeCreate
        req_imp = NoticeCreate(title="Delete Me", content="Important notice removal test", is_important=True)
        notice = notice_service.create_notice(self.db, req_imp, self.admin.id)
        
        # Get notifications referencing this notice
        notifs = self.db.query(Notification).filter(Notification.notice_id == notice.id).all()
        self.assertTrue(len(notifs) >= 1)
        
        # Delete notice
        notice_service.delete_notice(self.db, notice.id)
        self.db.flush()
        
        # Verify notifications are not deleted, instead their notice_id is set to None (SET NULL)
        for notif in notifs:
            self.db.refresh(notif)
            self.assertIsNone(notif.notice_id)
            self.assertEqual(notif.type, NotificationType.IMPORTANT_NOTICE)


if __name__ == "__main__":
    unittest.main()