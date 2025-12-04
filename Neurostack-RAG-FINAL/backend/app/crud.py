from sqlalchemy.orm import Session
from .models import UserModel, UserCreate

# 1. Get User by Username
def get_user_by_username(db: Session, username: str):
    """Retrieves a user by username."""
    return db.query(UserModel).filter(UserModel.username == username).first()

# 2. Create New User
def create_user(db: Session, user: UserCreate, hashed_password: str):
    """Creates a new user in the database."""
    db_user = UserModel(
        name=user.name,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user