# ERP Sales Service

A Django-based microservice for sales management in the ERP Suite. This service provides comprehensive sales functionality including lead management, opportunities, quotations, invoices, customers, and products.

## Features

- **Lead Management**: Track and manage sales leads with full lifecycle support
- **Opportunity Management**: Convert leads to opportunities and track sales pipeline
- **Quotation System**: Create and manage sales quotations with line items
- **Invoice Management**: Generate invoices from quotations with payment tracking
- **Customer Management**: Maintain customer database with contact information
- **Product Catalog**: Manage product inventory and pricing
- **Sales Dashboard**: Real-time analytics and reporting
- **Multi-tenancy**: Organization-based data isolation
- **gRPC Integration**: High-performance inter-service communication
- **REST API**: Full REST API with comprehensive endpoints
- **Search & Analytics**: Elasticsearch integration for advanced search
- **Caching**: Redis-based caching for improved performance
- **Message Queue**: Kafka integration for event-driven architecture

## Technology Stack

- **Framework**: Django 4.2.7 with Django REST Framework
- **Database**: PostgreSQL (primary), MongoDB (optional)
- **Cache**: Redis
- **Search**: Elasticsearch
- **Message Queue**: Apache Kafka
- **API Documentation**: Swagger/OpenAPI
- **Authentication**: JWT tokens
- **gRPC**: Protocol Buffers for inter-service communication
- **Containerization**: Docker & Docker Compose
- **Background Tasks**: Celery

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Development Setup

1. **Clone the repository**
   ```bash
   cd sales-service
   ```

2. **Install dependencies**
   ```bash
   make install
   # or
   pip install -r requirements.txt
   ```

3. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**
   ```bash
   make migrate
   # or
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   make run
   # or
   python manage.py runserver 0.0.0.0:8000
   ```

6. **Start gRPC server (in another terminal)**
   ```bash
   make run-grpc
   # or
   python grpc_server.py
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   make setup-docker
   # or
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   make docker-logs
   # or
   docker-compose logs -f
   ```

## API Endpoints

### REST API (Port 8000)

- **Health Check**: `GET /health/`
- **API Documentation**: `GET /swagger/` or `GET /redoc/`
- **Sales Dashboard**: `GET /api/v1/dashboard/`
- **Reports**: `GET /api/v1/reports/`

#### Lead Management
- `GET /api/v1/leads/` - List leads
- `POST /api/v1/leads/` - Create lead
- `GET /api/v1/leads/{id}/` - Get lead details
- `PUT /api/v1/leads/{id}/` - Update lead
- `DELETE /api/v1/leads/{id}/` - Delete lead
- `POST /api/v1/leads/{id}/convert_to_opportunity/` - Convert to opportunity

#### Opportunity Management
- `GET /api/v1/opportunities/` - List opportunities
- `POST /api/v1/opportunities/` - Create opportunity
- `GET /api/v1/opportunities/{id}/` - Get opportunity details
- `PUT /api/v1/opportunities/{id}/` - Update opportunity
- `DELETE /api/v1/opportunities/{id}/` - Delete opportunity
- `GET /api/v1/opportunities/pipeline/` - Get pipeline data

#### Quotation Management
- `GET /api/v1/quotations/` - List quotations
- `POST /api/v1/quotations/` - Create quotation
- `GET /api/v1/quotations/{id}/` - Get quotation details
- `PUT /api/v1/quotations/{id}/` - Update quotation
- `DELETE /api/v1/quotations/{id}/` - Delete quotation
- `POST /api/v1/quotations/{id}/convert_to_invoice/` - Convert to invoice

#### Invoice Management
- `GET /api/v1/invoices/` - List invoices
- `POST /api/v1/invoices/` - Create invoice
- `GET /api/v1/invoices/{id}/` - Get invoice details
- `PUT /api/v1/invoices/{id}/` - Update invoice
- `DELETE /api/v1/invoices/{id}/` - Delete invoice
- `POST /api/v1/invoices/{id}/mark_as_paid/` - Mark as paid

#### Customer Management
- `GET /api/v1/customers/` - List customers
- `POST /api/v1/customers/` - Create customer
- `GET /api/v1/customers/{id}/` - Get customer details
- `PUT /api/v1/customers/{id}/` - Update customer
- `DELETE /api/v1/customers/{id}/` - Delete customer

#### Product Management
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/{id}/` - Get product details
- `PUT /api/v1/products/{id}/` - Update product
- `DELETE /api/v1/products/{id}/` - Delete product
- `GET /api/v1/products/low_stock/` - Get low stock products

### gRPC API (Port 50051)

The service also provides a complete gRPC interface with the following services:

- `SalesService.CreateLead` - Create a new lead
- `SalesService.GetLead` - Get lead by ID
- `SalesService.UpdateLead` - Update lead
- `SalesService.DeleteLead` - Delete lead
- `SalesService.ListLeads` - List leads with filtering
- `SalesService.CreateOpportunity` - Create opportunity
- `SalesService.GetOpportunity` - Get opportunity by ID
- `SalesService.UpdateOpportunity` - Update opportunity
- `SalesService.DeleteOpportunity` - Delete opportunity
- `SalesService.ListOpportunities` - List opportunities
- `SalesService.CreateQuotation` - Create quotation
- `SalesService.GetQuotation` - Get quotation by ID
- `SalesService.UpdateQuotation` - Update quotation
- `SalesService.DeleteQuotation` - Delete quotation
- `SalesService.ListQuotations` - List quotations
- `SalesService.CreateInvoice` - Create invoice
- `SalesService.GetInvoice` - Get invoice by ID
- `SalesService.UpdateInvoice` - Update invoice
- `SalesService.DeleteInvoice` - Delete invoice
- `SalesService.ListInvoices` - List invoices
- `SalesService.CreateCustomer` - Create customer
- `SalesService.GetCustomer` - Get customer by ID
- `SalesService.UpdateCustomer` - Update customer
- `SalesService.DeleteCustomer` - Delete customer
- `SalesService.ListCustomers` - List customers
- `SalesService.CreateProduct` - Create product
- `SalesService.GetProduct` - Get product by ID
- `SalesService.UpdateProduct` - Update product
- `SalesService.DeleteProduct` - Delete product
- `SalesService.ListProducts` - List products
- `SalesService.GetSalesDashboard` - Get dashboard data
- `SalesService.HealthCheck` - Health check

## Configuration

### Environment Variables

Key environment variables that can be configured:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=erp_sales
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redispassword
REDIS_DB=0

# Elasticsearch Settings
ELASTICSEARCH_HOST=localhost:9200

# Kafka Settings
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC_PREFIX=erp_sales

# gRPC Settings
GRPC_PORT=50051

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Multi-tenancy

The service supports multi-tenancy through organization-based data isolation. All requests must include the `X-Organization-ID` header to identify the organization context.

## Development

### Project Structure

```
sales-service/
├── apps/                    # Django applications
│   ├── leads/              # Lead management
│   ├── opportunities/      # Opportunity management
│   ├── quotations/         # Quotation management
│   ├── invoices/           # Invoice management
│   ├── customers/          # Customer management
│   ├── products/           # Product management
│   ├── payments/           # Payment management
│   └── reports/            # Reporting
├── config/                 # Django configuration
│   ├── settings/           # Settings files
│   └── urls/               # URL configuration
├── core/                   # Core functionality
├── api/                    # REST API
├── proto/                  # Protocol Buffer definitions
├── grpc_services.py        # gRPC service implementation
├── grpc_server.py          # gRPC server
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── Makefile                # Development commands
└── README.md               # This file
```

### Available Commands

```bash
# Development
make install                # Install dependencies
make migrate                # Run migrations
make makemigrations         # Create migrations
make run                    # Start development server
make run-grpc               # Start gRPC server
make test                   # Run tests
make clean                  # Clean cache

# Docker
make docker-build           # Build Docker image
make docker-run             # Start Docker services
make docker-stop            # Stop Docker services
make docker-logs            # Show Docker logs

# gRPC
make proto-generate         # Generate gRPC code

# Database
make db-reset               # Reset database
make db-backup              # Backup database
make db-restore             # Restore database

# Setup
make setup-dev              # Setup development environment
make setup-docker           # Setup Docker environment

# Utility
make shell                  # Django shell
make superuser              # Create superuser
make collectstatic          # Collect static files
make check                  # Django checks
make deploy                 # Deploy to production
```

### Testing

```bash
# Run all tests
make test

# Run specific test
python manage.py test apps.leads.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Run all quality checks
pre-commit run --all-files
```

## Integration with ERP Suite

### API Gateway Integration

The sales service integrates with the ERP API Gateway through:

1. **gRPC Communication**: The API Gateway communicates with the sales service via gRPC for internal operations
2. **REST API**: External clients can access the sales service directly via REST API
3. **Authentication**: JWT tokens are validated through the auth service
4. **Multi-tenancy**: Organization context is passed through headers

### Event Publishing

The service publishes events to Kafka for:

- Lead creation/updates
- Opportunity stage changes
- Quotation status changes
- Invoice payments
- Customer updates

### Data Flow

1. **Frontend** → **API Gateway** → **Sales Service** (gRPC)
2. **Frontend** → **Sales Service** (REST API)
3. **Sales Service** → **Kafka** → **Other Services**
4. **Sales Service** → **Elasticsearch** (for search)
5. **Sales Service** → **Redis** (for caching)

## Monitoring & Logging

### Health Checks

- **HTTP**: `GET /health/`
- **gRPC**: `SalesService.HealthCheck`

### Logging

Logs are written to:
- Console (development)
- File: `logs/django.log`
- Structured logging with correlation IDs

### Metrics

The service exposes metrics for:
- Request counts and response times
- Database query performance
- Cache hit rates
- Business metrics (leads, opportunities, revenue)

## Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.production
   ```

2. **Database Migration**
   ```bash
   python manage.py migrate --settings=config.settings.production
   ```

3. **Static Files**
   ```bash
   python manage.py collectstatic --noinput --settings=config.settings.production
   ```

4. **Start Services**
   ```bash
   # Start Django with Gunicorn
   gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
   
   # Start gRPC server
   python grpc_server.py
   ```

### Docker Deployment

```bash
# Build and run
docker-compose -f docker-compose.yml up -d

# Scale services
docker-compose up -d --scale sales-service=3
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

This project is part of the ERP Suite and is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Changelog

### Version 1.0.0
- Initial release
- Complete sales management functionality
- gRPC and REST API support
- Multi-tenancy support
- Docker containerization
- Comprehensive documentation 