"""Auth service."""
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token


def register_user(db: Session, data: UserCreate) -> User:
    """Create a new user."""
    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: UserLogin) -> User | None:
    """Authenticate user by email and password."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        return None
    return user


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Get user by ID."""
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        return None
    return db.query(User).filter(User.id == uid).first()
