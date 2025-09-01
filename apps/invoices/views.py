"""
Invoice views for ERP Sales Service
"""
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer, InvoiceItemSerializer
from core.permissions import OrganizationPermission


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing invoices"""
    
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, OrganizationPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'customer', 'assigned_to']
    search_fields = ['invoice_number', 'subject', 'customer__name']
    ordering_fields = ['created_at', 'due_date', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter invoices by organization"""
        organization_id = self.request.headers.get('X-Organization-ID')
        return Invoice.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).select_related('customer', 'quotation').prefetch_related('items')
    
    @action(detail=True, methods=['post'])
    def generate_document(self, request, pk=None):
        """
        Generate document (PDF/HTML) for an invoice using the Invoice Service
        
        POST /api/v1/invoices/{id}/generate_document/
        {
            "format": "pdf",  // "pdf", "html", or "json"
            "template_id": "optional-template-id",
            "options": {
                "include_logo": true,
                "watermark": "PAID",
                "language": "en"
            }
        }
        """
        invoice = self.get_object()
        format_type = request.data.get('format', 'pdf').lower()
        template_id = request.data.get('template_id')
        options = request.data.get('options', {})
        
        # Validate format
        valid_formats = ['pdf', 'html', 'json']
        if format_type not in valid_formats:
            return Response(
                {'error': f'Invalid format. Use one of: {", ".join(valid_formats)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate document using the shared invoice service
            result = invoice.generate_document(
                format_type=format_type,
                template_id=template_id,
                **options
            )
            
            if not result:
                return Response(
                    {'error': 'Failed to generate document'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            document_data = result.get('document_data')
            content_type = result.get('content_type')
            filename = result.get('filename')
            
            if format_type == 'json':
                # Return JSON data directly
                return Response(document_data, status=status.HTTP_200_OK)
            else:
                # Return file download
                response = HttpResponse(document_data, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = len(document_data)
                return response
                
        except Exception as e:
            return Response(
                {'error': f'Error generating document: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """
        Generate PDF for an invoice (backward compatibility endpoint)
        
        POST /api/v1/invoices/{id}/generate_pdf/
        {
            "template_id": "optional-template-id"
        }
        """
        # Redirect to the new generate_document endpoint
        request.data['format'] = 'pdf'
        return self.generate_document(request, pk)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        
        if invoice.status == 'paid':
            return Response(
                {'message': 'Invoice is already marked as paid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'paid'
        invoice.paid_date = request.data.get('paid_date') or timezone.now().date()
        invoice.save()
        
        # Could publish event to notify other services
        # publish_invoice_paid_event(invoice)
        
        return Response(
            InvoiceSerializer(invoice).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def send_invoice(self, request, pk=None):
        """Send invoice to customer (update status to sent)"""
        invoice = self.get_object()
        
        if invoice.status != 'draft':
            return Response(
                {'error': 'Only draft invoices can be sent'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'sent'
        invoice.save()
        
        # Here you could integrate with email service to actually send the invoice
        # email_service.send_invoice_email(invoice)
        
        return Response(
            {'message': 'Invoice sent successfully'},
            status=status.HTTP_200_OK
        )


class InvoiceItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing invoice items"""
    
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated, OrganizationPermission]
    
    def get_queryset(self):
        """Filter invoice items by organization"""
        organization_id = self.request.headers.get('X-Organization-ID')
        return InvoiceItem.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).select_related('invoice', 'product')
    @acti
on(detail=False, methods=['get'])
    def templates(self, request):
        """
        List available invoice templates from the Invoice Service
        
        GET /api/v1/invoices/templates/
        """
        try:
            from grpc_clients.invoice_client import invoice_service_client
            
            organization_id = request.headers.get('X-Organization-ID')
            if not organization_id:
                return Response(
                    {'error': 'Organization ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            templates = invoice_service_client.list_templates(
                organization_id=organization_id,
                active_only=request.query_params.get('active_only', 'true').lower() == 'true'
            )
            
            return Response({
                'templates': templates,
                'count': len(templates)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error fetching templates: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def create_template(self, request):
        """
        Create a new invoice template in the Invoice Service
        
        POST /api/v1/invoices/create_template/
        {
            "name": "Custom Template",
            "description": "Custom invoice template",
            "html_template": "<html>...</html>",
            "css_styles": "body { font-family: Arial; }",
            "variables": {"company_name": "{{company_name}}"},
            "is_default": false
        }
        """
        try:
            from grpc_clients.invoice_client import invoice_service_client
            
            organization_id = request.headers.get('X-Organization-ID')
            if not organization_id:
                return Response(
                    {'error': 'Organization ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            template_data = request.data.copy()
            template_data['organization_id'] = organization_id
            
            template_id = invoice_service_client.create_template(template_data)
            
            if template_id:
                return Response({
                    'template_id': template_id,
                    'message': 'Template created successfully'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Failed to create template'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Error creating template: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def service_health(self, request):
        """
        Check Invoice Service health
        
        GET /api/v1/invoices/service_health/
        """
        try:
            from grpc_clients.invoice_client import invoice_service_client
            
            is_healthy = invoice_service_client.health_check()
            
            return Response({
                'invoice_service_healthy': is_healthy,
                'status': 'healthy' if is_healthy else 'unhealthy'
            }, status=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except Exception as e:
            return Response({
                'invoice_service_healthy': False,
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)