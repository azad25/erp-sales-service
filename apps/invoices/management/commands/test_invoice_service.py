"""
Management command to test Invoice Service integration
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.invoices.models import Invoice
from grpc_clients.invoice_client import invoice_service_client


class Command(BaseCommand):
    help = 'Test Invoice Service integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--invoice-id',
            type=str,
            help='Invoice ID to test document generation',
        )
        parser.add_argument(
            '--format',
            type=str,
            default='pdf',
            choices=['pdf', 'html', 'json'],
            help='Document format to generate',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Testing Invoice Service integration...')
        )

        # Test health check
        self.stdout.write('1. Testing health check...')
        is_healthy = invoice_service_client.health_check()
        if is_healthy:
            self.stdout.write(
                self.style.SUCCESS('✓ Invoice Service is healthy')
            )
        else:
            self.stdout.write(
                self.style.ERROR('✗ Invoice Service is not healthy')
            )
            return

        # Test template listing
        self.stdout.write('2. Testing template listing...')
        try:
            templates = invoice_service_client.list_templates(
                organization_id='test-org',
                active_only=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Found {len(templates)} templates')
            )
            for template in templates:
                self.stdout.write(f'  - {template.get("name", "Unknown")}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error listing templates: {e}')
            )

        # Test document generation
        if options['invoice_id']:
            self.stdout.write(f'3. Testing document generation for invoice {options["invoice_id"]}...')
            try:
                invoice = Invoice.objects.get(id=options['invoice_id'])
                result = invoice.generate_document(format_type=options['format'])
                
                if result:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Generated {options["format"]} document '
                            f'({result.get("file_size", 0)} bytes)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('✗ Failed to generate document')
                    )
            except Invoice.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ Invoice {options["invoice_id"]} not found')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error generating document: {e}')
                )
        else:
            self.stdout.write('3. Skipping document generation (no invoice ID provided)')

        # Test template creation
        self.stdout.write('4. Testing template creation...')
        try:
            template_data = {
                'organization_id': 'test-org',
                'name': f'Test Template {timezone.now().strftime("%Y%m%d_%H%M%S")}',
                'description': 'Test template created by management command',
                'html_template': '<html><body><h1>{{title}}</h1><p>{{description}}</p></body></html>',
                'css_styles': 'body { font-family: Arial, sans-serif; }',
                'variables': {'title': 'Invoice Title', 'description': 'Invoice Description'},
                'is_default': False
            }
            
            template_id = invoice_service_client.create_template(template_data)
            if template_id:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created template with ID: {template_id}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Failed to create template')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating template: {e}')
            )

        self.stdout.write(
            self.style.SUCCESS('Invoice Service integration test completed!')
        )