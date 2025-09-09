import pytest
from django.test import TestCase
from apps.usuarios.models import Usuario
from django.contrib.auth.hashers import make_password

@pytest.mark.django_db
class TestUsuarioModel:
    
    def test_create_user(self):
        usuario = Usuario.objects.create(
            email='test@example.com',
            password=make_password('password123'),
            nombre='Test',
            apellido='User',
            rol='empleado'
        )
        
        assert usuario.email == 'test@example.com'
        assert usuario.nombre == 'Test'
        assert usuario.activo == True
        assert usuario.es_administrador() == False
    
    def test_create_admin_user(self):
        admin = Usuario.objects.create(
            email='admin@example.com',
            password=make_password('admin123'),
            nombre='Admin',
            apellido='User',
            rol='administrador'
        )
        
        assert admin.es_administrador() == True