"""URLs REST de la aplicación de buses."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import reservar_pasaje_view

urlpatterns = [
    # Autenticación JWT
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # PÚBLICO: Búsqueda de pasajes
    path('servicios/buscar/', views.ServicioListView.as_view(), name='buscar-servicios'),

    # PASAJERO: Carro persistente y checkout
    path('carro-pasajes/', views.gestionar_carro, name='carro-pasajes'),
    path('ventas/checkout/', views.checkout_carro, name='checkout-ventas'),
    
    # ADMINISTRADOR DE FLOTA: Gestión transaccional
    path('ventas/<int:pk>/estado/', views.actualizar_estado_venta, name='actualizar-estado-venta'),

    # Ruta para ver el template visual directo
    path('reservar/', reservar_pasaje_view, name='reservar_pasaje'),
]