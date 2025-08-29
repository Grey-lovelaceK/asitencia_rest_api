from rest_framework import serializers
from .models import RegistroAsistencia
from apps.usuarios.serializers import UsuarioSerializer

class RegistroAsistenciaSerializer(serializers.ModelSerializer):
    usuario_info = UsuarioSerializer(source='usuario', read_only=True)
    fecha = serializers.SerializerMethodField()
    hora = serializers.SerializerMethodField()

    def get_fecha(self, obj):
        return obj.fecha_hora.strftime('%Y-%m-%d') if obj.fecha_hora else None

    def get_hora(self, obj):
        return obj.fecha_hora.strftime('%H:%M:%S') if obj.fecha_hora else None

    class Meta:
        model = RegistroAsistencia
        fields = '__all__'