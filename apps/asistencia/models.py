from django.db import models
from apps.usuarios.models import Usuario

class RegistroAsistencia(models.Model):
    TIPOS = [('entrada', 'Entrada'), ('salida', 'Salida')]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='registros') #related_name para acceder a los registros desde el usuario
    tipo_registro = models.CharField(max_length=20, choices=TIPOS)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['usuario', 'fecha_hora']),
            models.Index(fields=['tipo_registro']),
        ]
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.tipo_registro} - {self.fecha_hora}"
    
    def es_entrada(self):
        return self.tipo_registro == 'entrada'
    
    def es_salida(self):
        return self.tipo_registro == 'salida'