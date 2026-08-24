"""Gmail SMTP delivery for complaint and important-notice notifications."""
import smtplib
from email.message import EmailMessage
from typing import Optional

from app.core.config import settings


class EmailService:
    def __init__(self) -> None:
        self.gmail_email = settings.GMAIL_EMAIL
        self.gmail_app_password = settings.GMAIL_APP_PASSWORD
        self.from_email = settings.EMAIL_FROM or settings.GMAIL_EMAIL

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """Send an email through Gmail's SSL SMTP endpoint."""
        if not self.gmail_email or not self.gmail_app_password:
            return False, "Gmail is not configured. Set GMAIL_EMAIL and GMAIL_APP_PASSWORD."

        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        if html_body:
            message.add_alternative(html_body, subtype="html")

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
                smtp.login(self.gmail_email, self.gmail_app_password)
                smtp.send_message(message)
            return True, None
        except (OSError, smtplib.SMTPException) as exc:
            return False, str(exc)

    def send_complaint_status_email(
        self,
        to_email: str,
        resident_name: str,
        complaint_id: int,
        old_status: str | None,
        new_status: str,
        note: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        body = f"""Dear {resident_name},

Your complaint (ID: {complaint_id}) status has been updated.

Previous status: {old_status or 'New'}
New status: {new_status}
"""
        if note:
            body += f"\nNote: {note}\n"
        body += "\nSociety Management Team"
        return self.send_email(to_email, f"Complaint #{complaint_id} Status Updated", body)

    def send_important_notice_email(
        self,
        to_email: str,
        resident_name: str,
        notice_title: str,
        notice_content: str,
    ) -> tuple[bool, Optional[str]]:
        body = f"""Dear {resident_name},

An important notice has been posted:

{notice_title}

{notice_content}

Society Management Team"""
        return self.send_email(to_email, f"IMPORTANT: {notice_title}", body)


email_service = EmailService()
