from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import datetime, time, date
from .models import RegistroAsistencia
from .serializers import RegistroAsistenciaSerializer
from apps.usuarios.models import Usuario

class RegistroAsistenciaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistroAsistenciaSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]  # 🔹 JWT Authentication
    
    def get_queryset(self): # type: ignore
        # 🔹 Ahora usar request.user en lugar de session
        return RegistroAsistencia.objects.filter(usuario=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 🔹 Cambio de AllowAny a IsAuthenticated
def marcar_entrada_view(request):
    try:
        # 🔹 Ya no necesitas check_authenticated, request.user está disponible
        usuario = request.user
        
        print(f"Usuario autenticado: {usuario.email}")
        
        ultimo_registro = RegistroAsistencia.objects.filter(
            usuario=usuario
        ).order_by('-fecha_hora').first()
        
        if ultimo_registro and ultimo_registro.tipo_registro == 'entrada':
            return Response({
                'error': 'Ya tienes una entrada registrada. Debes marcar salida primero.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        registro = RegistroAsistencia.objects.create(
            usuario=usuario,
            tipo_registro='entrada'
        )
        
        return Response({
            'success': True,
            'mensaje': 'Entrada registrada correctamente',
            'pk': registro.id, # type: ignore
            'fecha_hora': registro.fecha_hora
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 🔹 Cambio de AllowAny a IsAuthenticated
def marcar_salida_view(request):
    usuario = request.user  # 🔹 Directo desde request.user
    
    ultimo_registro = RegistroAsistencia.objects.filter(
        usuario=usuario
    ).order_by('-fecha_hora').first() 
    
    if not ultimo_registro or ultimo_registro.tipo_registro == 'salida':
        return Response({
            'error': 'Debes marcar entrada primero.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    registro = RegistroAsistencia.objects.create(
        usuario=usuario,
        tipo_registro='salida'
    )
    
    serializer = RegistroAsistenciaSerializer(registro)
    return Response({
        'success': True,
        'mensaje': 'Salida marcada correctamente',
        'registro': serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 🔹 Cambio de AllowAny a IsAuthenticated
def reporte_atrasos_view(request):
    usuario = request.user  # 🔹 Directo desde request.user
    
    if not usuario.es_administrador():
        return Response({
            'error': 'Solo administradores pueden ver reportes'
        }, status=status.HTTP_403_FORBIDDEN)
    
    hora_limite = time(9, 30)
    atrasos = RegistroAsistencia.objects.filter(
        tipo_registro='entrada',
        fecha_hora__time__gt=hora_limite
    ).order_by('-fecha_hora')
    
    serializer = RegistroAsistenciaSerializer(atrasos, many=True)
    return Response({
        'reportes': serializer.data,
        'total': atrasos.count()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 🔹 Cambio de AllowAny a IsAuthenticated
def reporte_salidas_anticipadas_view(request): # type: ignore
    usuario = request.user  # 🔹 Directo desde request.user
    
    if not usuario.es_administrador():
        return Response({
            'error': 'Solo administradores pueden ver reportes'
        }, status=status.HTTP_403_FORBIDDEN)
    
    hora_limite = time(17, 30)
    salidas_anticipadas = RegistroAsistencia.objects.filter(
        tipo_registro='salida',
        fecha_hora__time__lt=hora_limite
    ).order_by('-fecha_hora')
    
    serializer = RegistroAsistenciaSerializer(salidas_anticipadas, many=True)
    return Response({
        'reportes': serializer.data,
        'total': salidas_anticipadas.count()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 🔹 Cambio de AllowAny a IsAuthenticated
def reporte_inasistencias_view(request):
    usuario = request.user  # 🔹 Directo desde request.user
    
    if not usuario.es_administrador():
        return Response({
            'error': 'Solo administradores pueden ver reportes'
        }, status=status.HTTP_403_FORBIDDEN)
    
    fecha_str = request.GET.get('fecha', str(date.today()))
    try:
        fecha_consulta = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({
            'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    usuarios_con_registro = RegistroAsistencia.objects.filter(
        fecha_hora__date=fecha_consulta
    ).values_list('usuario_id', flat=True).distinct()
    
    usuarios_sin_registro = Usuario.objects.filter(
        activo=True,
        rol='empleado'
    ).exclude(id__in=usuarios_con_registro)
    
    from apps.usuarios.serializers import UsuarioSerializer
    serializer = UsuarioSerializer(usuarios_sin_registro, many=True)
    
    return Response({
        'fecha': fecha_str,
        'usuarios_inasistentes': serializer.data,
        'total': usuarios_sin_registro.count()
    })
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def todos_registros_view(request):
    """Vista para obtener todos los registros de asistencia con filtros opcionales"""
    usuario = request.user
    
    if not usuario.es_administrador():
        return Response({
            'error': 'Solo administradores pueden ver todos los registros'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Obtener parámetros de filtro
    fecha = request.GET.get('fecha')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    usuario_id = request.GET.get('usuario_id')
    
    # Construir queryset base
    queryset = RegistroAsistencia.objects.all()
    
    # Aplicar filtros
    if fecha:
        try:
            fecha_consulta = datetime.strptime(fecha, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_hora__date=fecha_consulta)
        except ValueError:
            return Response({
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    if fecha_inicio and fecha_fin:
        try:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_hora__date__range=[inicio, fin])
        except ValueError:
            return Response({
                'error': 'Formato de fecha inválido para rango. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    if usuario_id:
        queryset = queryset.filter(usuario_id=usuario_id)
    
    # Ordenar por fecha más reciente
    registros = queryset.order_by('-fecha_hora')
    
    # Serializar
    serializer = RegistroAsistenciaSerializer(registros, many=True)
    
    return Response({
        'registros': serializer.data,
        'total': registros.count(),
        'filtros_aplicados': {
            'fecha': fecha,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'usuario_id': usuario_id
        }
    })

# También asegúrate de que el endpoint de salidas anticipadas esté funcionando
# Si no está en tus URLs, agrégalo:

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_salidas_anticipadas_view(request):
    usuario = request.user
    
    if not usuario.es_administrador():
        return Response({
            'error': 'Solo administradores pueden ver reportes'
        }, status=status.HTTP_403_FORBIDDEN)
    
    hora_limite = time(17, 30)  # 5:30 PM
    salidas_anticipadas = RegistroAsistencia.objects.filter(
        tipo_registro='salida',
        fecha_hora__time__lt=hora_limite
    ).order_by('-fecha_hora')
    
    serializer = RegistroAsistenciaSerializer(salidas_anticipadas, many=True)
    return Response({
        'reportes': serializer.data,
        'total': salidas_anticipadas.count()
    })