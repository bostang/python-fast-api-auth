from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
# from passlib.context import CryptContext  # DEPRECATED

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from datetime import datetime, timedelta
from datetime import UTC

from models import TokenData

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Import load_dotenv
from dotenv import load_dotenv
import os

# Muat variabel lingkungan dari .env

load_dotenv()     # UNTUK PENGEMBANGAN SECARA LOKAL.

# Konfigurasi diambil dari variabel lingkungan
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256") # Beri nilai default jika tidak ada di .env
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)) # Konversi ke integer

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set. Please set it in your .env file or environment.")


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # DEPRECATED
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

ph = PasswordHasher()

# DEPRECATED : DeprecationWarning: 'crypt' is deprecated and slated for removal in Python 3.13
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)


def get_password_hash(password: str) -> str:
    # Menggunakan Argon2 untuk menghash kata sandi
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Memverifikasi kata sandi
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        # Jika kata sandi tidak cocok
        return False
    except Exception as e:
        # Penanganan error lainnya (misalnya, hash tidak valid)
        print(f"Error verifying password: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta # <--- Gunakan UTC di sini
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # <--- Gunakan UTC di sini
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = {"username": token_data.username, "email": f"{token_data.username}@example.com"}
    if user is None:
        raise credentials_exception
    return user