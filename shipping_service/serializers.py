from rest_framework import serializers
from .models import Shipment


class DispatchShipmentSerializer(serializers.Serializer):
    """Serializer for dispatch shipment request"""
    order_id = serializers.IntegerField(required=True, min_value=1)
    payment_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_order_id(self, value):
        """Validate order_id is a positive integer"""
        if value <= 0:
            raise serializers.ValidationError("El order_id debe ser un número positivo")
        return value


class ShipmentSerializer(serializers.ModelSerializer):
    """Serializer for Shipment model"""
    
    class Meta:
        model = Shipment
        fields = [
            'id',
            'order_id',
            'payment_id',
            'tracking_number',
            'carrier',
            'delivery_address',
            'status',
            'estimated_delivery_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'tracking_number',
            'carrier',
            'estimated_delivery_date',
            'created_at',
            'updated_at'
        ]


class ShipmentResponseSerializer(serializers.ModelSerializer):
    """Serializer for shipment response"""
    
    class Meta:
        model = Shipment
        fields = [
            'id',
            'order_id',
            'tracking_number',
            'carrier',
            'delivery_address',
            'status',
            'estimated_delivery_date'
        ]


class TrackingSerializer(serializers.ModelSerializer):
    """Serializer for tracking shipment response"""
    
    class Meta:
        model = Shipment
        fields = [
            'tracking_number',
            'status',
            'carrier',
            'estimated_delivery_date',
            'order_id'
        ]


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    status_code = serializers.IntegerField(required=False)
