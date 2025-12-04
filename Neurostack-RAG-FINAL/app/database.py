from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Connection string: SQLite uses a file. The 'check_same_thread=False' is crucial 
#    for SQLite when used with FastAPI/multiple threads.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2. Session creation: Each request uses its own DB session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base class for SQLAlchemy ORM models.
Base = declarative_base()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()