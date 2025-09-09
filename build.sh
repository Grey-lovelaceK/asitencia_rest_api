#!/usr/bin/env bash
set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from apps.usuarios.models import Usuario

usuario, created = Usuario.objects.get_or_create(
    email='greyc9404@gmail.com'
)

if created:
    Usuario.objects.create_superuser(
        email='greyc9404@gmail.com',
        password='admin123',
        nombre='Administrador',
        apellido='Principal'
    )
    print('✅ Usuario administrador creado')
else:
    usuario.set_password('admin123')
    usuario.save()
    print('🔄 Usuario administrador existente actualizado con nueva contraseña')
"