from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login, logout
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer, UsuarioUpdateSerializer, LoginSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.filter(activo=True)

    def get_serializer_class(self): # type: ignore
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer
    
    def get_permissions(self):

        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def check_authenticated(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return False, None
        try:
            usuario = Usuario.objects.get(id=user_id, activo=True)
            return True, usuario
        except Usuario.DoesNotExist:
            return False, None
    
    def check_admin_permission(self, request):
        is_auth, usuario = self.check_authenticated(request)
        if not is_auth:
            return False
        return usuario.es_administrador() #type: ignore
        
    def create(self, request, *args, **kwargs):
        # Verificar que esté autenticado
        is_auth, usuario = self.check_authenticated(request)
        if not is_auth:
            return Response({'error': 'Debes estar logueado'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que sea admin
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden crear usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        is_auth, usuario = self.check_authenticated(request)
        if not is_auth:
            return Response({'error': 'Debes estar logueado'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
                          
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden actualizar usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        is_auth, usuario = self.check_authenticated(request)
        if not is_auth:
            return Response({'error': 'Debes estar logueado'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
                          
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden eliminar usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
    
        usuario_obj = self.get_object()   
        usuario_obj.activo = False
        usuario_obj.save()
        return Response({'success': 'usuario desactivado correctamente'})
    
    def list(self, request, *args, **kwargs):
        is_auth, usuario = self.check_authenticated(request)
        if not is_auth:
            return Response({'error': 'Debes estar logueado'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    
        if not self.check_admin_permission(request):
            return Response({'error': 'Solo administradores pueden ver la lista de usuarios'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        return super().list(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data.get('email') #type: ignore
    password = serializer.validated_data.get('password') #type: ignore
    
    if not email or not password:
        return Response({'error': 'Email y password son requeridos'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    try:
        usuario = Usuario.objects.get(email=email, activo=True)
        if check_password(password, usuario.password):
            request.session['user_id'] = usuario.pk
            request.session.modified = True
            request.session.save()
            
            return Response({
                'success': True,
                'usuario': UsuarioSerializer(usuario).data,
                'session_id': request.session.session_key  
            })
        else:
            return Response({'error': 'Credenciales inválidas'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, 
                      status=status.HTTP_404_NOT_FOUND)
        
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    request.session.flush()
    return Response({'success': True})