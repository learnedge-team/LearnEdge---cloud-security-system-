# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create data and logs directories
RUN mkdir -p /app/data /app/logs

# Set working directory to backend
WORKDIR /app/backend

# Expose port (Render injects PORT at runtime)
EXPOSE ${PORT}

# Run with gunicorn + eventlet for production SocketIO support
# -w 1: single worker required for SocketIO in-memory state
# Render overrides PORT via environment variable
CMD gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:${PORT} app:app