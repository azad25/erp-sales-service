# ERP Sales Service Makefile

.PHONY: help install migrate makemigrations run test clean docker-build docker-run docker-stop proto-generate

# Variables
PYTHON = python3
PIP = pip3
MANAGE = python manage.py
DOCKER_COMPOSE = docker-compose

# Default target
help:
	@echo "ERP Sales Service - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  install          - Install Python dependencies"
	@echo "  migrate          - Run database migrations"
	@echo "  makemigrations   - Create new migrations"
	@echo "  run              - Run development server"
	@echo "  run-grpc         - Run gRPC server"
	@echo "  test             - Run tests"
	@echo "  clean            - Clean Python cache"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-run       - Run with Docker Compose"
	@echo "  docker-stop      - Stop Docker services"
	@echo "  docker-logs      - Show Docker logs"
	@echo ""
	@echo "gRPC:"
	@echo "  proto-generate   - Generate gRPC code from proto files"
	@echo ""
	@echo "Database:"
	@echo "  db-reset         - Reset database (WARNING: deletes all data)"
	@echo "  db-backup        - Backup database"
	@echo "  db-restore       - Restore database from backup"

# Development commands
install:
	@echo "Installing Python dependencies..."
	$(PIP) install -r requirements.txt

migrate:
	@echo "Running database migrations..."
	$(MANAGE) migrate

makemigrations:
	@echo "Creating new migrations..."
	$(MANAGE) makemigrations

run:
	@echo "Starting Django development server..."
	$(MANAGE) runserver 0.0.0.0:8000

run-grpc:
	@echo "Starting gRPC server..."
	$(PYTHON) grpc_server.py

test:
	@echo "Running tests..."
	$(MANAGE) test

clean:
	@echo "Cleaning Python cache..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Docker commands
docker-build:
	@echo "Building Docker image..."
	$(DOCKER_COMPOSE) build

docker-run:
	@echo "Starting Docker services..."
	$(DOCKER_COMPOSE) up -d

docker-stop:
	@echo "Stopping Docker services..."
	$(DOCKER_COMPOSE) down

docker-logs:
	@echo "Showing Docker logs..."
	$(DOCKER_COMPOSE) logs -f

# gRPC commands
proto-generate:
	@echo "Generating gRPC code from proto files..."
	python -m grpc_tools.protoc \
		--python_out=. \
		--grpc_python_out=. \
		--proto_path=proto \
		proto/sales/sales.proto

# Database commands
db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(MANAGE) flush --no-input
	$(MANAGE) migrate

db-backup:
	@echo "Creating database backup..."
	pg_dump -h localhost -U postgres -d erp_sales > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file name: " backup_file && \
	psql -h localhost -U postgres -d erp_sales < $$backup_file

# Setup commands
setup-dev:
	@echo "Setting up development environment..."
	cp .env.example .env
	$(PIP) install -r requirements.txt
	$(MANAGE) migrate
	@echo "Development environment setup complete!"

setup-docker:
	@echo "Setting up Docker environment..."
	cp .env.example .env
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d
	@echo "Docker environment setup complete!"

# Utility commands
shell:
	@echo "Starting Django shell..."
	$(MANAGE) shell

superuser:
	@echo "Creating superuser..."
	$(MANAGE) createsuperuser

collectstatic:
	@echo "Collecting static files..."
	$(MANAGE) collectstatic --noinput

check:
	@echo "Running Django checks..."
	$(MANAGE) check

# Production commands
deploy:
	@echo "Deploying to production..."
	$(MANAGE) migrate --settings=config.settings.production
	$(MANAGE) collectstatic --noinput --settings=config.settings.production
	@echo "Deployment complete!" 