# Use an official Python slim runtime
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory in container
WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend source directories
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expose default port (optional metadata)
EXPOSE 8080

# Run uvicorn on container startup, pulling port from Cloud Run PORT env var
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
