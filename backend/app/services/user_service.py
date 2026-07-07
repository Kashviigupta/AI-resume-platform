from sqlalchemy.orm import Session

from app.models.user import User
from app.auth.security import hash_password, verify_password


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, full_name: str, email: str, password: str) -> User:
    user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # loads the auto-generated id/created_at back onto the object
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Returns the User if email+password are correct, otherwise None."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
