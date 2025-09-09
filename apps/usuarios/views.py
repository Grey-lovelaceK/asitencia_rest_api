from rest_framework import viewsets, status
from django.contrib.auth import login as django_login
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login, logout
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer, UsuarioUpdateSerializer, LoginSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.filter(activo=True)

    def get_serializer_class(self): #type: ignore
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer

    # 🔹 Autenticación manual con session
    def get_authenticated_user(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return None
        try:
            return Usuario.objects.get(id=user_id, activo=True)
        except Usuario.DoesNotExist:
            return None

    def check_admin_permission(self, request):
        usuario = self.get_authenticated_user(request)
        return usuario and usuario.rol == 'administrador'

    def list(self, request, *args, **kwargs):
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden ver la lista de usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden crear usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden actualizar usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden eliminar usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        usuario_obj = self.get_object()
        usuario_obj.activo = False
        usuario_obj.save()
        return Response({'success': 'Usuario desactivado correctamente'})

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email'] #type: ignore
    password = serializer.validated_data['password'] #type: ignore

    try:
        usuario = Usuario.objects.get(email=email, activo=True)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if not check_password(password, usuario.password):
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    # ⚡ Guardamos el id del usuario manualmente en la sesión
    request.session['user_id'] = usuario.id # type: ignore
    request.session.save()  # importante para crear session_key

    return Response({
        'success': True,
        'usuario': UsuarioSerializer(usuario).data,
        'session_id': request.session.session_key
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    request.session.flush()
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([AllowAny])
def check_session_view(request):
    user_id = request.session.get('user_id')
    if user_id:
        return Response({'logged_in': True})
    return Response({'logged_in': False}, status=status.HTTP_401_UNAUTHORIZED)