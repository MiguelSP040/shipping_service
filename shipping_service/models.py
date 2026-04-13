from django.db import models
from datetime import date, timedelta
import random
import string


class Shipment(models.Model):
    CARRIER_CHOICES = [
        ('DHL', 'DHL'),
        ('FedEx', 'FedEx'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pendiente'),
        ('In Transit', 'En Tránsito'),
        ('Delivered', 'Entregado'),
    ]
    
    order_id = models.IntegerField()
    payment_id = models.IntegerField(null=True, blank=True)
    delivery_address = models.TextField()
    tracking_number = models.CharField(max_length=50, unique=True)
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    estimated_delivery_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['order_id']),
        ]
    
    def __str__(self):
        return f"Shipment {self.tracking_number} - Order {self.order_id}"
    
    @staticmethod
    def generate_tracking_number():
        """Generate a unique tracking number in format SHIP-YYYYMMDD-XXXXXX"""
        today = date.today().strftime('%Y%m%d')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"SHIP-{today}-{random_chars}"
    
    @staticmethod
    def calculate_estimated_delivery(carrier):
        """Calculate estimated delivery date based on carrier"""
        if carrier == 'DHL':
            days = random.randint(3, 5)
        elif carrier == 'FedEx':
            days = random.randint(4, 7)
        else:
            days = 5
        
        return date.today() + timedelta(days=days)
    
    @staticmethod
    def select_random_carrier():
        """Select a random carrier"""
        return random.choice(['DHL', 'FedEx'])

