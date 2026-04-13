#!/usr/bin/env python3
"""
Script de prueba para el Shipping Service API
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8002"


def print_section(title):
    """Imprime un separador de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_dispatch_shipment():
    """Prueba el endpoint de dispatch"""
    print_section("TEST: Crear Envío (POST /api/shipping/dispatch/)")
    
    url = f"{BASE_URL}/api/shipping/dispatch/"
    payload = {
        "order_id": 123,
        "payment_id": 456
    }
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 201:
            print("\n✓ Envío creado exitosamente")
            return response.json()['tracking_number']
        else:
            print("\n✗ Error al crear envío")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   python3 manage.py runserver")
        return None
    except Exception as e:
        print(f"\n✗ Error inesperado: {str(e)}")
        return None


def test_track_shipment(tracking_number):
    """Prueba el endpoint de tracking"""
    print_section("TEST: Rastrear Envío (GET /api/shipping/track/<tracking_number>/)")
    
    if not tracking_number:
        print("Saltando test: No hay tracking number disponible")
        return
    
    url = f"{BASE_URL}/api/shipping/track/{tracking_number}/"
    
    print(f"URL: {url}")
    print(f"Tracking Number: {tracking_number}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("\n✓ Envío encontrado")
        else:
            print("\n✗ Envío no encontrado")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: No se pudo conectar al servidor")
    except Exception as e:
        print(f"\n✗ Error inesperado: {str(e)}")


def test_swagger():
    """Verifica que Swagger esté disponible"""
    print_section("TEST: Documentación Swagger")
    
    url = f"{BASE_URL}/api/schema/"
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Swagger disponible")
            print(f"\nAccede a la documentación interactiva en:")
            print(f"  - Swagger UI: {BASE_URL}/api/schema/swagger-ui/")
            print(f"  - ReDoc:      {BASE_URL}/api/schema/redoc/")
        else:
            print("✗ Swagger no disponible")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: No se pudo conectar al servidor")
    except Exception as e:
        print(f"\n✗ Error inesperado: {str(e)}")


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("  SHIPPING SERVICE API - SUITE DE PRUEBAS")
    print("="*60)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: Swagger
    test_swagger()
    
    # Test 2: Dispatch
    tracking_number = test_dispatch_shipment()
    
    # Test 3: Track
    if tracking_number:
        test_track_shipment(tracking_number)
    
    # Test con tracking number de ejemplo (debería fallar)
    test_track_shipment("SHIP-20260410-EJEMPLO")
    
    print_section("PRUEBAS COMPLETADAS")
    print("Nota: Los tests reales requieren que Order Service e Identity Service")
    print("      estén disponibles y respondan correctamente.")


if __name__ == "__main__":
    main()
