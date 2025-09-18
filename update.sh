#!/bin/bash

# Django POS Update Script
# This script helps update the Django POS application

set -e

echo "🔄 Starting Django POS Update..."

# Check if Docker services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Docker services are not running. Please run ./deploy.sh first."
    exit 1
fi

# Backup database (optional)
echo "💾 Do you want to backup the database before updating? (y/n)"
read -r backup_db
if [[ $backup_db =~ ^[Yy]$ ]]; then
    echo "📦 Creating database backup..."
    docker-compose exec db pg_dump -U pos_user django_pos > backup_$(date +%Y%m%d_%H%M%S).sql
    echo "✅ Database backup created"
fi

# Pull latest changes (if using git)
if [ -d .git ]; then
    echo "📥 Pulling latest changes from git..."
    git pull origin main
fi

# Rebuild and restart services
echo "🐳 Rebuilding Docker services..."
docker-compose build --no-cache web

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose exec web python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

# Compile translations
echo "🌐 Compiling translations..."
docker-compose exec web python manage.py compilemessages

# Restart services
echo "🔄 Restarting services..."
docker-compose restart

echo "✅ Update completed successfully!"
echo ""
echo "🌐 Your application is updated and running at:"
echo "   - Web App: http://localhost"
echo ""
echo "📊 To check logs: docker-compose logs -f"