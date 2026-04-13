from django.contrib import admin
from .models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'order_id', 'carrier', 'status', 'estimated_delivery_date', 'created_at']
    list_filter = ['status', 'carrier', 'created_at']
    search_fields = ['tracking_number', 'order_id', 'delivery_address']
    readonly_fields = ['tracking_number', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('order_id', 'payment_id')
        }),
        ('Información de Envío', {
            'fields': ('tracking_number', 'carrier', 'status', 'delivery_address', 'estimated_delivery_date')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

