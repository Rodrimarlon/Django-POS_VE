# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=django_pos.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    gettext \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy entire project directory with correct structure
COPY django_pos/ /app/

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

COPY docker-entrypoint-web.sh /docker-entrypoint-web.sh
RUN chmod +x /docker-entrypoint-web.sh

# Create non-root user and set permissions
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app /docker-entrypoint-web.sh

# Switch to non-root user
USER app

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint-web.sh"]

# Expose port
EXPOSE 8000

# Run the application with gunicorn optimized for limited hardware
CMD ["gunicorn", "django_pos.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "1", "--worker-class", "gthread", "--max-requests", "500", "--max-requests-jitter", "50", "--timeout", "120", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-"]