# Diagnóstico del Error 500 en Django con Docker

## Problema Identificado
- **Síntoma**: Error 500 (Server Error) al acceder a la aplicación
- **Estado**: Los contenedores están ejecutándose (UP)
- **Comunicación**: Nginx puede comunicarse con Django (por eso ves el error 500 en lugar de 502)

## Análisis de la Causa Raíz

### 1. Problemas Identificados en la Configuración

#### A. **PROBLEMA PRINCIPAL: Configuración de DEBUG en Producción**
En tu archivo `docker-compose.yml`, Django está usando `django_pos.settings.production` pero:
- `DEBUG=False` está configurado en el `.env`
- Cuando DEBUG=False, Django NO muestra errores detallados y requiere configuración adicional

#### B. **Problema de ALLOWED_HOSTS**
Tu `.env` tiene:
```
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```
El "your-domain.com" podría estar causando problemas si Django intenta validarlo.

#### C. **Problema de STATIC_ROOT y Rutas**
- En `settings.py`: `STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')`
- En `production.py`: `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')`
- Las rutas BASE_DIR y CORE_DIR son diferentes, lo que puede causar que Django no encuentre los archivos estáticos

## Comandos de Diagnóstico Inmediato

Ejecuta estos comandos para obtener información detallada del error:

### 1. Ver los logs del contenedor web
```bash
# Ver los últimos logs con detalles del error
docker-compose logs web --tail=100

# Seguir los logs en tiempo real
docker-compose logs -f web
```

### 2. Verificar el estado de las migraciones
```bash
docker-compose exec web python manage.py showmigrations
```

### 3. Verificar la configuración de Django
```bash
# Verificar que Django puede cargar la configuración
docker-compose exec web python manage.py check --deploy

# Ver la configuración actual
docker-compose exec web python manage.py shell -c "from django.conf import settings; print('DEBUG:', settings.DEBUG); print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS); print('STATIC_ROOT:', settings.STATIC_ROOT)"
```

### 4. Probar con DEBUG=True temporalmente
```bash
# Detener los contenedores
docker-compose down

# Modificar temporalmente el .env para activar DEBUG
# Cambia DEBUG=False a DEBUG=True en el archivo .env

# Reiniciar
docker-compose up -d

# Ver si ahora muestra el error detallado
```

## Soluciones Propuestas

### Solución 1: Configuración Corregida (RECOMENDADA)

#### A. Actualizar el archivo `.env`:
```env
# Django Configuration
SECRET_KEY=8ae09f338a0e2f7e8ae2e2fc846e7c6e23b5f5894260bb9e6eb6e457550fe549fd836daeba260ad0103e475d1e1971094e50
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://pos_user:pos_password@db:5432/django_pos

# Other Settings
TIME_ZONE=America/Caracas
LANGUAGE_CODE=es
```

#### B. Modificar `docker-compose.yml`:
Cambiar el comando del servicio web para incluir mejor manejo de errores:

```yaml
web:
  build: .
  restart: always
  user: root
  environment:
    - DJANGO_SETTINGS_MODULE=django_pos.settings.production
    - DEBUG=${DEBUG:-False}
    - SECRET_KEY=${SECRET_KEY:-django-insecure-change-this-in-production}
    - DATABASE_URL=postgresql://pos_user:pos_password@db:5432/django_pos
    - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost,127.0.0.1,0.0.0.0}
    - TIME_ZONE=${TIME_ZONE:-America/Caracas}
    - LANGUAGE_CODE=${LANGUAGE_CODE:-es}
    - PYTHONUNBUFFERED=1  # Añadir esta línea para ver logs en tiempo real
  volumes:
    - ./django_pos/media:/app/media
    - static_volume:/app/staticfiles
  ports:
    - "8000:8000"
  depends_on:
    db:
      condition: service_healthy
  command: >
    sh -c "
    echo 'Starting Django setup...' &&
    chown -R app:app /app/staticfiles &&
    chown -R app:app /app/media &&
    su app -c '
    echo \"Running migrations...\" &&
    python manage.py migrate --noinput &&
    echo \"Collecting static files...\" &&
    python manage.py collectstatic --noinput &&
    echo \"Starting Gunicorn...\" &&
    gunicorn django_pos.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-level info --access-logfile - --error-logfile -
    '"
```

### Solución 2: Crear un archivo de configuración de desarrollo local

Crear `django_pos/django_pos/settings/docker.py`:

```python
from .production import *

# Override para desarrollo local con Docker
DEBUG = True  # Temporalmente para ver errores
ALLOWED_HOSTS = ['*']  # Permitir cualquier host en desarrollo

# Logging más detallado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

Y luego cambiar en `docker-compose.yml`:
```yaml
environment:
  - DJANGO_SETTINGS_MODULE=django_pos.settings.docker
```

## Pasos de Implementación

1. **Primero, obtén los logs actuales del error**:
   ```bash
   docker-compose logs web --tail=200 > error_logs.txt
   ```

2. **Activa DEBUG temporalmente** para ver el error real:
   - Edita `.env` y cambia `DEBUG=False` a `DEBUG=True`
   - Ejecuta: `docker-compose restart web`
   - Accede a la aplicación y anota el error específico

3. **Una vez identificado el error**, implementa la solución correspondiente

4. **Reconstruye y reinicia**:
   ```bash
   docker-compose down
   docker-compose build --no-cache web
   docker-compose up -d
   ```

## Problemas Comunes y Sus Soluciones

### 1. Error: "Invalid HTTP_HOST header"
**Causa**: ALLOWED_HOSTS no incluye el host correcto
**Solución**: Actualizar ALLOWED_HOSTS en .env

### 2. Error: "TemplateDoesNotExist"
**Causa**: Las rutas de templates no son correctas
**Solución**: Verificar TEMPLATE_DIR en settings

### 3. Error: "Static files not found"
**Causa**: STATIC_ROOT mal configurado o collectstatic no ejecutado
**Solución**: Verificar rutas y ejecutar collectstatic

### 4. Error: "Database connection failed"
**Causa**: La base de datos no está lista o credenciales incorrectas
**Solución**: Verificar que el healthcheck de la DB pase

## Verificación Final

Después de aplicar las correcciones:

1. **Verificar que todos los contenedores estén saludables**:
   ```bash
   docker-compose ps
   ```

2. **Verificar logs sin errores**:
   ```bash
   docker-compose logs web --tail=50
   ```

3. **Probar la aplicación**:
   - Acceder a http://localhost (aplicación principal)
   - Acceder a http://localhost/admin (panel de administración)
   - Verificar que los archivos estáticos cargan (CSS/JS)

## Siguiente Paso Recomendado

**Ejecuta este comando ahora para ver el error específico**:
```bash
docker-compose logs web --tail=100 | grep -A 10 -B 10 "ERROR\|Error\|500"
```

Esto te mostrará el error real que está causando el problema 500, y con esa información podremos aplicar la solución específica.