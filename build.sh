#!/usr/bin/env bash
set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from apps.usuarios.models import Usuario
from django.contrib.auth.hashers import make_password

usuario, created = Usuario.objects.get_or_create(
    email='admin@empresa.com',
    defaults={
        'nombre': 'Administrador',
        'apellido': 'Principal',
        'rol': 'administrador',
        'activo': True,
        'password': make_password('Admin123!')
    }
)

if not created:
    usuario.password = make_password('Admin123!')
    usuario.save()
    print('🔄 Usuario administrador existente actualizado con nueva contraseña')
else:
    print('✅ Usuario administrador creado')
"