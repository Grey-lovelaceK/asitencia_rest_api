# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer, UsuarioUpdateSerializer, LoginSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    # 🔹 CAMBIO IMPORTANTE: Obtener todos los usuarios, no solo activos
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
       
    def get_serializer_class(self): # type: ignore
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer
     
    def list(self, request, *args, **kwargs):
        if not request.user.es_administrador():
            return Response({'error': 'Solo administradores pueden ver la lista de usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)
     
    def create(self, request, *args, **kwargs):
        if not request.user.es_administrador():
            return Response({'error': 'Solo administradores pueden crear usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            usuario = serializer.save()
            
            # 🔹 Retornar el usuario con el UsuarioSerializer completo
            response_data = UsuarioSerializer(usuario).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
     
    def update(self, request, *args, **kwargs):
        if not request.user.es_administrador():
            return Response({'error': 'Solo administradores pueden actualizar usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            usuario = serializer.save()
            
            # 🔹 Retornar el usuario actualizado con el UsuarioSerializer completo
            response_data = UsuarioSerializer(usuario).data
            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
     
    def destroy(self, request, *args, **kwargs):
        if not request.user.es_administrador():
            return Response({'error': 'Solo administradores pueden eliminar usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        
        try:
            usuario_obj = self.get_object()
            # 🔹 Soft delete - marcar como inactivo en lugar de eliminar
            usuario_obj.activo = False
            usuario_obj.save()
            return Response({'success': 'Usuario desactivado correctamente'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
         
        email = serializer.validated_data['email'] # type: ignore
        password = serializer.validated_data['password'] # type: ignore
          
        user = authenticate(request, username=email, password=password)
         
        if user is None:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.activo: # type: ignore
            return Response({'error': 'Usuario inactivo'}, status=status.HTTP_401_UNAUTHORIZED)
         
        # 🔹 Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'usuario': UsuarioSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        # 🔹 Obtener el refresh token del request
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Requiere 'rest_framework_simplejwt.token_blacklist'
        return Response({'success': True})
    except Exception as e:
        return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_session_view(request):
    return Response({
        'logged_in': True, 
        'usuario': UsuarioSerializer(request.user).data
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """Vista para refrescar el access token"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token)
        })
    except Exception as e:
        return Response({'error': 'Refresh token inválido'}, status=status.HTTP_401_UNAUTHORIZED)