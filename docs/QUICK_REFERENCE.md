# ERP Sales Service - Quick Reference

**Last Updated:** January 16, 2025

## Quick Commands

```bash
# Setup
make install && make migrate && make run

# Development
make run                    # Start Django server (port 8000)
make run-grpc              # Start gRPC server (port 50051)
make test                  # Run all tests
make clean                 # Clean Python cache

# Database
make migrate               # Apply migrations
make makemigrations        # Create new migrations
python manage.py shell     # Django shell

# Docker
make docker-run            # Start all services
make run-with-invoice      # Start with invoice service integration

# Code Quality
black . && isort . && flake8 .
```

## Project Structure Cheat Sheet

```
erp-sales-service/
├── apps/                  # Business logic
│   ├── leads/            # Lead management
│   ├── opportunities/    # Sales pipeline
│   ├── quotations/       # Quote system
│   ├── invoices/         # Invoice management
│   ├── customers/        # Customer database
│   ├── products/         # Product catalog
│   └── reports/          # Analytics
├── config/               # Django settings
├── core/                 # Shared utilities
├── grpc_clients/         # External service clients
└── docs/                 # Documentation
```

## Common API Patterns

### Standard CRUD Endpoints
```
GET    /api/v1/{resource}/           # List
POST   /api/v1/{resource}/           # Create
GET    /api/v1/{resource}/{id}/      # Retrieve
PUT    /api/v1/{resource}/{id}/      # Update
DELETE /api/v1/{resource}/{id}/      # Delete
```

### Required Headers
```http
X-Organization-ID: {uuid}
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

## Model Patterns

### Base Model (All models inherit from this)
```python
class YourModel(OrganizationModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'your_table'
        verbose_name = 'Your Model'
```

### ViewSet Pattern
```python
class YourModelViewSet(viewsets.ModelViewSet):
    serializer_class = YourModelSerializer
    permission_classes = [IsAuthenticated, OrganizationPermission]
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        org_id = self.request.headers.get('X-Organization-ID')
        return YourModel.objects.filter(
            organization_id=org_id,
            is_active=True
        )
```

## Environment Variables

```bash
# Core Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_sales
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Invoice Service Integration
INVOICE_SERVICE_HOST=invoice-service
INVOICE_SERVICE_PORT=50055
```

## Testing Patterns

### Model Test
```python
class YourModelTest(TestCase):
    def setUp(self):
        self.org_id = uuid.uuid4()
        
    def test_model_creation(self):
        obj = YourModel.objects.create(
            organization_id=self.org_id,
            name="Test"
        )
        self.assertEqual(obj.name, "Test")
```

### API Test
```python
class YourViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.org_id = str(uuid.uuid4())
        
    def test_create_endpoint(self):
        data = {"name": "Test"}
        response = self.client.post(
            '/api/v1/your-endpoint/',
            data,
            HTTP_X_ORGANIZATION_ID=self.org_id
        )
        self.assertEqual(response.status_code, 201)
```

## Database Queries

### Common Query Patterns
```python
# Filter by organization
Model.objects.filter(organization_id=org_id, is_active=True)

# With related data
Model.objects.select_related('customer').prefetch_related('items')

# Aggregation
Model.objects.aggregate(total=Sum('amount'))

# Annotations
Model.objects.annotate(item_count=Count('items'))
```

## gRPC Integration

### Client Usage
```python
from grpc_clients.invoice_client import invoice_service_client

# Generate document
result = invoice_service_client.generate_document(
    invoice_data=data,
    format_type='pdf'
)

# Health check
is_healthy = invoice_service_client.health_check()
```

## Debugging

### Enable Debug Logging
```python
# In settings
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Django Shell Helpers
```python
# In Django shell
from apps.leads.models import Lead
from django.contrib.auth.models import User

# Query examples
leads = Lead.objects.filter(organization_id='your-org-id')
lead = Lead.objects.get(id='lead-id')

# Create test data
lead = Lead.objects.create(
    organization_id='test-org',
    first_name='John',
    last_name='Doe',
    email='john@example.com'
)
```

## Common Issues & Solutions

### Database Connection Error
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Reset database
make db-reset
```

### Redis Connection Error
```bash
# Check Redis
redis-cli ping

# Should return PONG
```

### Migration Issues
```bash
# Reset migrations (development only)
rm apps/*/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

### gRPC Connection Issues
```bash
# Test gRPC server
grpcurl -plaintext localhost:50051 list

# Check if port is in use
lsof -i :50051
```

## Performance Tips

### Database Optimization
```python
# Use select_related for ForeignKey
queryset.select_related('customer', 'product')

# Use prefetch_related for ManyToMany
queryset.prefetch_related('items', 'tags')

# Add indexes to models
class Meta:
    indexes = [
        models.Index(fields=['status']),
        models.Index(fields=['created_at']),
    ]
```

### API Optimization
```python
# Pagination
class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# Filtering
filterset_fields = ['status', 'assigned_to']
search_fields = ['name', 'email']
ordering_fields = ['created_at', 'updated_at']
```

## Useful URLs

### Development
- Django Admin: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/swagger/
- API Root: http://localhost:8000/api/v1/

### Health Checks
- Django Health: http://localhost:8000/health/
- Invoice Service Health: http://localhost:8000/api/v1/invoices/service_health/

## File Locations

### Key Configuration Files
- Main settings: `config/settings/base.py`
- URL routing: `config/urls.py`
- Environment: `.env`
- Dependencies: `requirements.txt`

### App Structure (Example: leads)
- Models: `apps/leads/models.py`
- Views: `apps/leads/views.py`
- Serializers: `apps/leads/serializers.py`
- URLs: `apps/leads/urls.py`
- Tests: `apps/leads/tests/`

### Integration Files
- gRPC Client: `grpc_clients/invoice_client.py`
- gRPC Services: `grpc_services.py`
- Docker Compose: `docker-compose.yml`

## Next Steps for New Developers

1. **Setup Development Environment**
   ```bash
   make setup-dev
   ```

2. **Explore the API**
   - Visit http://localhost:8000/swagger/
   - Test endpoints with Postman or curl

3. **Run Tests**
   ```bash
   make test
   ```

4. **Read Full Documentation**
   - `docs/DEVELOPER_GUIDE.md` - Complete development guide
   - `docs/INVOICE_SERVICE_INTEGRATION_2025-01-16.md` - Invoice integration

5. **Start Development**
   - Pick an app (leads, opportunities, etc.)
   - Follow the patterns in existing code
   - Write tests for new features

---

For detailed information, see the complete [Developer Guide](DEVELOPER_GUIDE.md).