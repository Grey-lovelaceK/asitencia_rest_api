#!/usr/bin/env bash
set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
ffrom apps.usuarios.models import Usuario

email = 'greyc9404@gmail.com'
password = 'admin123'

usuario, created = Usuario.objects.get_or_create(email=email)

usuario.nombre = 'Administrador'
usuario.apellido = 'Principal'
usuario.rol = 'administrador'
usuario.is_staff = True
usuario.is_superuser = True
usuario.set_password(password)
usuario.save()

if created:
    print('✅ Usuario administrador creado')
else:
    print('🔄 Usuario administrador existente actualizado')
"
