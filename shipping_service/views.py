from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from .models import Shipment
from .serializers import (
    DispatchShipmentSerializer,
    ShipmentResponseSerializer,
    TrackingSerializer,
    ErrorResponseSerializer
)
from .services import OrderServiceClient, IdentityServiceClient, ExternalServiceException


logger = logging.getLogger('shipping_service')


class DispatchShipmentView(APIView):
    """
    POST /api/shipping/dispatch/
    
    Endpoint para crear un envío de un pedido pagado.
    Valida con Order Service que el pedido existe y está pagado,
    obtiene la dirección del usuario desde Identity Service,
    genera una guía de rastreo y actualiza el estado del pedido a "Enviado".
    """
    
    @extend_schema(
        request=DispatchShipmentSerializer,
        responses={
            201: OpenApiResponse(
                response=ShipmentResponseSerializer,
                description="Envío creado exitosamente"
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Datos inválidos en la solicitud"
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Pedido o usuario no encontrado"
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="El pedido no está en estado 'Pagado'"
            ),
            503: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Servicio externo no disponible"
            ),
        },
        description="Crea un envío para un pedido pagado y genera una guía de rastreo",
        tags=["Shipping"]
    )
    def post(self, request):
        serializer = DispatchShipmentSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Invalid dispatch request: {serializer.errors}")
            return Response(
                {"error": "Datos inválidos", "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order_id = serializer.validated_data['order_id']
        payment_id = serializer.validated_data.get('payment_id')
        
        order_client = OrderServiceClient()
        identity_client = IdentityServiceClient()
        
        try:
            # Step 1: Validate order exists and is paid
            logger.info(f"Step 1: Validating order {order_id}")
            order_data = order_client.get_order(order_id)
            
            order_status = order_data.get('status') or order_data.get('estado')
            user_id = order_data.get('user_id') or order_data.get('usuario') or order_data.get('id_usuario')
            
            if not user_id:
                logger.error(f"User ID not found in order data: {order_data}")
                return Response(
                    {"error": "El pedido no contiene información del usuario"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if order is paid (accept different variations)
            paid_statuses = ['Pagado', 'pagado', 'PAGADO', 'Paid', 'paid', 'PAID']
            if order_status not in paid_statuses:
                logger.warning(f"Order {order_id} is not paid. Status: {order_status}")
                return Response(
                    {
                        "error": "El pedido no está pagado",
                        "detail": f"Estado actual del pedido: {order_status}"
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            # Step 2: Get user delivery address
            logger.info(f"Step 2: Getting user {user_id} delivery address")
            user_data = identity_client.get_user_profile(user_id)
            
            delivery_address = (
                user_data.get('address') or 
                user_data.get('direccion') or 
                user_data.get('dirección') or
                user_data.get('direccion_envio') or
                user_data.get('shipping_address')
            )
            
            if not delivery_address:
                logger.error(f"Delivery address not found for user {user_id}")
                return Response(
                    {"error": "El usuario no tiene dirección de envío registrada"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Step 3: Check if shipment already exists for this order
            existing_shipment = Shipment.objects.filter(order_id=order_id).first()
            if existing_shipment:
                logger.warning(f"Shipment already exists for order {order_id}")
                return Response(
                    {
                        "error": "Ya existe un envío para este pedido",
                        "detail": f"Guía de rastreo: {existing_shipment.tracking_number}"
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            # Step 4: Generate tracking number, select carrier, and calculate delivery date
            logger.info(f"Step 3: Creating shipment for order {order_id}")
            
            tracking_number = Shipment.generate_tracking_number()
            while Shipment.objects.filter(tracking_number=tracking_number).exists():
                tracking_number = Shipment.generate_tracking_number()
            
            carrier = Shipment.select_random_carrier()
            estimated_delivery = Shipment.calculate_estimated_delivery(carrier)
            
            # Step 5: Create shipment record
            shipment = Shipment.objects.create(
                order_id=order_id,
                payment_id=payment_id,
                delivery_address=delivery_address,
                tracking_number=tracking_number,
                carrier=carrier,
                status='Pending',
                estimated_delivery_date=estimated_delivery
            )
            
            logger.info(f"Shipment created: {tracking_number}")
            
            # Step 6: Update order status to "Enviado"
            logger.info(f"Step 4: Updating order {order_id} status to 'Enviado'")
            try:
                order_client.update_order_status(order_id, 'Enviado')
            except ExternalServiceException as e:
                logger.warning(f"Failed to update order status, but shipment was created: {str(e)}")
            
            response_serializer = ShipmentResponseSerializer(shipment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ExternalServiceException as e:
            logger.error(f"External service error: {e.message}")
            return Response(
                {
                    "error": e.message,
                    "service": e.service_name
                },
                status=e.status_code or status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Unexpected error in dispatch: {str(e)}", exc_info=True)
            return Response(
                {"error": "Error interno del servidor", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrackShipmentView(APIView):
    """
    GET /api/shipping/track/<tracking_number>/
    
    Endpoint para consultar el estado de un envío mediante su guía de rastreo.
    """
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='tracking_number',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Guía de rastreo del envío'
            )
        ],
        responses={
            200: OpenApiResponse(
                response=TrackingSerializer,
                description="Información del envío"
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Envío no encontrado"
            ),
        },
        description="Consulta el estado de un envío por su guía de rastreo",
        tags=["Shipping"]
    )
    def get(self, request, tracking_number):
        try:
            logger.info(f"Tracking shipment: {tracking_number}")
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            
            serializer = TrackingSerializer(shipment)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Shipment.DoesNotExist:
            logger.warning(f"Tracking number not found: {tracking_number}")
            return Response(
                {"error": "Guía de rastreo no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error in tracking: {str(e)}", exc_info=True)
            return Response(
                {"error": "Error interno del servidor", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

