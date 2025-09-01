# ERP Sales Service - Developer Guide

**Version:** 1.0  
**Last Updated:** January 16, 2025  
**Framework:** Django 4.2.7 + Django REST Framework  

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Development Setup](#development-setup)
5. [Core Concepts](#core-concepts)
6. [Database Models](#database-models)
7. [API Endpoints](#api-endpoints)
8. [gRPC Services](#grpc-services)
9. [Integration Points](#integration-points)
10. [Development Workflow](#development-workflow)
11. [Testing](#testing)
12. [Deployment](#deployment)
13. [Troubleshooting](#troubleshooting)

## Overview

The ERP Sales Service is a Django-based microservice that manages the complete sales lifecycle including leads, opportunities, quotations, invoices, customers, and products. It provides both REST and gRPC APIs and integrates with other ERP services.

### Key Features

- **Lead Management**: Track and nurture sales leads
- **Opportunity Pipeline**: Manage sales opportunities through stages
- **Quotation System**: Create and manage sales quotes
- **Invoice Management**: Generate and track invoices
- **Customer Database**: Maintain customer relationships
- **Product Catalog**: Manage product inventory and pricing
- **Multi-tenancy**: Organization-based data isolation
- **Real-time Analytics**: Sales dashboard and reporting

## Architecture

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ERP Sales Service                        │
├─────────────────────────────────────────────────────────────┤
│  REST API (Port 8000)     │     gRPC API (Port 50051)      │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                     │
│  • Lead Service    • Opportunity Service   • Invoice Svc    │
│  • Customer Svc    • Product Service      • Report Svc     │
├─────────────────────────────────────────────────────────────┤
│                    Data Access Layer                        │
│  • Django ORM     • Repository Pattern    • Caching        │
├─────────────────────────────────────────────────────────────┤
│                    External Integrations                    │
│  • PostgreSQL     • Redis Cache          • Elasticsearch   │
│  • Kafka Events   • Invoice Service      • Auth Service    │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: PostgreSQL (primary), MongoDB (optional)
- **Cache**: Redis 5.0.1
- **Search**: Elasticsearch 7.17.9
- **Message Queue**: Apache Kafka
- **gRPC**: grpcio 1.59.2
- **Authentication**: JWT tokens
- **Documentation**: drf-yasg (Swagger/OpenAPI)

## Project Structure

```
erp-sales-service/
├── apps/                           # Django applications
│   ├── leads/                      # Lead management
│   │   ├── models.py              # Lead data models
│   │   ├── views.py               # Lead API views
│   │   ├── serializers.py         # Lead serializers
│   │   └── urls.py                # Lead URL routing
│   ├── opportunities/              # Opportunity management
│   ├── quotations/                 # Quotation system
│   ├── invoices/                   # Invoice management
│   │   ├── models.py              # Invoice models
│   │   ├── views.py               # Invoice API views
│   │   ├── serializers.py         # Invoice serializers
│   │   └── management/commands/    # Management commands
│   ├── customers/                  # Customer management
│   ├── products/                   # Product catalog
│   ├── payments/                   # Payment processing
│   └── reports/                    # Analytics and reporting
├── config/                         # Django configuration
│   ├── settings/                   # Environment-specific settings
│   │   ├── base.py                # Base settings
│   │   ├── development.py         # Development settings
│   │   ├── production.py          # Production settings
│   │   └── invoice_service.py     # Invoice service integration
│   ├── urls/                       # URL configuration
│   └── wsgi.py                     # WSGI application
├── core/                           # Core functionality
│   ├── models.py                   # Base models (OrganizationModel)
│   ├── permissions.py              # Custom permissions
│   ├── pagination.py               # Custom pagination
│   └── utils.py                    # Utility functions
├── api/                            # REST API configuration
│   ├── v1/                         # API version 1
│   └── serializers.py              # Common serializers
├── grpc_clients/                   # gRPC client implementations
│   └── invoice_client.py           # Invoice service client
├── proto/                          # Protocol Buffer definitions
│   └── sales/                      # Sales service protobuf
├── docs/                           # Documentation
├── logs/                           # Log files
├── grpc_services.py                # gRPC service implementation
├── grpc_server.py                  # gRPC server
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose
└── Makefile                        # Development commands
```

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Quick Start

1. **Clone and Setup Environment**
   ```bash
   cd erp-sales-service
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install Dependencies**
   ```bash
   make install
   # or
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   make migrate
   # or
   python manage.py migrate
   ```

4. **Run Development Server**
   ```bash
   make run
   # or
   python manage.py runserver 0.0.0.0:8000
   ```

5. **Run gRPC Server (separate terminal)**
   ```bash
   make run-grpc
   # or
   python grpc_server.py
   ```

### Docker Setup

```bash
# Build and run with Docker
make setup-docker
# or
docker-compose up -d
```

## Core Concepts

### 1. Multi-tenancy

All models inherit from `OrganizationModel` which provides organization-based isolation:

```python
# core/models.py
class OrganizationModel(models.Model):
    organization_id = models.UUIDField(db_index=True)
    organization_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)

    class Meta:
        abstract = True
```

### 2. Sales Lifecycle

The sales process follows this flow:

```
Lead → Opportunity → Quotation → Invoice → Payment
```

Each stage has its own app with dedicated models, views, and business logic.

### 3. API Design Patterns

- **ViewSets**: Use Django REST Framework ViewSets for CRUD operations
- **Serializers**: Separate serializers for create, update, and read operations
- **Permissions**: Organization-based permissions with JWT authentication
- **Pagination**: Custom pagination for large datasets
- **Filtering**: Django-filter integration for advanced filtering

## Database Models

### Lead Model

```python
# apps/leads/models.py
class Lead(OrganizationModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, default='new')
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    description = models.TextField(blank=True)
    assigned_to = models.CharField(max_length=100, blank=True)
```

### Opportunity Model

```python
# apps/opportunities/models.py
class Opportunity(OrganizationModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    stage = models.CharField(max_length=50, default='qualification')
    probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    expected_close_date = models.DateField()
    assigned_to = models.CharField(max_length=100, blank=True)
```

### Invoice Model

```python
# apps/invoices/models.py
class Invoice(OrganizationModel):
    quotation = models.ForeignKey('quotations.Quotation', on_delete=models.CASCADE)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    subject = models.CharField(max_length=200)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='draft')
    due_date = models.DateField()
    
    def generate_document(self, format_type='pdf', template_id=None, **options):
        """Generate document using Invoice Service"""
        # Implementation details in invoice integration docs
```

## API Endpoints

### REST API Structure

All REST endpoints follow this pattern:
```
/api/v1/{resource}/
```

### Lead Endpoints

```http
GET    /api/v1/leads/                    # List leads
POST   /api/v1/leads/                    # Create lead
GET    /api/v1/leads/{id}/               # Get lead
PUT    /api/v1/leads/{id}/               # Update lead
DELETE /api/v1/leads/{id}/               # Delete lead
POST   /api/v1/leads/{id}/convert_to_opportunity/  # Convert to opportunity
```

### Invoice Endpoints

```http
GET    /api/v1/invoices/                 # List invoices
POST   /api/v1/invoices/                 # Create invoice
GET    /api/v1/invoices/{id}/            # Get invoice
PUT    /api/v1/invoices/{id}/            # Update invoice
DELETE /api/v1/invoices/{id}/            # Delete invoice
POST   /api/v1/invoices/{id}/generate_document/  # Generate PDF/HTML
POST   /api/v1/invoices/{id}/mark_as_paid/       # Mark as paid
GET    /api/v1/invoices/templates/       # List templates
POST   /api/v1/invoices/create_template/ # Create template
```

### Request/Response Examples

**Create Lead:**
```http
POST /api/v1/leads/
Content-Type: application/json
X-Organization-ID: 123e4567-e89b-12d3-a456-426614174000

{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "company": "Acme Corp",
    "source": "website",
    "estimated_value": 50000.00
}
```

**Response:**
```json
{
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "company": "Acme Corp",
    "status": "new",
    "created_at": "2025-01-16T10:30:00Z"
}
```

## gRPC Services

### Service Definition

```python
# grpc_services.py
class SalesServiceServicer:
    def CreateLead(self, request, context):
        """Create a new lead via gRPC"""
        
    def GetLead(self, request, context):
        """Get lead by ID via gRPC"""
        
    def ListLeads(self, request, context):
        """List leads with filtering via gRPC"""
```

### Running gRPC Server

```bash
# Start gRPC server
python grpc_server.py

# Test gRPC endpoints
grpcurl -plaintext localhost:50051 list
```

## Integration Points

### 1. Invoice Service Integration

The sales service integrates with a dedicated invoice service for document generation:

```python
# Usage example
from grpc_clients.invoice_client import invoice_service_client

# Generate PDF
invoice = Invoice.objects.get(id=invoice_id)
pdf_data = invoice.generate_pdf(template_id='custom-template')

# List templates
templates = invoice_service_client.list_templates(organization_id)
```

### 2. Authentication Service

JWT tokens are validated for all API requests:

```python
# Headers required for all requests
X-Organization-ID: {organization_uuid}
Authorization: Bearer {jwt_token}
```

### 3. Event Publishing

The service publishes events to Kafka for other services:

```python
# Example event publishing
def publish_lead_created_event(lead):
    event_data = {
        'event_type': 'lead_created',
        'lead_id': str(lead.id),
        'organization_id': str(lead.organization_id),
        'timestamp': timezone.now().isoformat()
    }
    # Publish to Kafka topic
```

## Development Workflow

### 1. Adding New Features

1. **Create/Update Models**
   ```bash
   # Edit models in apps/{app_name}/models.py
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create Serializers**
   ```python
   # apps/{app_name}/serializers.py
   class NewFeatureSerializer(serializers.ModelSerializer):
       class Meta:
           model = NewFeature
           fields = '__all__'
   ```

3. **Create Views**
   ```python
   # apps/{app_name}/views.py
   class NewFeatureViewSet(viewsets.ModelViewSet):
       serializer_class = NewFeatureSerializer
       permission_classes = [IsAuthenticated, OrganizationPermission]
   ```

4. **Add URLs**
   ```python
   # apps/{app_name}/urls.py
   router.register(r'new-features', NewFeatureViewSet)
   ```

### 2. Testing New Features

```bash
# Run tests
make test

# Run specific app tests
python manage.py test apps.leads

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### 3. Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

## Testing

### Test Structure

```
apps/{app_name}/tests/
├── test_models.py          # Model tests
├── test_views.py           # API endpoint tests
├── test_serializers.py     # Serializer tests
└── test_integration.py     # Integration tests
```

### Example Test

```python
# apps/leads/tests/test_views.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class LeadViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.organization_id = "123e4567-e89b-12d3-a456-426614174000"
        
    def test_create_lead(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com'
        }
        response = self.client.post(
            '/api/v1/leads/',
            data,
            HTTP_X_ORGANIZATION_ID=self.organization_id
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

### Running Tests

```bash
# All tests
make test

# Specific app
python manage.py test apps.leads

# With coverage
coverage run manage.py test
coverage html  # Generate HTML report
```

## Deployment

### Environment Configuration

```bash
# .env file
DEBUG=False
SECRET_KEY=your-production-secret-key
DB_HOST=production-db-host
REDIS_HOST=production-redis-host
ALLOWED_HOSTS=your-domain.com
```

### Docker Deployment

```bash
# Build production image
docker build -t erp-sales-service:latest .

# Run with docker-compose
docker-compose -f docker-compose.yml up -d
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure Elasticsearch
- [ ] Set up Kafka for events
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure SSL/TLS
- [ ] Set up backup strategy

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database connectivity
   python manage.py dbshell
   
   # Run migrations
   python manage.py migrate
   ```

2. **Redis Connection Issues**
   ```bash
   # Test Redis connection
   redis-cli ping
   
   # Check Redis configuration in settings
   ```

3. **gRPC Service Issues**
   ```bash
   # Check if gRPC server is running
   grpcurl -plaintext localhost:50051 list
   
   # Check gRPC logs
   tail -f logs/grpc.log
   ```

4. **Invoice Service Integration Issues**
   ```bash
   # Test invoice service health
   python manage.py test_invoice_service
   
   # Check invoice service connectivity
   curl http://localhost:8085/health
   ```

### Debugging Tips

1. **Enable Debug Logging**
   ```python
   # settings/development.py
   LOGGING = {
       'version': 1,
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
           },
       },
       'loggers': {
           'django': {
               'handlers': ['console'],
               'level': 'DEBUG',
           },
       },
   }
   ```

2. **Use Django Debug Toolbar**
   ```bash
   pip install django-debug-toolbar
   # Add to INSTALLED_APPS and middleware
   ```

3. **Database Query Debugging**
   ```python
   # Enable query logging
   LOGGING['loggers']['django.db.backends'] = {
       'handlers': ['console'],
       'level': 'DEBUG',
   }
   ```

### Performance Optimization

1. **Database Optimization**
   - Use `select_related()` for foreign keys
   - Use `prefetch_related()` for many-to-many relationships
   - Add database indexes for frequently queried fields

2. **Caching Strategy**
   - Cache frequently accessed data in Redis
   - Use Django's cache framework
   - Implement cache invalidation strategies

3. **API Optimization**
   - Implement pagination for large datasets
   - Use serializer optimization techniques
   - Add API rate limiting

## Useful Commands

```bash
# Development
make install                # Install dependencies
make run                    # Start development server
make run-grpc              # Start gRPC server
make test                  # Run tests
make clean                 # Clean cache

# Database
make migrate               # Run migrations
make makemigrations        # Create migrations
make db-reset             # Reset database

# Docker
make docker-build         # Build Docker image
make docker-run           # Start Docker services
make docker-stop          # Stop Docker services

# Invoice Service Integration
make test-invoice-service # Test invoice integration
make run-with-invoice     # Run with invoice service

# Code Quality
black .                   # Format code
isort .                   # Sort imports
flake8 .                  # Lint code
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

---

This developer guide provides a comprehensive overview of the ERP Sales Service codebase. For specific integration details, refer to the `INVOICE_SERVICE_INTEGRATION_2025-01-16.md` document.