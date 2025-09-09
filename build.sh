#!/usr/bin/env bash
set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from apps.usuarios.models import Usuario

email = 'greyc9404@gmail.com'
password = 'admin123'

usuario, created = Usuario.objects.get_or_create(email=email)

if created:
    # Si no existía, crear superusuario
    Usuario.objects.filter(email=email).update(
        nombre='Administrador',
        apellido='Principal',
        rol='administrador',
        is_staff=True,
        is_superuser=True
    )
    usuario.set_password(password)
    usuario.save()
    print('✅ Usuario administrador creado')
else:
    # Si existía, actualizar contraseña
    usuario.set_password(password)
    usuario.is_staff = True
    usuario.is_superuser = True
    usuario.save()
    print('🔄 Usuario administrador existente actualizado con nueva contraseña')
"
