# Django POS - Sistema de Punto de Venta

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.1.5-green.svg)](https://djangoproject.com)

Sistema completo de Punto de Venta (POS) desarrollado en Django, completamente localizado para Venezuela con interfaz 100% en español.

## 🚀 Características Principales

- ✅ **Interfaz 100% en Español** - Completamente localizado para Venezuela
- ✅ **Independiente de Internet** - Todos los recursos locales (sin CDNs)
- ✅ **Base de Datos PostgreSQL** - Robusta y escalable
- ✅ **Despliegue con Docker** - Fácil implementación en cualquier máquina
- ✅ **Arquitectura Moderna** - Django 4.1.5 con mejores prácticas
- ✅ **Sistema de Usuarios** - Autenticación y roles
- ✅ **Gestión de Productos** - Inventario completo
- ✅ **Ventas y Clientes** - Sistema completo de POS
- ✅ **Reportes PDF** - Generación de recibos y reportes
- ✅ **API REST** - Para integraciones futuras

## 📋 Requisitos del Sistema

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **4GB RAM** mínimo
- **2GB Espacio en Disco** mínimo
- **Sistema Operativo**: Linux, macOS, Windows

## 🛠️ Instalación y Despliegue

### Paso 1: Clonar el Repositorio

```bash
git clone <tu-repositorio>
cd django_point_of_sale
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus configuraciones
nano .env
```

**Contenido mínimo del archivo `.env`:**
```bash
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com
```

### Paso 3: Desplegar con Docker

```bash
# Hacer ejecutables los scripts
chmod +x deploy.sh update.sh

# Ejecutar despliegue
./deploy.sh
```

### Paso 4: Acceder a la Aplicación

- **Aplicación Web**: http://localhost
- **Panel de Administración**: http://localhost/admin/
- **API**: http://localhost/api/

## 🔄 Actualizaciones

Para actualizar la aplicación con nuevos cambios:

```bash
./update.sh
```

Este script:
- ✅ Crea backup de la base de datos (opcional)
- ✅ Descarga últimos cambios de git
- ✅ Reconstruye contenedores
- ✅ Ejecuta migraciones
- ✅ Recopila archivos estáticos
- ✅ Reinicia servicios

## 📁 Estructura del Proyecto

```
django_point_of_sale/
├── django_pos/                 # Proyecto Django principal
│   ├── django_pos/            # Configuración del proyecto
│   │   ├── settings/          # Configuraciones divididas
│   │   │   ├── __init__.py
│   │   │   ├── settings.py    # Configuración desarrollo
│   │   │   └── production.py  # Configuración producción
│   │   └── wsgi.py
│   ├── authentication/        # App de autenticación
│   ├── customers/            # App de clientes
│   ├── products/             # App de productos
│   ├── sales/                # App de ventas
│   ├── pos/                  # App del POS
│   ├── suppliers/            # App de proveedores
│   ├── core/                 # App núcleo (configuraciones)
│   ├── locale/es/            # Traducciones al español
│   ├── static/               # Archivos estáticos
│   ├── media/                # Archivos multimedia
│   └── templates/            # Plantillas HTML
├── docker-compose.yml        # Configuración Docker
├── Dockerfile               # Imagen Docker
├── nginx.conf              # Configuración Nginx
├── requirements.txt        # Dependencias Python
├── .env.example           # Variables de entorno ejemplo
├── deploy.sh              # Script de despliegue
├── update.sh              # Script de actualización
└── README.md              # Esta documentación
```

## 🐳 Arquitectura Docker

### Servicios

1. **web** - Aplicación Django + Gunicorn
2. **db** - Base de datos PostgreSQL 15
3. **nginx** - Servidor web y proxy reverso

### Volúmenes

- `postgres_data` - Datos persistentes de PostgreSQL
- `./django_pos/media` - Archivos multimedia
- `./django_pos/staticfiles` - Archivos estáticos

## ⚙️ Configuración de Producción

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta Django | **OBLIGATORIO** |
| `DEBUG` | Modo debug | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL de base de datos | PostgreSQL local |
| `TIME_ZONE` | Zona horaria | `America/Caracas` |
| `LANGUAGE_CODE` | Código de idioma | `es` |

### Base de Datos

- **Motor**: PostgreSQL 15
- **Usuario**: `pos_user`
- **Base de datos**: `django_pos`
- **Contraseña**: `pos_password` (cambiar en producción)

## 🔒 Seguridad

### Configuraciones de Seguridad Implementadas

- ✅ **SECRET_KEY** segura y única
- ✅ **DEBUG=False** en producción
- ✅ **ALLOWED_HOSTS** configurados
- ✅ **HTTPS** forzado
- ✅ **Headers de seguridad** (XSS, CSRF, etc.)
- ✅ **Base de datos PostgreSQL** (más segura que SQLite)
- ✅ **Usuario no-root** en contenedores
- ✅ **Variables de entorno** para configuración sensible

### Mejores Prácticas de Seguridad

1. **Cambiar SECRET_KEY** por una clave segura y única
2. **Configurar HTTPS** en producción
3. **Cambiar credenciales** de base de datos
4. **Limitar ALLOWED_HOSTS** a dominios específicos
5. **Mantener Docker** y dependencias actualizadas
6. **Realizar backups** regulares de la base de datos

## 📊 Monitoreo y Logs

### Ver Logs de la Aplicación

```bash
# Todos los servicios
docker-compose logs -f

# Solo aplicación web
docker-compose logs -f web

# Solo base de datos
docker-compose logs -f db
```

### Health Checks

- **Aplicación**: http://localhost/health/
- **Base de datos**: Puerto 5432 (PostgreSQL)

## 🔧 Comandos Útiles

### Gestión de Contenedores

```bash
# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver estado de servicios
docker-compose ps

# Acceder al shell del contenedor web
docker-compose exec web bash

# Acceder a PostgreSQL
docker-compose exec db psql -U pos_user -d django_pos
```

### Gestión de Django

```bash
# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic

# Compilar traducciones
docker-compose exec web python manage.py compilemessages
```

### Backup y Restauración

```bash
# Backup de base de datos
docker-compose exec db pg_dump -U pos_user django_pos > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U pos_user -d django_pos < backup.sql
```

## 🌐 Despliegue en Producción

### Requisitos Adicionales

1. **Dominio**: Configurar DNS
2. **SSL Certificate**: Let's Encrypt o similar
3. **Firewall**: Configurar puertos (80, 443)
4. **Backup**: Configurar backups automáticos

### Configuración de Nginx (Producción)

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    # Proxy to Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🆘 Solución de Problemas

### Problema: Puerto 80 ocupado

```bash
# Ver qué proceso usa el puerto 80
sudo lsof -i :80

# Cambiar puerto en docker-compose.yml
ports:
  - "8080:80"  # Cambiar de 80 a 8080
```

### Problema: Error de conexión a base de datos

```bash
# Verificar estado de PostgreSQL
docker-compose logs db

# Reiniciar base de datos
docker-compose restart db
```

### Problema: Archivos estáticos no cargan

```bash
# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Reiniciar Nginx
docker-compose restart nginx
```

## 📞 Soporte

Para soporte técnico o reportar problemas:

1. **Revisar logs**: `docker-compose logs -f`
2. **Verificar configuración**: Archivo `.env`
3. **Comprobar servicios**: `docker-compose ps`
4. **Documentación**: Este README

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

**Desarrollado con ❤️ para Venezuela** 🇻🇪