"""Vistas para la plataforma de buses interurbanos."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from rest_framework.response import Response
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import Servicio, CarroPasajes, ItemCarro, Venta
from .serializers import ServicioSerializer, ItemCarroSerializer, VentaSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.shortcuts import render

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
@extend_schema(request=ItemCarroSerializer, responses={201: ItemCarroSerializer})
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
    """Liquida el carro, descuenta el stock de forma atómica y genera la venta directamente como PAGADA."""
    carro = CarroPasajes.objects.filter(usuario=request.user).first()
    if not carro or not carro.items.exists():
        return Response({"detail": "El carro está vacío."}, status=400)

    items = carro.items.all()
    total = sum(item.servicio.tarifa for item in items)
    
    detalles_compra = []
    for item in items:
        # Descontar stock atómicamente por cada asiento comprado
        servicio = Servicio.objects.select_for_update().get(id=item.servicio.id)
        if servicio.asientos_disponibles <= 0:
            raise Exception(f"No hay asientos disponibles para el servicio {servicio.id}")
        
        servicio.asientos_disponibles -= 1
        servicio.save()

        detalles_compra.append({
            "servicio_id": item.servicio.id,
            "rut": item.rut_pasajero,
            "nombre": item.nombre_pasajero,
            "asiento": item.numero_asiento
        })

    # Creamos la venta directamente en estado PAGADO para que se bloquee el asiento en gris
    venta = Venta.objects.create(
        usuario=request.user,
        total=total,
        estado='PAGADO',
        detalles=detalles_compra
    )
    
    items.delete()
    return Response({"detail": "¡Checkout realizado con éxito! Asientos reservados.", "venta_id": venta.id}, status=201)


# 4. Vistas de Administrador de Flota
@extend_schema(request={'application/json': {'type': 'object', 'properties': {'estado': {'type': 'string'}}}})
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
    
    if nuevo_estado == 'CANCELADO' and venta.estado == 'PAGADO':
        for detalle in venta.detalles:
            servicio = Servicio.objects.select_for_update().get(id=detalle['servicio_id'])
            servicio.asientos_disponibles += 1
            servicio.save()
        venta.estado = 'CANCELADO'
        venta.save()
        
    return Response({"detail": f"Venta actualizada a {venta.estado}"})

def reservar_pasaje_view(request):
    servicios = Servicio.objects.all()
    
    servicios_con_asientos = []
    for servicio in servicios:
        ventas_activas = Venta.objects.filter(estado__in=['PENDIENTE', 'PAGADO'])
        
        asientos_ocupados = []
        for venta in ventas_activas:
            if isinstance(venta.detalles, list):
                for detalle in venta.detalles:
                    s_id = detalle.get('servicio_id') or detalle.get('servicio')
                    if s_id and int(s_id) == int(servicio.id):
                        asiento = detalle.get('asiento') or detalle.get('numero_asiento')
                        if asiento is not None:
                            asientos_ocupados.append(int(asiento))

        # Obtenemos la capacidad total real del bus asociado a este servicio
        capacidad_bus = servicio.bus.capacidad_total
        
        # Calculamos disponibles reales restando los ocupados de la capacidad del bus
        asientos_disponibles_reales = capacidad_bus - len(set(asientos_ocupados))

        servicios_con_asientos.append({
            'servicio': servicio,
            'asientos_ocupados': asientos_ocupados,
            'asientos_disponibles_reales': asientos_disponibles_reales,
            # Creamos una lista numérica exacta del 1 hasta la capacidad del bus (ej: 35)
            'rango_asientos': range(1, capacidad_bus + 1)
        })

    contexto = {
        'servicios_con_asientos': servicios_con_asientos
    }
    return render(request, 'buses/reservar.html', contexto)