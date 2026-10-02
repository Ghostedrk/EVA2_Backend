"""Vistas para la plataforma de buses interurbanos."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from rest_framework.response import Response
from rest_framework import generics
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import Servicio, CarroPasajes, ItemCarro, Venta
from .serializers import ServicioSerializer, ItemCarroSerializer, VentaSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# 1. Definición de Permisos (DEBE ir arriba para que los decoradores la encuentren)
class IsAdministradorFlota(BasePermission):
    """Permite el acceso solo si el token JWT contiene el rol de Administrador."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.auth.payload.get('rol') == 'Administrador de Flota'


# 2. Vistas Públicas
class ServicioListView(generics.ListAPIView):
    """Lista servicios disponibles permitiendo filtrar por origen, destino y fecha."""
    queryset = Servicio.objects.filter(asientos_disponibles__gt=0)
    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ruta__origen', 'ruta__destino', 'fecha_salida']


# 3. Vistas de Pasajero (Carro y Checkout)
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def gestionar_carro(request):
    """Maneja el carro persistente (relación 1 a 1 con el usuario)."""
    carro, created = CarroPasajes.objects.get_or_create(usuario=request.user)

    if request.method == 'GET':
        items = carro.items.all()
        serializer = ItemCarroSerializer(items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ItemCarroSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(carro=carro)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        carro.items.all().delete()
        return Response({"detail": "Carro vaciado correctamente."}, status=204)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def checkout_carro(request):
    """Liquida el carro y genera la venta en estado PENDIENTE."""
    carro = CarroPasajes.objects.filter(usuario=request.user).first()
    if not carro or not carro.items.exists():
        return Response({"detail": "El carro está vacío."}, status=400)

    items = carro.items.all()
    total = sum(item.servicio.tarifa for item in items)
    
    detalles_compra = []
    for item in items:
        detalles_compra.append({
            "servicio_id": item.servicio.id,
            "rut": item.rut_pasajero,
            "nombre": item.nombre_pasajero,
            "asiento": item.numero_asiento
        })

    venta = Venta.objects.create(
        usuario=request.user,
        total=total,
        estado='PENDIENTE',
        detalles=detalles_compra
    )
    
    items.delete()
    return Response({"detail": "Checkout exitoso", "venta_id": venta.id}, status=201)


# 4. Vistas de Administrador de Flota
@api_view(['PATCH'])
@permission_classes([IsAdministradorFlota])
@transaction.atomic
def actualizar_estado_venta(request, pk):
    """Actualiza la venta ejecutando el descuento atómico de inventario."""
    try:
        venta = Venta.objects.get(pk=pk)
    except Venta.DoesNotExist:
        return Response(status=404)
        
    nuevo_estado = request.data.get('estado')
    
    if nuevo_estado == 'PAGADO' and venta.estado == 'PENDIENTE':
        for detalle in venta.detalles:
            servicio = Servicio.objects.select_for_update().get(id=detalle['servicio_id'])
            if servicio.asientos_disponibles <= 0:
                raise Exception(f"No hay asientos disponibles para el servicio {servicio.id}")
            servicio.asientos_disponibles -= 1
            servicio.save()
        venta.estado = 'PAGADO'
        venta.save()
        
    elif nuevo_estado == 'CANCELADO' and venta.estado == 'PAGADO':
        for detalle in venta.detalles:
            servicio = Servicio.objects.select_for_update().get(id=detalle['servicio_id'])
            servicio.asientos_disponibles += 1
            servicio.save()
        venta.estado = 'CANCELADO'
        venta.save()
        
    return Response({"detail": f"Venta actualizada a {venta.estado}"})