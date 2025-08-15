"""
Core views for ERP Sales Service
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import psutil
import time


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Basic health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': settings.SALES_SERVICE_NAME,
        'version': settings.SALES_SERVICE_VERSION,
        'timestamp': time.time(),
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def service_status(request):
    """Detailed service status endpoint"""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check Redis connection
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        redis_status = cache.get('health_check') == 'ok'
        
        status_data = {
            'status': 'healthy',
            'service': settings.SALES_SERVICE_NAME,
            'version': settings.SALES_SERVICE_VERSION,
            'timestamp': time.time(),
            'components': {
                'database': 'healthy',
                'redis': 'healthy' if redis_status else 'unhealthy',
                'elasticsearch': 'unknown',  # TODO: Add ES health check
                'kafka': 'unknown',  # TODO: Add Kafka health check
            },
            'system': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
            }
        }
        
        return Response(status_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'service': settings.SALES_SERVICE_NAME,
            'version': settings.SALES_SERVICE_VERSION,
            'timestamp': time.time(),
            'error': str(e),
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def service_metrics(request):
    """Service metrics endpoint"""
    try:
        from apps.leads.models import Lead
        from apps.opportunities.models import Opportunity
        from apps.quotations.models import Quotation
        from apps.invoices.models import Invoice
        from apps.customers.models import Customer
        
        metrics = {
            'service': settings.SALES_SERVICE_NAME,
            'version': settings.SALES_SERVICE_VERSION,
            'timestamp': time.time(),
            'counts': {
                'leads': Lead.objects.filter(is_active=True).count(),
                'opportunities': Opportunity.objects.filter(is_active=True).count(),
                'quotations': Quotation.objects.filter(is_active=True).count(),
                'invoices': Invoice.objects.filter(is_active=True).count(),
                'customers': Customer.objects.filter(is_active=True).count(),
            },
            'system': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
            }
        }
        
        return Response(metrics, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 