# Invoice Service Integration Documentation

**Date:** January 16, 2025  
**Author:** Kiro AI Assistant  
**Version:** 1.0  
**Service:** ERP Sales Service  

## Overview

This document describes the integration of the dedicated Invoice Service with the ERP Sales Service. The integration follows a hybrid approach where the Sales Service maintains invoice business logic and data management, while leveraging the Invoice Service as a specialized document generator for PDF, HTML, and JSON formats.

## Integration Architecture

### Design Pattern: Hybrid Service Integration

```
┌─────────────────┐    gRPC     ┌─────────────────┐
│   Sales Service │ ──────────► │ Invoice Service │
│                 │             │                 │
│ • Business Logic│             │ • PDF Generation│
│ • Data Storage  │             │ • HTML Export   │
│ • CRUD Operations│             │ • Templates     │
│ • Status Mgmt   │             │ • Caching       │
└─────────────────┘             └─────────────────┘
```

### Benefits of This Approach

1. **Separation of Concerns**: Business logic vs. document generation
2. **Performance**: Optimized Go service for document processing
3. **Scalability**: Independent scaling of document generation workload
4. **Reusability**: Invoice service can serve multiple ERP modules
5. **Maintainability**: Centralized document templates and formatting

## Files Created and Modified

### 1. gRPC Client Implementation

**File:** `grpc_clients/invoice_client.py`

**Purpose:** Provides a robust gRPC client for communicating with the Invoice Service.

**Key Features:**
- Connection pooling and health monitoring
- Data normalization for cross-service compatibility
- Multiple document format support (PDF, HTML, JSON)
- Template management capabilities
- Comprehensive error handling and logging

**Key Methods:**
```python
def generate_document(invoice_data, format_type='pdf', template_id=None, options=None)
def create_template(template_data)
def list_templates(organization_id, active_only=True)
def health_check()
```

### 2. Enhanced Invoice Model

**File:** `apps/invoices/models.py`

**Modifications:**
- Added `generate_document()` method for multi-format generation
- Enhanced `generate_pdf()` method with template support
- Added `_prepare_invoice_data_for_service()` for data normalization
- Comprehensive metadata preparation for invoice service

**New Methods:**
```python
def generate_document(self, format_type='pdf', template_id=None, **options)
def generate_pdf(self, template_id=None, **options)  # Enhanced
def _prepare_invoice_data_for_service(self)
```

### 3. Enhanced Invoice Views

**File:** `apps/invoices/views.py`

**New Endpoints:**
- `POST /api/v1/invoices/{id}/generate_document/` - Multi-format document generation
- `GET /api/v1/invoices/templates/` - List available templates
- `POST /api/v1/invoices/create_template/` - Create custom templates
- `GET /api/v1/invoices/service_health/` - Check invoice service health

**Enhanced Features:**
- Support for PDF, HTML, and JSON formats
- Template selection and custom options
- Comprehensive error handling
- Backward compatibility with existing endpoints

### 4. Serializers

**File:** `apps/invoices/serializers.py`

**New Serializers:**
- `InvoiceSerializer` - Complete invoice serialization
- `InvoiceItemSerializer` - Invoice line items
- `DocumentGenerationSerializer` - Document generation requests
- `TemplateSerializer` - Template management

### 5. URL Configuration

**File:** `apps/invoices/urls.py`

**Purpose:** Defines URL routing for invoice-related endpoints using Django REST Framework routers.

### 6. Configuration Settings

**File:** `config/settings/invoice_service.py`

**Configuration Options:**
```python
INVOICE_SERVICE_HOST = 'invoice-service'
INVOICE_SERVICE_PORT = '50055'
INVOICE_SERVICE_TIMEOUT = '10s'
INVOICE_SERVICE_ENABLED = True
INVOICE_SERVICE_FALLBACK_ENABLED = True
```

### 7. Management Command

**File:** `apps/invoices/management/commands/test_invoice_service.py`

**Purpose:** Comprehensive testing tool for invoice service integration.

**Test Coverage:**
- Health check validation
- Template listing and creation
- Document generation in multiple formats
- Error handling verification

### 8. Docker Integration

**File:** `docker-compose.invoice-integration.yml`

**Purpose:** Docker Compose configuration for running sales service with invoice service integration.

**Services Included:**
- Sales service with invoice service environment variables
- Invoice service container configuration
- Network and volume management

### 9. Enhanced Makefile

**File:** `Makefile`

**New Commands:**
```bash
make test-invoice-service   # Test invoice service integration
make run-with-invoice      # Run with invoice service integration
```

### 10. Updated Dependencies

**File:** `requirements.txt`

**Added Dependencies:**
```
grpcio-health-checking==1.59.2
grpcio-reflection==1.59.2
```

## API Documentation

### Document Generation Endpoint

```http
POST /api/v1/invoices/{id}/generate_document/
Content-Type: application/json
X-Organization-ID: {organization_id}

{
    "format": "pdf",  // "pdf", "html", or "json"
    "template_id": "custom-template-id",  // Optional
    "options": {
        "include_logo": true,
        "watermark": "PAID",
        "language": "en"
    }
}
```

**Response:**
- For PDF/HTML: File download with appropriate content-type
- For JSON: Structured invoice data

### Template Management

```http
GET /api/v1/invoices/templates/
X-Organization-ID: {organization_id}

Response:
{
    "templates": [
        {
            "id": "template-123",
            "name": "Default Invoice Template",
            "description": "Standard invoice template",
            "is_default": true,
            "is_active": true
        }
    ],
    "count": 1
}
```

### Service Health Check

```http
GET /api/v1/invoices/service_health/

Response:
{
    "invoice_service_healthy": true,
    "status": "healthy"
}
```

## Environment Configuration

### Required Environment Variables

```bash
# Invoice Service Integration
INVOICE_SERVICE_HOST=invoice-service
INVOICE_SERVICE_PORT=50055
INVOICE_SERVICE_TIMEOUT=10s
INVOICE_SERVICE_ENABLED=true
INVOICE_SERVICE_FALLBACK_ENABLED=true

# Document Generation Settings
INVOICE_DEFAULT_FORMAT=pdf
INVOICE_DEFAULT_TEMPLATE=default-template
INVOICE_SERVICE_CACHE_TTL=300
```

### Docker Environment

```yaml
services:
  sales-service:
    environment:
      - INVOICE_SERVICE_HOST=invoice-service
      - INVOICE_SERVICE_PORT=50055
    depends_on:
      - invoice-service
```

## Usage Examples

### 1. Generate PDF Invoice

```python
# In Django views or models
invoice = Invoice.objects.get(id=invoice_id)
pdf_data = invoice.generate_pdf(template_id='custom-template')

# Via API
curl -X POST "http://localhost:8000/api/v1/invoices/123/generate_document/" \
  -H "Content-Type: application/json" \
  -H "X-Organization-ID: org-123" \
  -d '{"format": "pdf", "template_id": "custom-template"}'
```

### 2. Generate HTML Invoice

```python
# Generate HTML version
result = invoice.generate_document(format_type='html')
html_content = result['document_data'].decode('utf-8')
```

### 3. List Available Templates

```python
from grpc_clients.invoice_client import invoice_service_client

templates = invoice_service_client.list_templates(
    organization_id='org-123',
    active_only=True
)
```

### 4. Create Custom Template

```python
template_data = {
    'name': 'Custom Invoice Template',
    'description': 'Company-specific invoice template',
    'html_template': '<html><body>{{content}}</body></html>',
    'css_styles': 'body { font-family: Arial; }',
    'variables': {'company_name': '{{company_name}}'},
    'is_default': False
}

template_id = invoice_service_client.create_template(template_data)
```

## Testing

### Running Integration Tests

```bash
# Test the integration
make test-invoice-service

# Or run the management command directly
python manage.py test_invoice_service --invoice-id=123 --format=pdf
```

### Test Coverage

The integration includes tests for:
1. **Health Check**: Verify invoice service connectivity
2. **Template Operations**: List and create templates
3. **Document Generation**: Generate documents in all formats
4. **Error Handling**: Graceful failure scenarios
5. **Data Normalization**: Ensure data compatibility

## Deployment

### Development Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with invoice service settings

# 3. Run with invoice service
make run-with-invoice
```

### Production Deployment

```bash
# 1. Build and deploy invoice service first
cd ../invoice-service
make build
make deploy

# 2. Deploy sales service with integration
cd ../erp-sales-service
docker-compose -f docker-compose.yml -f docker-compose.invoice-integration.yml up -d
```

## Monitoring and Troubleshooting

### Health Monitoring

```bash
# Check invoice service health
curl http://localhost:8000/api/v1/invoices/service_health/

# Check invoice service directly
curl http://localhost:8085/health
```

### Logging

Invoice service integration logs are written to:
- Console output (development)
- `logs/invoice_service.log` (production)

### Common Issues and Solutions

1. **Connection Refused**
   - Verify invoice service is running
   - Check network connectivity
   - Validate gRPC port configuration

2. **Document Generation Fails**
   - Check invoice data completeness
   - Verify template exists and is valid
   - Review invoice service logs

3. **Template Not Found**
   - Ensure template exists for the organization
   - Check template ID spelling
   - Verify organization context

## Performance Considerations

### Caching Strategy

- Invoice service uses Redis for template and document caching
- Generated documents cached for 5 minutes by default
- Template metadata cached for 1 hour

### Connection Management

- gRPC connection pooling enabled
- Automatic reconnection on failures
- Health checks every 30 seconds

### Resource Usage

- Invoice service runs with 512MB memory limit
- PDF generation is CPU-intensive but fast
- Temporary files cleaned up automatically

## Security

### Data Protection

- All communication over gRPC with TLS (production)
- Organization-based data isolation
- No sensitive data logged

### Authentication

- JWT tokens validated by sales service
- Organization context passed via headers
- Service-to-service authentication (future enhancement)

## Future Enhancements

### Planned Features

1. **Email Integration**: Direct email sending of generated invoices
2. **Batch Processing**: Generate multiple invoices simultaneously
3. **Advanced Templates**: Rich template editor with preview
4. **Digital Signatures**: PDF signing capabilities
5. **Audit Trail**: Document generation tracking

### Scalability Improvements

1. **Load Balancing**: Multiple invoice service instances
2. **Async Processing**: Queue-based document generation
3. **CDN Integration**: Cached document delivery
4. **Microservice Mesh**: Service discovery and routing

## Conclusion

The invoice service integration provides the sales service with powerful document generation capabilities while maintaining clean service boundaries. The hybrid approach ensures optimal performance, scalability, and maintainability while enabling the invoice service to serve multiple ERP modules.

The integration is production-ready with comprehensive error handling, monitoring, and fallback mechanisms. It provides a solid foundation for future enhancements and can serve as a template for integrating other specialized services within the ERP suite.

---

**Next Steps:**
1. Deploy invoice service to production environment
2. Configure monitoring and alerting
3. Train team on new API endpoints
4. Plan integration with other ERP modules
5. Implement advanced features based on user feedback