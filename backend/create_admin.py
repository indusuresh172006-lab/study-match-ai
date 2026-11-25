import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import func

from database import SessionLocal, engine
from models import Student, Base
from auth import get_password_hash


def create_first_admin() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Student.id).filter(Student.role == "admin").first():
            raise SystemExit("An admin account already exists; bootstrap is disabled.")

        name = input("Admin name: ").strip()
        raw_email = input("Admin email: ").strip().lower()
        password = getpass.getpass("Admin password (12+ characters): ")
        confirmation = getpass.getpass("Confirm password: ")

        if len(name) < 2:
            raise SystemExit("Name must contain at least 2 characters.")
        try:
            email = str(TypeAdapter(EmailStr).validate_python(raw_email))
        except Exception:
            if "@" not in raw_email or "." not in raw_email.split("@")[-1]:
                raise SystemExit("Enter a valid email address.")
            email = raw_email
        if len(password) < 5:
            raise SystemExit("Password must contain at least 5 characters.")
        if password != confirmation:
            raise SystemExit("Passwords do not match.")
        if db.query(Student.id).filter(func.lower(Student.email) == email).first():
            raise SystemExit("That email is already registered.")

        db.add(Student(
            name=name,
            email=email,
            password_hash=get_password_hash(password),
            role="admin",
        ))
        db.commit()
        print(f"Admin account created for {email}.")
    finally:
        db.close()


if __name__ == "__main__":
    create_first_admin()
