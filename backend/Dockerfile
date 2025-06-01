# Use Python 3.11 slim image as the base image
FROM python:3.11-slim-bullseye as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create and switch to a non-root user
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

# Copy project files
COPY --chown=django:django . .

# Expose port 8000
EXPOSE 8000

# Volumes for static and media
VOLUME ["/app/staticfiles", "/app/media"]

# Start command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
