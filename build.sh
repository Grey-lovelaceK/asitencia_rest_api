#!/usr/bin/env bash
set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from apps.usuarios.models import Usuario
from django.contrib.auth.hashers import make_password

# Crear usuario administrador para la API
if not Usuario.objects.filter(email='admin@empresa.com').exists():
    Usuario.objects.create(
        email='admin@empresa.com',
        password=make_password('Admin123!'),
        nombre='Administrador',
        apellido='Principal',
        rol='administrador',
        activo=True
    )
    print('✅ Usuario administrador creado para API:')
    print('   Email: admin@empresa.com')
    print('   Password: Admin123!')
    print('   Rol: administrador')
else:
    print('⚠️  Usuario administrador ya existe')
"
