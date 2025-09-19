"""
Django settings for Docker deployment.
Inherits from production settings with Docker-specific overrides.
"""
import os
from .production import *

# Override paths for Docker container
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CORE_DIR = BASE_DIR

# Template configuration for Docker
TEMPLATES[0]['DIRS'] = [
    os.path.join(BASE_DIR, 'templates'),
    '/app/templates',  # Fallback path
]

# Static files configuration
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = '/static/'

# Media files configuration
MEDIA_ROOT = '/app/media'
MEDIA_URL = '/media/'

# Debug mode from environment
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Allow all hosts in Docker (nginx handles the filtering)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Logging configuration for Docker
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Security settings adjusted for Docker
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Session settings
SESSION_COOKIE_SECURE = False  # Set to True when using HTTPS
CSRF_COOKIE_SECURE = False  # Set to True when using HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Trusted origins for CSRF
CSRF_TRUSTED_ORIGINS = ['http://localhost']

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB

print(f"Docker settings loaded - DEBUG: {DEBUG}, BASE_DIR: {BASE_DIR}")
print(f"TEMPLATE_DIRS: {TEMPLATES[0]['DIRS']}")
print(f"STATIC_ROOT: {STATIC_ROOT}")