import pytest
from pytest_asyncio import fixture as pytest_asyncio_fixture

from fastapi.testclient import TestClient # <--- Sudah benar

from main import app, fake_users_db
from auth import get_password_hash

@pytest_asyncio_fixture(name="client")
async def client_fixture():
    fake_users_db.clear()
    with TestClient(app=app) as client_sync:
        yield client_sync

# --- Tes untuk Endpoint Register ---

@pytest.mark.asyncio
async def test_register_user_success(client: TestClient): # <-- Ubah ini
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json() == {"username": "testuser", "email": "test@example.com"}
    assert "testuser" in fake_users_db
    assert fake_users_db["testuser"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_register_user_already_exists(client: TestClient): # <-- Ubah ini
    # Register user pertama kali
    client.post(
        "/api/auth/register",
        json={"username": "existinguser", "email": "existing@example.com", "password": "password123"}
    )

    # Coba register user dengan username yang sama
    response = client.post(
        "/api/auth/register",
        json={"username": "existinguser", "email": "another@example.com", "password": "newpassword"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

@pytest.mark.asyncio
async def test_register_email_already_exists(client: TestClient): # <-- Ubah ini
    # Register user pertama kali
    client.post(
        "/api/auth/register",
        json={"username": "user1", "email": "common@example.com", "password": "password123"}
    )

    # Coba register user lain dengan email yang sama
    response = client.post(
        "/api/auth/register",
        json={"username": "user2", "email": "common@example.com", "password": "anotherpassword"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

# --- Tes untuk Endpoint Login ---

@pytest.mark.asyncio
async def test_login_user_success(client: TestClient): # <-- Ubah ini
    # Register user terlebih dahulu
    client.post(
        "/api/auth/register",
        json={"username": "loginuser", "email": "login@example.com", "password": "password123"}
    )

    response = client.post(
        "/api/auth/login",
        json={"username": "loginuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user_invalid_password(client: TestClient): # <-- Ubah ini
    # Register user terlebih dahulu
    client.post(
        "/api/auth/register",
        json={"username": "invalidpwuser", "email": "invalidpw@example.com", "password": "correctpassword"}
    )

    response = client.post(
        "/api/auth/login",
        json={"username": "invalidpwuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

@pytest.mark.asyncio
async def test_login_user_not_registered(client: TestClient): # <-- Ubah ini
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistentuser", "password": "anypassword"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

# --- Tes untuk Endpoint yang Dilindungi (misal: /api/users/me) ---

@pytest.mark.asyncio
async def test_access_protected_endpoint_success(client: TestClient): # <-- Ubah ini
    # Register user dan login untuk mendapatkan token
    client.post(
        "/api/auth/register",
        json={"username": "protecteduser", "email": "protected@example.com", "password": "password123"}
    )
    login_response = client.post(
        "/api/auth/login",
        json={"username": "protecteduser", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Akses endpoint yang dilindungi dengan token
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    # assert response.json() == {"username": "protecteduser", "email": "protected@example.com"}
    assert response.json() == {"username": "protecteduser", "email": "protecteduser@example.com"}

@pytest.mark.asyncio
async def test_access_protected_endpoint_no_token(client: TestClient): # <-- Ubah ini
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

@pytest.mark.asyncio
async def test_access_protected_endpoint_invalid_token(client: TestClient): # <-- Ubah ini
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}