#!/bin/bash

# Script de verificación de despliegue Django con Docker
# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "🔍 Verificación de Despliegue Django"
echo "======================================"
echo ""

# Función para verificar servicios
check_service() {
    local service=$1
    local port=$2
    echo -n "Verificando $service en puerto $port... "
    
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FALLO${NC}"
        return 1
    fi
}

# 1. Verificar que los contenedores estén corriendo
echo "1. Estado de los contenedores:"
echo "------------------------------"
docker-compose ps
echo ""

# 2. Verificar conectividad de servicios
echo "2. Conectividad de servicios:"
echo "------------------------------"
check_service "PostgreSQL" 5432
check_service "Django/Gunicorn" 8000
check_service "Nginx" 80
echo ""

# 3. Verificar migraciones
echo "3. Estado de las migraciones:"
echo "------------------------------"
docker-compose exec -T web python manage.py showmigrations --plan | head -20
echo ""

# 4. Verificar archivos estáticos
echo "4. Archivos estáticos:"
echo "------------------------------"
echo -n "Verificando directorio de archivos estáticos... "
if docker-compose exec -T web ls /app/staticfiles/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Existe${NC}"
    echo "Cantidad de archivos estáticos:"
    docker-compose exec -T web find /app/staticfiles -type f | wc -l
else
    echo -e "${RED}✗ No existe${NC}"
fi
echo ""

# 5. Verificar templates
echo "5. Templates:"
echo "------------------------------"
echo -n "Verificando directorio de templates... "
if docker-compose exec -T web ls /app/templates/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Existe${NC}"
    echo "Templates disponibles:"
    docker-compose exec -T web find /app/templates -name "*.html" -type f | head -10
else
    echo -e "${RED}✗ No existe${NC}"
fi
echo ""

# 6. Probar endpoints
echo "6. Prueba de endpoints:"
echo "------------------------------"
endpoints=(
    "http://localhost/"
    "http://localhost/admin/"
    "http://localhost/static/admin/css/base.css"
    "http://localhost/health/"
)

for endpoint in "${endpoints[@]}"; do
    echo -n "Probando $endpoint... "
    response=$(curl -s -o /dev/null -w "%{http_code}" $endpoint)
    
    if [[ $response == "200" ]] || [[ $response == "302" ]] || [[ $response == "301" ]]; then
        echo -e "${GREEN}✓ HTTP $response${NC}"
    elif [[ $response == "404" ]]; then
        echo -e "${YELLOW}⚠ HTTP 404 (No encontrado)${NC}"
    else
        echo -e "${RED}✗ HTTP $response${NC}"
    fi
done
echo ""

# 7. Verificar logs de errores recientes
echo "7. Errores recientes (últimos 10):"
echo "------------------------------"
docker-compose logs web --tail=50 2>&1 | grep -i "error\|exception\|traceback" | tail -10 || echo "No se encontraron errores recientes"
echo ""

# 8. Información de configuración
echo "8. Configuración actual:"
echo "------------------------------"
docker-compose exec -T web python -c "
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
print(f'DATABASE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')"
echo ""

# 9. Uso de recursos
echo "9. Uso de recursos:"
echo "------------------------------"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
echo ""

# Resumen final
echo "======================================"
echo "📊 RESUMEN"
echo "======================================"

if check_service "Nginx" 80 > /dev/null 2>&1 && \
   docker-compose exec -T web ls /app/templates/ > /dev/null 2>&1 && \
   docker-compose exec -T web ls /app/staticfiles/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ El despliegue parece estar funcionando correctamente${NC}"
    echo ""
    echo "🌐 Puedes acceder a la aplicación en:"
    echo "   - Aplicación: http://localhost/"
    echo "   - Admin: http://localhost/admin/"
else
    echo -e "${RED}❌ Se detectaron problemas en el despliegue${NC}"
    echo ""
    echo "Sugerencias:"
    echo "1. Revisa los logs: docker-compose logs -f"
    echo "2. Reinicia los servicios: docker-compose restart"
    echo "3. Reconstruye si es necesario: docker-compose build --no-cache"
fi