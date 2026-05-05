"""
Eagle API Proxy Views
Forwards Eagle API requests from Django backend to Next.js frontend
"""

import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["GET"])
def eagle_properties_proxy(request):
    """
    Proxy Eagle properties requests to Next.js frontend
    """
    try:
        # Forward request to Next.js frontend (using container IP on bridge network)
        frontend_url = "http://172.16.0.2:3000/api/eagle/properties"
        
        # Forward query parameters
        params = request.GET.dict()
        
        # Make request to frontend
        response = requests.get(frontend_url, params=params, timeout=30)
        
        # Return the response
        return JsonResponse(
            response.json(),
            status=response.status_code,
            safe=False
        )
    except requests.RequestException as e:
        return JsonResponse(
            {
                "success": False,
                "error": f"Failed to fetch properties: {str(e)}"
            },
            status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def eagle_property_detail_proxy(request, property_id):
    """
    Proxy Eagle property detail requests to Next.js frontend
    """
    try:
        # Forward request to Next.js frontend (using container IP on bridge network)
        frontend_url = f"http://172.16.0.2:3000/api/eagle/properties/{property_id}"
        
        # Make request to frontend
        response = requests.get(frontend_url, timeout=30)
        
        # Return the response
        return JsonResponse(
            response.json(),
            status=response.status_code,
            safe=False
        )
    except requests.RequestException as e:
        return JsonResponse(
            {
                "success": False,
                "error": f"Failed to fetch property: {str(e)}"
            },
            status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def eagle_test_auth_proxy(request):
    """
    Proxy Eagle auth test requests to Next.js frontend
    """
    try:
        # Forward request to Next.js frontend (using container IP on bridge network)
        frontend_url = "http://172.16.0.2:3000/api/eagle/test-auth"
        
        # Make request to frontend
        response = requests.get(frontend_url, timeout=30)
        
        # Return the response
        return JsonResponse(
            response.json(),
            status=response.status_code,
            safe=False
        )
    except requests.RequestException as e:
        return JsonResponse(
            {
                "success": False,
                "error": f"Failed to test auth: {str(e)}"
            },
            status=500
        )
