"""Configuración del panel administrativo para la gestión de flota y pasajes."""

from django.contrib import admin
from .models import Ruta, Bus, Servicio, CarroPasajes, ItemCarro, Venta

admin.site.register(Ruta)
admin.site.register(Bus)
admin.site.register(Servicio)
admin.site.register(CarroPasajes)
admin.site.register(ItemCarro)
admin.site.register(Venta)