import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

drivername = "postgresql+psycopg2"
try:
    import psycopg2
except ImportError:
    drivername = "postgresql+psycopg"

raw_db_url = os.getenv("DATABASE_URL")
if raw_db_url:
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    parsed_url = make_url(raw_db_url)
    if "psycopg" not in parsed_url.drivername:
        parsed_url = parsed_url.set(drivername=drivername)
    DATABASE_URL = parsed_url
else:
    def _require(name):
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing {name}. Add it to backend/.env")
        return value

    DB_USER = _require("DB_USER")
    DB_PASSWORD = _require("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = _require("DB_NAME")
    sslmode = os.getenv("DB_SSLMODE")
    if not sslmode and DB_HOST not in ("127.0.0.1", "localhost"):
        sslmode = "require"

    query = {"sslmode": sslmode} if sslmode else {}
    DATABASE_URL = URL.create(
        drivername=drivername,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        query=query
    )

engine = create_engine(DATABASE_URL)

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