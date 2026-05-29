# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN uv pip install -r requirements.txt

# Copy application code
COPY . .

# Expose application port
EXPOSE 9900

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9900"]

