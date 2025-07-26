from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Muat variabel lingkungan dari .env
load_dotenv()

# Ambil komponen kredensial database dari variabel lingkungan
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "postgres-service") # Default ke nama service Kubernetes
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Pastikan semua variabel penting telah disetel
if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Database credentials (DB_USER, DB_PASSWORD, DB_NAME) must be set in environment variables.")

# Bangun DATABASE_URL dari komponen-komponen terpisah
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Periksa apakah DATABASE_URL telah disetel
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please set it in your .env file or environment.")

# Buat engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Buat objek SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk model deklaratif SQLAlchemy
Base = declarative_base()

# Dependency untuk mendapatkan sesi database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()