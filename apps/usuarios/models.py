from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = [('empleado', 'Empleado'), ('administrador', 'Administrador')]

    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES, default='empleado')
    activo = models.BooleanField(default=True)

    # Campos requeridos por Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # 🔹 Evitar conflictos con auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuarios_usuario_set',  # <--- cambió aquí
        blank=True,
        help_text='Grupos a los que pertenece este usuario',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios_usuario_permissions_set',  # <--- y aquí
        blank=True,
        help_text='Permisos específicos para este usuario',
        verbose_name='user permissions'
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def es_administrador(self):
        return self.rol == 'administrador'

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"
