from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session # Import Session
from typing import Dict

from models import UserIn, UserOut, Token, UserLogin, User # Import model User SQLAlchemy
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from database import get_db # Import get_db dari database.py

import os

from sqlalchemy import select

app = FastAPI()

# Konfigurasi CORS (tetap sama)
cors_origins_str = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]

# Tambahkan localhost untuk pengembangan lokal jika variabel lingkungan tidak disetel
if not origins:
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

# Tambahkan middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hapus fake_users_db karena kita akan menggunakan database
# fake_users_db: Dict[str, dict] = {}

@app.post("/api/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserIn, db: Session = Depends(get_db)): # Tambahkan db: Session
    # Cek apakah username sudah terdaftar
    # db_user_by_username = db.query(User).filter(User.username == user.username).first() # deprecated for testing
    result = await db.execute(select(User).filter(User.username == user.username))
    db_user_by_username = result.scalars().first()
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Cek apakah email sudah terdaftar
    # db_user_by_email = db.query(User).filter(User.email == user.email).first()
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user_by_email = result.scalars().first()
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)

    # Buat instance model User SQLAlchemy
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

    # Tambahkan user ke sesi database dan commit
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Refresh instance untuk mendapatkan ID yang dibuat oleh DB

    return UserOut(username=db_user.username, email=db_user.email)


@app.post("/api/auth/login", response_model=Token)
async def login(user_in: UserLogin, db: Session = Depends(get_db)): # Tambahkan db: Session
    
    # db_user = db.query(User).filter(User.username == user_in.username).first()        # deprecated for testing
    result = await db.execute(select(User).filter(User.username == user_in.username))
    db_user = result.scalars().first()

    if not db_user or not verify_password(user_in.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": db_user.username} # Gunakan db_user.username
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)): # Tambahkan db: Session
    # Anda mungkin ingin mengambil detail pengguna dari database berdasarkan username di current_user
    # Saat ini, get_current_user hanya mengembalikan dict dengan username dan email placeholder.
    # Jika Anda ingin detail lengkap dari DB, Anda bisa melakukan:
    # user_from_db = db.query(User).filter(User.username == current_user["username"]).first()
    # return UserOut(username=user_from_db.username, email=user_from_db.email)
    # Untuk tujuan demo ini, kita tetap menggunakan yang dikembalikan oleh get_current_user
    return current_user


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)