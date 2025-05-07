# appProtectiOn/admin.py

from django.contrib import admin
from .models import Alerta

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display    = ('id', 'usuario', 'lat', 'lng', 'audio', 'timestamp')
    readonly_fields = ('timestamp',)
