FROM python:3.12-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies first
# Perhatikan path: ini adalah relatif terhadap context build (root proyek)
COPY python-fast-api-auth/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code
# Perhatikan path: ini adalah relatif terhadap context build (root proyek)
COPY python-fast-api-auth/. /app

# Expose the port your FastAPI application listens on (default is 8000)
EXPOSE 8000

# Command to run your FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]