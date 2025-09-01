"""
gRPC client for Invoice Service integration
"""
import grpc
import logging
from typing import Optional, Dict, Any, List
from django.conf import settings
from datetime import datetime
from decimal import Decimal

# Import generated protobuf classes (would need to be generated)
# from proto.invoice import invoice_pb2, invoice_pb2_grpc

logger = logging.getLogger(__name__)


class InvoiceServiceClient:
    """Client for communicating with the Invoice Service as a shared document generator"""
    
    def __init__(self):
        self.channel = None
        self.stub = None
        self._connect()
    
    def _connect(self):
        """Establish gRPC connection to Invoice Service"""
        invoice_service_host = getattr(settings, 'INVOICE_SERVICE_HOST', 'localhost')
        invoice_service_port = getattr(settings, 'INVOICE_SERVICE_PORT', '50055')
        timeout = getattr(settings, 'INVOICE_SERVICE_TIMEOUT', '10s')
        
        # Configure gRPC options for better reliability
        options = [
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.min_ping_interval_without_data_ms', 300000)
        ]
        
        self.channel = grpc.insecure_channel(
            f'{invoice_service_host}:{invoice_service_port}',
            options=options
        )
        # self.stub = invoice_pb2_grpc.InvoiceServiceStub(self.channel)
        logger.info(f"Connected to Invoice Service at {invoice_service_host}:{invoice_service_port}")
    
    def generate_document(self, 
                         invoice_data: Dict[str, Any], 
                         format_type: str = 'pdf',
                         template_id: Optional[str] = None,
                         options: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Generate document (PDF/HTML) for an invoice using the Invoice Service
        
        Args:
            invoice_data: Dictionary containing invoice information
            format_type: 'pdf', 'html', or 'json'
            template_id: Optional template ID for custom formatting
            options: Additional generation options
            
        Returns:
            Dictionary with document_data (bytes), content_type, filename, file_size
        """
        try:
            # Validate and normalize invoice data
            normalized_data = self._normalize_invoice_data(invoice_data)
            
            # Create generation request
            request_data = {
                'invoice_data': normalized_data,
                'format': format_type.upper(),
                'template_id': template_id,
                'options': options or {}
            }
            
            # For now, simulate the call (would be actual gRPC call)
            logger.info(f"Generating {format_type} document for invoice {normalized_data.get('invoice_number')}")
            
            # Placeholder response - in real implementation this would be:
            # response = self.stub.GenerateInvoiceDocument(request)
            # return {
            #     'document_data': response.document_data,
            #     'content_type': response.content_type,
            #     'filename': response.filename,
            #     'file_size': response.file_size
            # }
            
            return {
                'document_data': b'%PDF-1.4 placeholder',  # Placeholder PDF data
                'content_type': 'application/pdf' if format_type == 'pdf' else 'text/html',
                'filename': f"invoice_{normalized_data.get('invoice_number', 'unknown')}.{format_type}",
                'file_size': 1024
            }
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error generating invoice document: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating invoice document: {e}")
            return None
    
    def create_template(self, template_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new invoice template in the Invoice Service
        
        Args:
            template_data: Template configuration
            
        Returns:
            Template ID or None if creation fails
        """
        try:
            logger.info(f"Creating template: {template_data.get('name')}")
            # Placeholder implementation
            # response = self.stub.CreateTemplate(request)
            # return response.template.id
            return "template-123"  # Placeholder
        except Exception as e:
            logger.error(f"Error creating invoice template: {e}")
            return None
    
    def list_templates(self, organization_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List available templates for an organization
        
        Args:
            organization_id: Organization ID
            active_only: Only return active templates
            
        Returns:
            List of template dictionaries
        """
        try:
            logger.info(f"Listing templates for organization: {organization_id}")
            # Placeholder implementation
            return [
                {
                    'id': 'default-template',
                    'name': 'Default Invoice Template',
                    'description': 'Standard invoice template',
                    'is_default': True,
                    'is_active': True
                }
            ]
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return []
    
    def health_check(self) -> bool:
        """
        Check if the Invoice Service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Placeholder implementation
            # response = self.stub.HealthCheck(empty_pb2.Empty())
            # return response.success
            return True
        except Exception as e:
            logger.error(f"Invoice Service health check failed: {e}")
            return False
    
    def _normalize_invoice_data(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize invoice data to ensure compatibility with Invoice Service
        
        Args:
            invoice_data: Raw invoice data from sales service
            
        Returns:
            Normalized invoice data
        """
        normalized = {
            'id': str(invoice_data.get('id', '')),
            'organization_id': str(invoice_data.get('organization_id', '')),
            'invoice_number': str(invoice_data.get('invoice_number', '')),
            'title': str(invoice_data.get('title', invoice_data.get('subject', ''))),
            'description': str(invoice_data.get('description', '')),
            'status': str(invoice_data.get('status', 'draft')).upper(),
            'currency': str(invoice_data.get('currency', 'USD')),
            'notes': str(invoice_data.get('notes', '')),
        }
        
        # Handle customer data
        customer_data = invoice_data.get('customer', {})
        normalized['customer'] = {
            'id': str(customer_data.get('id', '')),
            'name': str(customer_data.get('name', '')),
            'email': str(customer_data.get('email', '')),
            'phone': str(customer_data.get('phone', '')),
            'tax_id': str(customer_data.get('tax_id', '')),
            'billing_address': self._normalize_address(customer_data.get('billing_address', {})),
            'shipping_address': self._normalize_address(customer_data.get('shipping_address', {})),
        }
        
        # Handle financial data
        normalized.update({
            'subtotal': float(invoice_data.get('subtotal', 0)),
            'tax_rate': float(invoice_data.get('tax_rate', 0)),
            'tax_amount': float(invoice_data.get('tax_amount', 0)),
            'discount_amount': float(invoice_data.get('discount_amount', 0)),
            'total_amount': float(invoice_data.get('total_amount', 0)),
        })
        
        # Handle dates
        for date_field in ['issue_date', 'due_date', 'paid_date']:
            date_value = invoice_data.get(date_field)
            if date_value:
                if isinstance(date_value, str):
                    normalized[date_field] = date_value
                else:
                    normalized[date_field] = date_value.isoformat()
        
        # Handle items
        items = invoice_data.get('items', [])
        normalized['items'] = [
            {
                'id': str(item.get('id', '')),
                'name': str(item.get('name', '')),
                'description': str(item.get('description', '')),
                'quantity': float(item.get('quantity', 0)),
                'unit_price': float(item.get('unit_price', 0)),
                'discount_rate': float(item.get('discount_rate', 0)),
                'tax_rate': float(item.get('tax_rate', 0)),
                'total': float(item.get('total', 0)),
                'metadata': item.get('metadata', {})
            }
            for item in items
        ]
        
        # Handle metadata
        normalized['metadata'] = invoice_data.get('metadata', {})
        
        return normalized
    
    def _normalize_address(self, address_data: Dict[str, Any]) -> Dict[str, str]:
        """Normalize address data"""
        return {
            'street': str(address_data.get('street', '')),
            'city': str(address_data.get('city', '')),
            'state': str(address_data.get('state', '')),
            'postal_code': str(address_data.get('postal_code', '')),
            'country': str(address_data.get('country', ''))
        }
    
    def __del__(self):
        """Close gRPC connection"""
        if self.channel:
            try:
                self.channel.close()
            except Exception:
                pass


# Singleton instance
invoice_service_client = InvoiceServiceClient()