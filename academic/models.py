"""Modelos para la plataforma de arriendo de pasajes de buses interurbanos."""

from django.db import models
from django.contrib.auth.models import User
import uuid

class Ruta(models.Model):
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.origen} - {self.destino}"

class Bus(models.Model):
    patente = models.CharField(max_length=10, unique=True)
    capacidad_total = models.PositiveIntegerField()

    def __str__(self):
        return f"Bus {self.patente}"

class Servicio(models.Model):
    TIPO_ASIENTO_CHOICES = [
        ('semicama', 'Semicama'),
        ('cama', 'Cama'),
    ]
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='servicios')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    fecha_salida = models.DateTimeField()
    tipo_asiento = models.CharField(max_length=20, choices=TIPO_ASIENTO_CHOICES)
    tarifa = models.PositiveIntegerField()
    asientos_disponibles = models.PositiveIntegerField()

class CarroPasajes(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carro')
    creado_en = models.DateTimeField(auto_now_add=True)

class ItemCarro(models.Model):
    carro = models.ForeignKey(CarroPasajes, on_delete=models.CASCADE, related_name='items')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    rut_pasajero = models.CharField(max_length=15)
    nombre_pasajero = models.CharField(max_length=150)
    numero_asiento = models.PositiveIntegerField()

class Venta(models.Model):
    ESTADOS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras')
    total = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='PENDIENTE')
    codigo_boleto = models.UUIDField(default=uuid.uuid4, editable=False)
    detalles = models.JSONField(default=list)
    creado_en = models.DateTimeField(auto_now_add=True)