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

    def check_authenticated(self, request):
        user_id = request.session.get('_auth_user_id')
        if not user_id:
            return False, None
        try:
            usuario = Usuario.objects.get(id=user_id, activo=True)
            return True, usuario
        except Usuario.DoesNotExist:
            return False, None

    def check_admin_permission(self, request):
        is_auth, usuario = self.check_authenticated(request)
        return is_auth and usuario.rol == 'administrador' # type: ignore

    def list(self, request, *args, **kwargs):
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden ver la lista de usuarios'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden crear usuarios'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden actualizar usuarios'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden eliminar usuarios'}, status=status.HTTP_403_FORBIDDEN)
        usuario_obj = self.get_object()
        usuario_obj.activo = False
        usuario_obj.save()
        return Response({'success': 'usuario desactivado correctamente'})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email') # type: ignore
        password = serializer.validated_data.get('password') # type: ignore

        usuario = Usuario.objects.get(email=email, activo=True)

        if not check_password(password, usuario.password):
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        # ⚡ Login con sesiones Django
        login(request, usuario) # type: ignore

        return Response({
            'success': True,
            'usuario': UsuarioSerializer(usuario).data
        })

    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # 🔹 Para debug y siempre responder JSON
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    try:
        logout(request)
        return Response({'success': True})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_session_view(request):
    try:
        return Response({'logged_in': request.user.is_authenticated})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)