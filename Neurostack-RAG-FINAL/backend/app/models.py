from pydantic import BaseModel, Field
from typing import Dict, Any
from sqlalchemy import Column, Integer, String
from .database import Base # CRITICAL: Import Base for SQLAlchemy models

# --------------------
# 1. SQLAlchemy ORM Model (The actual DB table structure)
# --------------------

class UserModel(Base):
    """SQLAlchemy model for the 'users' table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String) # Stored securely in the database


# --------------------
# 2. Pydantic Schemas (The FastAPI Request/Response structure)
# --------------------

class User(BaseModel):
    """Data model for a user in the system (Response Schema)."""
    # NOTE: Does NOT include 'hashed_password' for security
    name: str
    email: str
    username: str
    
    class Config:
        # CRITICAL: Allows Pydantic to read data from ORM objects (like UserModel)
        from_attributes = True

class UserCreate(BaseModel):
    """Schema for a user creating an account (Signup)."""
    name: str = Field(..., min_length=1, max_length=18)
    email: str = Field(..., description="user's email address.")
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6, description="Password must be at least 6 length")


class UserLogin(BaseModel):
    '''Schema for a user logging in.'''
    username: str
    password: str


class Token(BaseModel):
    """Schema for the JWT token returned upon successful login."""
    access_token: str
    token_type: str = "bearer"

class QueryRequest(BaseModel):
    """Schema for the incoming RAG query."""
    text: str
