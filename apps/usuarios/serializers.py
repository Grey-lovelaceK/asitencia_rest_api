# serializers.py
from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombre', 'apellido', 'rol', 'activo',
            'is_active', 'is_staff', 'date_joined', 'last_login'
        ]
        read_only_fields = ('date_joined', 'last_login')

class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
 
    class Meta:
        model = Usuario
        fields = ['email', 'password', 'nombre', 'apellido', 'rol']
   
    def validate_email(self, value):
        """Validar que el email no esté duplicado"""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email")
        return value
   
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario.objects.create_user(password=password, **validated_data) #type: ignore
        return user

class UsuarioUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ['email', 'password', 'nombre', 'apellido', 'rol', 'activo']

    def validate_email(self, value):
        """Validar que el email no esté duplicado (excluyendo el usuario actual)"""
        user_id = self.instance.id if self.instance else None
        if Usuario.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email")
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()