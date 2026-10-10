from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:adi281#2@127.0.0.1:5432/railmitra")

try:
    engine = create_engine(DATABASE_URL, echo=False)
    # Test connection
    with engine.connect():
        pass
except Exception as err:
    print(f"[Database Warning] PostgreSQL connection failed: {err}. Falling back to SQLite.")
    engine = create_engine("sqlite:///./railmitra.db", echo=False, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()