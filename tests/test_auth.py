import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi.testclient import TestClient
from main import app # Hanya import app dari main.py
from database import get_db, Base # Asumsi Base dan get_db diekspos dari database.py Anda

# Konfigurasi URL database pengujian dari variabel lingkungan
# Penting: Pastikan Anda memiliki database terpisah untuk pengujian (misalnya, py_auth_db_test)
# untuk menghindari penghapusan data dari database pengembangan/produksi Anda.
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{os.environ.get('DB_USER')}:"
    f"{os.environ.get('DB_PASSWORD')}@"
    f"{os.environ.get('DB_HOST')}:"
    f"{os.environ.get('DB_PORT')}/"
    f"{os.environ.get('DB_NAME')}_test" # Menggunakan nama database _test
)

# Buat engine asinkron untuk database pengujian
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Buat sessionmaker asinkron untuk database pengujian
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency override untuk pengujian:
# Fungsi ini akan menggantikan get_db yang sebenarnya di aplikasi FastAPI
# selama pengujian, memastikan bahwa semua operasi database menggunakan
# sesi dari database pengujian dan di-rollback setelah setiap tes.
async def override_get_db():
    async with TestingSessionLocal() as session:
        # Mulai transaksi untuk setiap tes
        async with session.begin():
            yield session
            # Rollback transaksi setelah tes selesai untuk membersihkan data
            # Ini memastikan setiap tes dimulai dengan database yang bersih
            await session.rollback()

# Fixture pytest asinkron untuk menyiapkan dan membersihkan database
# Scope "module" berarti ini akan dijalankan sekali sebelum semua tes dalam modul
# dan sekali setelah semua tes selesai.
@pytest.fixture(scope="module", autouse=True)
async def setup_test_db():
    # Pastikan app.dependency_overrides diatur sebelum memulai operasi DB
    app.dependency_overrides[get_db] = override_get_db

    # TIDAK PERLU lagi Base.metadata.drop_all() dan create_all() di sini,
    # karena Alembic akan menangani pembuatan skema di workflow YAML.
    # Kita hanya perlu memastikan bahwa database sudah siap untuk menerima koneksi.

    yield
    # Setelah semua tes selesai, bersihkan dependency override
    app.dependency_overrides.clear()
    # Opsional: Jika Anda ingin memastikan database pengujian benar-benar bersih
    # setelah semua tes (misalnya untuk run lokal), Anda bisa tambahkan drop_all di sini.
    # Namun, untuk CI, biasanya cukup dengan memulai dengan database yang di-upgrade Alembic
    # pada setiap run job yang baru.
    # async with test_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


# Fixture pytest untuk menyiapkan TestClient
# Fixture ini sekarang sinkron karena TestClient adalah sinkron.
# Ini akan dijalankan sebelum setiap fungsi tes.
@pytest.fixture(name="client", scope="function")
def client_fixture(): # setup_test_db diatur sebagai autouse=True, jadi tidak perlu di-pass di sini
    # Yield TestClient untuk digunakan dalam tes
    with TestClient(app=app) as client_sync:
        yield client_sync


# --- Tes untuk Endpoint Register ---

@pytest.mark.asyncio
async def test_register_user_success(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json() == {"username": "testuser", "email": "test@example.com"}

@pytest.mark.asyncio
async def test_register_user_already_exists(client: TestClient):
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
async def test_register_email_already_exists(client: TestClient):
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
async def test_login_user_success(client: TestClient):
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
async def test_login_user_invalid_password(client: TestClient):
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
async def test_login_user_not_registered(client: TestClient):
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistentuser", "password": "anypassword"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

# --- Tes untuk Endpoint yang Dilindungi (misal: /api/users/me) ---

@pytest.mark.asyncio
async def test_access_protected_endpoint_success(client: TestClient):
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
    # Periksa kunci dan nilai tertentu karena respons mungkin mengandung lebih dari username dan email
    response_data = response.json()
    assert "username" in response_data
    assert "email" in response_data
    assert response_data["username"] == "protecteduser"
    assert response_data["email"] == "protected@example.com"

@pytest.mark.asyncio
async def test_access_protected_endpoint_no_token(client: TestClient):
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

@pytest.mark.asyncio
async def test_access_protected_endpoint_invalid_token(client: TestClient):
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
