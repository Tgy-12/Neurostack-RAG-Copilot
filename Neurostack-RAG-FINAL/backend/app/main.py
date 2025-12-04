from fastapi import FastAPI, Depends, HTTPException, status, Request,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import os
import bcrypt
from jose import jwt
from dotenv import load_dotenv

# Re-enable the RAG pipeline when the auth is stable
from .rag_pipeline import get_rag_answer
from .models import User, UserCreate, UserLogin, Token, QueryRequest, UserModel
from .database import engine, Base, get_db
from sqlalchemy.orm import Session
from . import crud

# NOTE: CORSMiddleware is not being used, relying on the manual handler below

load_dotenv()
Base.metadata.create_all(bind=engine) # creating of database table at startup

# --- SECURITY CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-that-should-be-long")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Using absolute path for tokenUrl:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# --- APP INITIALIZATION ---
app = FastAPI(
    title="SaaS Support Copilot API",
    description="Hybrid RAG with Answer Validation Layer for Hackathon.",
    root_path = "/"
)
# Define a clean router to fix pathing issues
api_router = APIRouter()

# --- ORIGINS LIST (USED BY MANUAL HANDLER) ---
origins = [
    "http://localhost:3000",
    "https://neurostack-rag-copilot-1n7ii8cp3-tgy-12s-projects.vercel.app",
    "https://neurostackfro.netlify.app",
    "https://thomi-12-neurostack-rag-copilot.hf.space"
]

# --- HELPER FUNCTIONS ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    # bcrypt requires bytes in use
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = crud.get_user_by_username(db, username=username)

        if user is None:
            raise credentials_exception
        return User.model_validate(user)
    except jwt.JWTError:
        raise credentials_exception

# --- AUTHENTICATION ROUTES (Using standard absolute paths /api/*) ---
@api_router.options("/api/register")
async def options_signup():
    """Handles OPTIONS preflight check specifically for the signup route."""
    return {"message": "Options allowed"}

@api_router.post("/api/register", response_model=Token)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # Define db_user before checking it
    db_user = crud.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    db_email = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_in.password)
    user = crud.create_user(db=db, user=user_in, hashed_password=hashed_password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # The return type MUST be a dictionary matching the Token response_model
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/api/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- RAG Endpoint (Commented out for startup stability) ---
@api_router.post("/api/copilot", response_model=Dict[str, Any])
async def get_copilot_response(
    query: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    RAG Endpoint: uses in Retrieving context and generates a validated answer.
    Requires a valid JWT Access Token.
    """
    try:
        response = await get_rag_answer(query.text)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG Pipeline error: {str(e)}"
        )

# --- HEALTH CHECK ---
@api_router.get("/health")
async def health_check():
    """Simple health check on a specific path to confirm API is running."""
    return {"status": "ok", "service": "SaaS Support Copilot API"}

# --- CORS PREFLIGHT HANDLER ---
@api_router.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str = "") -> Response:
    """Manually handles all OPTIONS preflight requests for any path."""
    response = Response(status_code=204)
    origin = request.headers.get("origin")
    if origin and origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    else:
        response.headers["Access-Control-Allow-Origin"] = origins[0]
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response
# Mount the API router to the application
app.include_router(api_router)