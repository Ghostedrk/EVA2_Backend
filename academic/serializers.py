"""Serializadores para transformar los modelos de transporte a JSON."""
from rest_framework import serializers
from .models import Ruta, Bus, Servicio, CarroPasajes, ItemCarro, Venta

"""Serializadores para transformar los modelos de transporte a JSON."""
from rest_framework import serializers
from .models import Ruta, Bus, Servicio, CarroPasajes, ItemCarro, Venta

class ServicioSerializer(serializers.ModelSerializer):
    origen = serializers.CharField(source='ruta.origen', read_only=True)
    destino = serializers.CharField(source='ruta.destino', read_only=True)

    class Meta:
        model = Servicio
        fields = ['id', 'origen', 'destino', 'fecha_salida', 'tipo_asiento', 'tarifa', 'asientos_disponibles']

class ItemCarroSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarro
        fields = ['id', 'servicio', 'rut_pasajero', 'nombre_pasajero', 'numero_asiento']

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Personaliza el token JWT inyectando el rol del usuario."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Inyectamos el claim 'rol'. Usamos is_staff de Django para identificar al administrador.
        token['rol'] = 'Administrador de Flota' if user.is_staff else 'Pasajero'
        return token