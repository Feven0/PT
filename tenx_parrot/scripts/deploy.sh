#!/bin/bash

# Exit on error
set -e

# Build Docker image
docker build -t ipersona-backend .

# Run with Docker Compose
docker-compose up -d

echo "Deployment complete! The application is running at http://localhost:9900"
echo "Check logs with: docker-compose logs -f" 