from django.urls import path
from .views import DispatchShipmentView, TrackShipmentView

urlpatterns = [
    path('dispatch/', DispatchShipmentView.as_view(), name='dispatch-shipment'),
    path('track/<str:tracking_number>/', TrackShipmentView.as_view(), name='track-shipment'),
]
