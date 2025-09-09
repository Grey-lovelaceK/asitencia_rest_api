from django.db import models

# Create your models here.

class Usuario(models.Model):
    ROLES = [('empleado', 'Empleado'), ('administrador', 'Administrador')] # Definición de roles
    
    
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES, default='empleado')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    # def __str__(self):
    #     return f"{self.nombre} {self.apellido}"
    
    def es_administrador(self):
        return self.rol == 'administrador'
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"