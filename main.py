from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
# Import UserLogin
from models import UserIn, UserOut, Token, UserLogin # <--- Tambahkan UserLogin di sini
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from typing import Dict

app = FastAPI()

fake_users_db: Dict[str, dict] = {}

@app.post("/api/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserIn):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if any(u["email"] == user.email for u in fake_users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    return UserOut(username=user.username, email=user.email)

# Ubah user_in: UserIn menjadi user_in: UserLogin
@app.post("/api/auth/login", response_model=Token)
async def login(user_in: UserLogin): # <--- Perubahan di sini
    user_db = fake_users_db.get(user_in.username)
    if not user_db or not verify_password(user_in.password, user_db["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user_db["username"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)