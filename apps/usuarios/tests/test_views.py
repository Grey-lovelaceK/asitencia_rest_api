import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.usuarios.models import Usuario
from django.contrib.auth.hashers import make_password


@pytest.mark.django_db
class TestUsuarioViewSet:
    
    def setup_method(self):
        self.client = APIClient()
        self.usuarios_url = reverse('usuario-list')
        

        self.admin = Usuario.objects.create(
            email='admin@empresa.com',
            password=make_password('admin123'),
            nombre='Admin',
            apellido='User',
            rol='administrador',
            activo=True
        )
        
        self.empleado = Usuario.objects.create(
            email='empleado@empresa.com',
            password=make_password('empleado123'),
            nombre='Empleado',
            apellido='User',
            rol='empleado',
            activo=True
        )
    
    def test_create_user_as_admin(self):

        login_data = {'email': 'admin@empresa.com', 'password': 'admin123'}
        login_response = self.client.post(reverse('login'), login_data, format='json')
        
        session_id = login_response.data.get('session_id') # type: ignore
        self.client.cookies['sessionid'] = session_id
        

        new_user_data = {
            'email': 'nuevo@empresa.com',
            'password': 'nuevo123',
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'rol': 'empleado'
        }
        
        response = self.client.post(self.usuarios_url, new_user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED #type: ignore
        assert Usuario.objects.filter(email='nuevo@empresa.com').exists()
    
    def test_create_user_as_employee_should_fail(self):
        login_data = {'email': 'empleado@empresa.com', 'password': 'empleado123'}
        login_response = self.client.post(reverse('login'), login_data, format='json')
        
        session_id = login_response.data.get('session_id') #type: ignore
        self.client.cookies['sessionid'] = session_id
        

        new_user_data = {
            'email': 'nuevo2@empresa.com',
            'password': 'nuevo123',
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'rol': 'empleado'
        }
        
        response = self.client.post(self.usuarios_url, new_user_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN #type: ignore