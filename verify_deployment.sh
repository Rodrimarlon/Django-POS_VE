#!/bin/bash

# Crear archivo temporal para capturar salida
OUTPUT_FILE=$(mktemp)

# Función para imprimir con colores y capturar salida
print_status() {
    echo -e "\n\e[1;34m$1\e[0m" | tee -a "$OUTPUT_FILE"
}

print_success() {
    echo -e "\e[1;32m✅ $1\e[0m" | tee -a "$OUTPUT_FILE"
}

print_error() {
    echo -e "\e[1;31m❌ $1\e[0m" | tee -a "$OUTPUT_FILE"
}

print_warning() {
    echo -e "\e[1;33m⚠️  $1\e[0m" | tee -a "$OUTPUT_FILE"
}

# Función para imprimir normal (sin colores en archivo)
print_normal() {
    echo "$1" | tee -a "$OUTPUT_FILE"
}

echo "=== VERIFICACIÓN COMPLETA DEL SISTEMA POS ===" | tee "$OUTPUT_FILE"
echo "Fecha: $(date)" | tee -a "$OUTPUT_FILE"
echo "============================================" | tee -a "$OUTPUT_FILE"

# 1. Verificar estado de contenedores
print_status "1. VERIFICANDO ESTADO DE CONTENEDORES"
print_normal "Contenedores corriendo:"
docker compose ps | tee -a "$OUTPUT_FILE"

# Verificar que todos los servicios estén UP
if docker compose ps | grep -q "Up"; then
    print_success "Contenedores están ejecutándose"
else
    print_error "Algunos contenedores no están ejecutándose"
fi

# 2. Verificar configuración de Django
print_status "2. VERIFICANDO CONFIGURACIÓN DJANGO"

echo "Ejecutando 'python manage.py check'..."
if docker compose exec -T web python manage.py check --deploy > /dev/null 2>&1; then
    print_success "Configuración de Django es válida"
else
    print_error "Errores en configuración de Django"
    docker compose exec -T web python manage.py check --deploy
fi

# 3. Verificar base de datos
print_status "3. VERIFICANDO CONEXIÓN A BASE DE DATOS"

if docker compose exec -T db pg_isready -U pos_user -d django_pos > /dev/null 2>&1; then
    print_success "PostgreSQL está respondiendo"

    # Verificar que las tablas existen
    TABLES_COUNT=$(docker compose exec -T db psql -U pos_user -d django_pos -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" -t)
    if [ "$TABLES_COUNT" -gt 0 ]; then
        print_success "Base de datos tiene $TABLES_COUNT tablas"
    else
        print_warning "Base de datos parece vacía (sin tablas)"
    fi
else
    print_error "No se puede conectar a PostgreSQL"
fi

# 4. Verificar conectividad web
print_status "4. VERIFICANDO CONECTIVIDAD WEB"

# Probar Nginx
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    print_success "Nginx responde correctamente (HTTP $HTTP_CODE)"
else
    print_error "Nginx no responde (HTTP $HTTP_CODE)"
fi

# Probar Django admin
ADMIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/ 2>/dev/null || echo "000")
if [ "$ADMIN_CODE" = "200" ] || [ "$ADMIN_CODE" = "302" ]; then
    print_success "Django admin responde (HTTP $ADMIN_CODE)"
else
    print_warning "Django admin no responde correctamente (HTTP $ADMIN_CODE)"
fi

# 5. Verificar archivos estáticos
print_status "5. VERIFICANDO ARCHIVOS ESTÁTICOS"

STATIC_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/admin/css/base.css 2>/dev/null || echo "000")
if [ "$STATIC_CODE" = "200" ]; then
    print_success "Archivos estáticos se sirven correctamente"
else
    print_error "Archivos estáticos no se sirven (HTTP $STATIC_CODE)"
fi

# 6. Verificar workers de Gunicorn
print_status "6. VERIFICANDO CONFIGURACIÓN GUNICORN"

WORKERS=$(docker compose exec -T web ps aux | grep gunicorn | grep -v grep | wc -l)
if [ "$WORKERS" -eq 1 ]; then
    print_success "Gunicorn ejecutándose con 1 worker (optimizado)"
else
    print_warning "Gunicorn tiene $WORKERS workers (esperado: 1)"
fi

# 7. Verificar configuración PostgreSQL
print_status "7. VERIFICANDO CONFIGURACIÓN POSTGRESQL"

SHARED_BUFFERS=$(docker compose exec -T db psql -U pos_user -d django_pos -c "SHOW shared_buffers;" -t 2>/dev/null | tr -d ' ')
if [ "$SHARED_BUFFERS" = "128MB" ]; then
    print_success "PostgreSQL shared_buffers optimizado: $SHARED_BUFFERS"
else
    print_warning "PostgreSQL shared_buffers: $SHARED_BUFFERS (esperado: 128MB)"
fi

WORK_MEM=$(docker compose exec -T db psql -U pos_user -d django_pos -c "SHOW work_mem;" -t 2>/dev/null | tr -d ' ')
if [ "$WORK_MEM" = "4MB" ]; then
    print_success "PostgreSQL work_mem optimizado: $WORK_MEM"
else
    print_warning "PostgreSQL work_mem: $WORK_MEM (esperado: 4MB)"
fi

# 8. Verificar logs recientes
print_status "8. VERIFICANDO LOGS RECIENTES"

print_normal "Últimas 10 líneas de logs de web:"
docker compose logs --tail=10 web 2>/dev/null | head -10 | tee -a "$OUTPUT_FILE"

print_normal ""
print_normal "Últimas 10 líneas de logs de db:"
docker compose logs --tail=10 db 2>/dev/null | head -10 | tee -a "$OUTPUT_FILE"

# 9. Verificar uso de recursos
print_status "9. VERIFICANDO USO DE RECURSOS"

print_normal "Uso de memoria de contenedores:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | tee -a "$OUTPUT_FILE" || print_warning "No se puede obtener estadísticas de Docker"

# 10. Resumen final
print_status "10. RESUMEN FINAL"

print_normal "============================================"
print_normal "Verificación completada: $(date)"
print_normal ""

# Contar errores y warnings del archivo de salida
ERRORS=$(grep "❌" "$OUTPUT_FILE" | wc -l | tr -d ' ' || echo "0")
WARNINGS=$(grep "⚠️" "$OUTPUT_FILE" | wc -l | tr -d ' ' || echo "0")

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    print_success "🎉 TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE"
    print_success "El sistema está listo para producción"
elif [ "$ERRORS" -eq 0 ]; then
    print_warning "Sistema funcional pero con algunas advertencias"
else
    print_error "Se encontraron errores que requieren atención"
fi

print_normal ""
print_status "Próximos pasos recomendados:"
print_normal "1. Acceder a http://localhost para probar la interfaz"
print_normal "2. Crear usuario admin si no existe"
print_normal "3. Probar funcionalidades básicas (productos, ventas)"
print_normal "4. Monitorear logs durante uso normal"

print_normal "============================================"

# Limpiar archivo temporal
rm -f "$OUTPUT_FILE"