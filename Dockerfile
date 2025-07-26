FROM python:3.12-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies first
# Perhatikan path: ini adalah relatif terhadap context build (root proyek)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code
# Perhatikan path: ini adalah relatif terhadap context build (root proyek)
COPY . /app

# Expose the port your FastAPI application listens on (default is 8000)
EXPOSE 8000

# Command to run your FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# Catatan:
# jalankan docker build dari folder python-fast-api-auth
# docker build -t your_dockerhub_username/auth-app-backend:latest .
# Gantilah `your_dockerhub_username` dengan username Docker Hub Anda.
# Setelah itu, Anda bisa push ke Docker Hub:
# docker push your_dockerhub_username/auth-app-backend:latest