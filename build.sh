#!/usr/bin/env bash
set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from apps.usuarios.models import Usuario

# Crear usuario administrador usando el manager correcto
if not Usuario.objects.filter(email='admin@empresa.com').exists():
    Usuario.objects.create_superuser(
        email='admin@empresa.com',
        password='Admin123!',
        nombre='Administrador',
        apellido='Principal'
    )
    print('✅ Usuario administrador creado para API')
else:
    print('⚠️ Usuario administrador ya existe')
"
