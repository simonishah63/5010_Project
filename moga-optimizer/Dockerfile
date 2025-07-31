# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the microservice
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]