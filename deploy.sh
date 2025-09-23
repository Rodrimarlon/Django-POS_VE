#!/bin/bash

# Django POS Deployment Script
# This script helps deploy the Django POS application using Docker

set -e

echo "🚀 Starting Django POS Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ docker compose is not available. Please install Docker Compose V2 first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   Especially change the SECRET_KEY for security!"
    read -p "Press Enter after editing .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p django_pos/media
mkdir -p django_pos/staticfiles

# Build and start services
echo "🐳 Building and starting Docker services..."
docker compose down --remove-orphans
docker compose build --no-cache
docker compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
docker compose exec web python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker compose exec web python manage.py collectstatic --noinput

# Create superuser (optional)
echo "👤 Do you want to create a superuser? (y/n)"
read -r create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    docker compose exec web python manage.py createsuperuser
fi

# Compile translations
echo "🌐 Compiling translations..."
docker compose exec web python manage.py compilemessages

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your application is now running at:"
echo "   - Web App: http://localhost"
echo "   - Admin: http://localhost/admin/"
echo ""
echo "📊 To check logs: docker compose logs -f"
echo "🛑 To stop: docker compose down"
echo "🔄 To restart: docker compose restart"