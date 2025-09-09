from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import authentication_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer, UsuarioUpdateSerializer, LoginSerializer


@method_decorator(csrf_exempt, name='dispatch')
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.filter(activo=True)
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]  

    def get_serializer_class(self): #type: ignore
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
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.es_administrador():
            return Response({'error': 'Solo administradores pueden actualizar usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.es_administrador():
            return Response({'error': 'Solo administradores pueden eliminar usuarios'},
                            status=status.HTTP_403_FORBIDDEN)
        usuario_obj = self.get_object()
        usuario_obj.activo = False
        usuario_obj.save()
        return Response({'success': 'Usuario desactivado correctamente'})

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([BasicAuthentication]) 
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']  # type: ignore
    password = serializer.validated_data['password']  # type: ignore

    # 🔹 Aquí está el cambio
    user = authenticate(request, username=email, password=password)

    if user is None:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)
    return Response({
        'success': True,
        'usuario': UsuarioSerializer(user).data
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication])
def logout_view(request):
    logout(request)
    return Response({'success': True})

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication])
def check_session_view(request):
    return Response({'logged_in': True, 'usuario': UsuarioSerializer(request.user).data})
