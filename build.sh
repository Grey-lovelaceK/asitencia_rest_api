cat > build.sh << 'EOF'
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"
EOF

# Darle permisos
git update-index --chmod=+x build.sh

# Verificar que tiene todo el contenido
cat build.sh

# Commit y push
git add build.sh
git commit -m "Fix build.sh with complete content including superuser creation"
git push