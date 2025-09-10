from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'registros', views.RegistroAsistenciaViewSet, basename='registroasistencia')

urlpatterns = [
    path('', include(router.urls)),
    path('marcar-entrada/', views.marcar_entrada_view, name='marcar-entrada'),
    path('marcar-salida/', views.marcar_salida_view, name='marcar-salida'),
    path('reportes/atrasos/', views.reporte_atrasos_view, name='reporte-atrasos'),
    path('reportes/salidas-anticipadas/', views.reporte_salidas_anticipadas_view, name='reporte-salidas'),
    path('reportes/inasistencias/', views.reporte_inasistencias_view, name='reporte-inasistencias'),
    path('todos-registros/', views.todos_registros_view, name='todos-registros'),
]