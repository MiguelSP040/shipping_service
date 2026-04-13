import requests
import logging
from django.conf import settings
from requests.exceptions import RequestException, Timeout, ConnectionError


logger = logging.getLogger('shipping_service')


class ExternalServiceException(Exception):
    """Custom exception for external service errors"""
    def __init__(self, message, status_code=None, service_name=None):
        self.message = message
        self.status_code = status_code
        self.service_name = service_name
        super().__init__(self.message)


class OrderServiceClient:
    """Client for consuming Order Service API (Equipo 3)"""
    
    def __init__(self):
        self.base_url = settings.ORDER_SERVICE_URL
        self.timeout = 10
    
    def get_order(self, order_id):
        """
        Get order details from Order Service
        
        Args:
            order_id: ID of the order to retrieve
            
        Returns:
            dict: Order data including user_id and status
            
        Raises:
            ExternalServiceException: If the request fails
        """
        url = f"{self.base_url}/api/orders/{order_id}/"
        
        try:
            logger.info(f"Requesting order {order_id} from Order Service: {url}")
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 404:
                logger.warning(f"Order {order_id} not found in Order Service")
                raise ExternalServiceException(
                    f"El pedido {order_id} no existe",
                    status_code=404,
                    service_name="Order Service"
                )
            
            if response.status_code != 200:
                logger.error(f"Order Service returned status {response.status_code}")
                raise ExternalServiceException(
                    f"Error al consultar el pedido: {response.status_code}",
                    status_code=response.status_code,
                    service_name="Order Service"
                )
            
            data = response.json()
            logger.info(f"Successfully retrieved order {order_id}")
            return data
            
        except Timeout:
            logger.error(f"Timeout connecting to Order Service")
            raise ExternalServiceException(
                "El servicio de pedidos no responde (timeout)",
                status_code=503,
                service_name="Order Service"
            )
        except ConnectionError:
            logger.error(f"Connection error to Order Service")
            raise ExternalServiceException(
                "No se pudo conectar con el servicio de pedidos",
                status_code=503,
                service_name="Order Service"
            )
        except RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise ExternalServiceException(
                f"Error al comunicarse con el servicio de pedidos: {str(e)}",
                status_code=503,
                service_name="Order Service"
            )
    
    def update_order_status(self, order_id, status):
        """
        Update order status in Order Service
        
        Args:
            order_id: ID of the order to update
            status: New status (e.g., "Enviado")
            
        Returns:
            dict: Updated order data
            
        Raises:
            ExternalServiceException: If the request fails
        """
        url = f"{self.base_url}/api/orders/{order_id}/status/"
        payload = {"status": status}
        
        try:
            logger.info(f"Updating order {order_id} status to '{status}' in Order Service")
            response = requests.patch(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 404:
                logger.warning(f"Order {order_id} not found when updating status")
                raise ExternalServiceException(
                    f"El pedido {order_id} no existe",
                    status_code=404,
                    service_name="Order Service"
                )
            
            if response.status_code not in [200, 204]:
                logger.error(f"Order Service returned status {response.status_code} on update")
                raise ExternalServiceException(
                    f"Error al actualizar el estado del pedido: {response.status_code}",
                    status_code=response.status_code,
                    service_name="Order Service"
                )
            
            logger.info(f"Successfully updated order {order_id} status")
            return response.json() if response.content else {}
            
        except Timeout:
            logger.error(f"Timeout updating order status")
            raise ExternalServiceException(
                "El servicio de pedidos no responde (timeout)",
                status_code=503,
                service_name="Order Service"
            )
        except ConnectionError:
            logger.error(f"Connection error to Order Service")
            raise ExternalServiceException(
                "No se pudo conectar con el servicio de pedidos",
                status_code=503,
                service_name="Order Service"
            )
        except RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise ExternalServiceException(
                f"Error al comunicarse con el servicio de pedidos: {str(e)}",
                status_code=503,
                service_name="Order Service"
            )


class IdentityServiceClient:
    """Client for consuming Identity Service API (Equipo 1)"""
    
    def __init__(self):
        self.base_url = settings.IDENTITY_SERVICE_URL
        self.timeout = 10
    
    def get_user_profile(self, user_id):
        """
        Get user profile from Identity Service
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            dict: User data including delivery address
            
        Raises:
            ExternalServiceException: If the request fails
        """
        url = f"{self.base_url}/api/users/{user_id}/profile/"
        
        try:
            logger.info(f"Requesting user {user_id} profile from Identity Service: {url}")
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 404:
                logger.warning(f"User {user_id} not found in Identity Service")
                raise ExternalServiceException(
                    f"El usuario {user_id} no existe",
                    status_code=404,
                    service_name="Identity Service"
                )
            
            if response.status_code != 200:
                logger.error(f"Identity Service returned status {response.status_code}")
                raise ExternalServiceException(
                    f"Error al consultar el usuario: {response.status_code}",
                    status_code=response.status_code,
                    service_name="Identity Service"
                )
            
            data = response.json()
            logger.info(f"Successfully retrieved user {user_id} profile")
            return data
            
        except Timeout:
            logger.error(f"Timeout connecting to Identity Service")
            raise ExternalServiceException(
                "El servicio de usuarios no responde (timeout)",
                status_code=503,
                service_name="Identity Service"
            )
        except ConnectionError:
            logger.error(f"Connection error to Identity Service")
            raise ExternalServiceException(
                "No se pudo conectar con el servicio de usuarios",
                status_code=503,
                service_name="Identity Service"
            )
        except RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise ExternalServiceException(
                f"Error al comunicarse con el servicio de usuarios: {str(e)}",
                status_code=503,
                service_name="Identity Service"
            )
