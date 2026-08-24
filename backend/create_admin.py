"""Create an administrator account without exposing its password in source or shell history."""
import argparse
import getpass

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Society Maintenance Tracker administrator.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="Administrator")
    parser.add_argument("--phone", default=None)
    parser.add_argument("--flat-no", default=None)
    args = parser.parse_args()

    password = getpass.getpass("Admin password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")
    if not 6 <= len(password) <= 72:
        raise SystemExit("Password must be between 6 and 72 characters.")

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == args.email.lower()).first():
            raise SystemExit("A user with this email already exists.")
        user = User(
            name=args.name,
            email=args.email.lower(),
            password_hash=hash_password(password),
            phone=args.phone,
            flat_no=args.flat_no,
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        print(f"Created administrator account: {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
