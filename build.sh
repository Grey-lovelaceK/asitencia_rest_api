cat > build.sh << 'EOF'
#!/usr/bin/env bash
set -o errexit

# Usar Poetry en lugar de pip
poetry install --only=main

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

git add build.sh
git commit -m "Use poetry install instead of pip"
git push