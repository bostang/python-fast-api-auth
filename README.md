# python-fast-api-auth

## Cara Menjalankan

> untuk Linux / UNIX (MAC OS)

```bash
# LANGKAH 0 : Buat virtual environment
python -m venv venv
source venv/bin/activate

# LANGKAH 1 : Install dependency
pip install -r requirements.txt

# LANGKAH 2 : Jalankan aplikasi
uvicorn main:app --reload

# KETIKA SELESAI, non-aktifkan lagi virtual environment dengan:
deactivate

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
