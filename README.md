# python-fast-api-auth

## Cara Menjalankan

> untuk Linux / UNIX (MAC OS)

```bash
# LANGKAH 0 : Buat virtual environment
python -m venv venv         # <-- KALAU SUDAH ADA FOLDER venv, tidak perlu lakukan baris ini
source venv/bin/activate    # aktifkan virtual environment

# LANGKAH 1 : Install dependency
pip install -r requirements.txt

# LANGKAH 2 : Jalankan aplikasi
uvicorn main:app --reload

# KETIKA SELESAI, non-aktifkan lagi virtual environment dengan:
deactivate

```

> **catatan** : apabila `python` tidak ditemukan, kemungkinan yang terinstall adalah `python3` sehingga gunakan `python3` dan juga `pip3`. Pastikan juga `python3-venv` terinstall dengan `sudo apt install python3.12-venv`.

## PostgreSQL

```bash
# Inisialisasi Alembic
alembic init alembic

# ubah alembic/env.py

# buat database
psql -U postgres

# di dalam konsol psql :
CREATE DATABASE py_auth_db;
\q  # keluar dari konsol psql


# migrasi database pertama (akan membua tabel : alembic_version di db kita)
alembic revision --autogenerate -m "Create users table"

# menerapkan migrasi dan membuat tabel users di database
alembic upgrade head

```

## Cara Pengujian

- register

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register" \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

- login

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "password": "password123"}'
```

- akses endpoint yang dilindungi

```bash
curl -X GET "http://127.0.0.1:8000/api/users/me" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Pytest

Untuk melakukan testing menggunakan pytest (script telah disiapkan di `/tests/test_auth.py`), lakukan:

```bash
PYTHONPATH=. pytest -v tests/
```

## API Documentation

FastAPI automatically generates interactive API documentation for you, thanks to its underlying libraries like Starlette and Pydantic, and the integration of Swagger UI (OpenAPI) and ReDoc. Akses dapat dilakukan pada : **`http://127.0.0.1:8000/docs/`**

## Catatan tentang `.env` dan _secrets_

Ketika pengujian di lokal, buat `.env` di _root_ project directory dengan isi :

```conf
JWT_SECRET_KEY="your_super_secret_key_from_env"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
SONAR_TOKEN="xxx"       # gunakan untuk SONAR CLOUD SCANNING. APABILA TIDAK BUTUH, HAPUS SAJA.
```

pastikan `.env` ada pada `.gitignore`. Ketika melakukan github workflow, simpan pada _serets_ dan panggil pada `.yml` workflow:

```yaml
    env:
        # Masukkan secrets sebagai environment variables
        SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }} # Nama disesuaikan
        ALGORITHM: ${{ secrets.JWT_ALGORITHM }} # Nama disesuaikan
        ACCESS_TOKEN_EXPIRE_MINUTES: ${{ secrets.JWT_ACCESS_TOKEN_EXPIRE_MINUTES }} # Nama disesuaikan
      run: |
```

![cara-membuat-repository-secrets](./img/cara-membuat-repository-secrets.png)

tampilan repo secrests yang sudah dibuat:

![tampilan-repository-secrets-yang-sudah-dibuat](./img/tampilan-repository-secrets-yang-sudah-dibuat.png)
