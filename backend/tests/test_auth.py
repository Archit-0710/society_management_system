import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.core.security import hash_password

# Test database setup
TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/society_db_test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def resident_user(db_session):
    """Create a resident user for testing."""
    user = User(
        name="Test Resident",
        email="resident@test.com",
        password_hash=hash_password("password123"),
        phone="1234567890",
        flat_no="101",
        role=UserRole.RESIDENT,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    user = User(
        name="Test Admin",
        email="admin@test.com",
        password_hash=hash_password("adminpass"),
        phone=None,
        flat_no=None,
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_register_new_user(client):
    """Test successful user registration."""
    response = client.post("/api/auth/register", json={
        "name": "New User",
        "email": "newuser@test.com",
        "password": "securepass",
        "phone": "9876543210",
        "flat_no": "202",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, resident_user):
    """Test registration with duplicate email fails."""
    response = client.post("/api/auth/register", json={
        "name": "Another User",
        "email": resident_user.email,
        "password": "password123",
        "flat_no": "303",
    })
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_register_creates_resident_role(client, db_session):
    """Test that public registration always creates RESIDENT role."""
    response = client.post("/api/auth/register", json={
        "name": "New Resident",
        "email": "resident2@test.com",
        "password": "pass1234",
        "flat_no": "404",
    })
    assert response.status_code == 201
    
    # Verify user has RESIDENT role
    user = db_session.query(User).filter(User.email == "resident2@test.com").first()
    assert user is not None
    assert user.role == UserRole.RESIDENT


def test_login_valid_credentials(client, resident_user):
    """Test login with valid credentials."""
    response = client.post("/api/auth/login", json={
        "email": resident_user.email,
        "password": "password123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client):
    """Test login with non-existent email."""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "password123",
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_invalid_password(client, resident_user):
    """Test login with wrong password."""
    response = client.post("/api/auth/login", json={
        "email": resident_user.email,
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_get_me_authenticated(client, resident_user):
    """Test /auth/me with valid token."""
    # Login first
    login_response = client.post("/api/auth/login", json={
        "email": resident_user.email,
        "password": "password123",
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == resident_user.id
    assert data["email"] == resident_user.email
    assert data["name"] == resident_user.name
    assert data["role"] == "RESIDENT"


def test_get_me_unauthenticated(client):
    """Test /auth/me without token fails."""
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # No credentials


def test_get_me_invalid_token(client):
    """Test /auth/me with invalid token."""
    response = client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid_token_here"
    })
    assert response.status_code == 401


def test_admin_user_authentication(client, admin_user):
    """Test admin can authenticate."""
    response = client.post("/api/auth/login", json={
        "email": admin_user.email,
        "password": "adminpass",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Verify role in /me
    me_response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_response.status_code == 200
    assert me_response.json()["role"] == "ADMIN"