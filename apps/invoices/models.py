"""
Invoice models for ERP Sales Service
"""
from django.db import models
from core.models import OrganizationModel


class Invoice(OrganizationModel):
    """Invoice model for sales invoices"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    quotation = models.ForeignKey('quotations.Quotation', on_delete=models.CASCADE, related_name='invoices')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    terms_conditions = models.TextField(blank=True)
    assigned_to = models.CharField(max_length=100, blank=True)  # User ID

    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['due_date']),
            models.Index(fields=['paid_date']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.subject}"

    def save(self, *args, **kwargs):
        # Auto-generate invoice number if not provided
        if not self.invoice_number:
            last_invoice = Invoice.objects.filter(
                organization_id=self.organization_id
            ).order_by('-invoice_number').first()
            
            if last_invoice:
                try:
                    last_number = int(last_invoice.invoice_number.split('-')[-1])
                    self.invoice_number = f"INV-{self.organization_id[:8]}-{last_number + 1:06d}"
                except (ValueError, IndexError):
                    self.invoice_number = f"INV-{self.organization_id[:8]}-000001"
            else:
                self.invoice_number = f"INV-{self.organization_id[:8]}-000001"
        
        super().save(*args, **kwargs)

    @property
    def customer_name(self):
        return self.customer.full_name if self.customer else ""

    @property
    def quotation_number(self):
        return self.quotation.quotation_number if self.quotation else ""
    
    def generate_document(self, format_type: str = 'pdf', template_id: str = None, **options) -> dict:
        """
        Generate document using the Invoice Service
        
        Args:
            format_type: 'pdf', 'html', or 'json'
            template_id: Optional template ID for custom formatting
            **options: Additional generation options
            
        Returns:
            Dictionary with document data and metadata
        """
        from grpc_clients.invoice_client import invoice_service_client
        
        # Prepare comprehensive invoice data for the invoice service
        invoice_data = self._prepare_invoice_data_for_service()
        
        # Generate document using the shared invoice service
        result = invoice_service_client.generate_document(
            invoice_data=invoice_data,
            format_type=format_type,
            template_id=template_id,
            options=options
        )
        
        return result
    
    def generate_pdf(self, template_id: str = None, **options) -> bytes:
        """
        Generate PDF using the Invoice Service (backward compatibility)
        
        Args:
            template_id: Optional template ID for custom formatting
            **options: Additional generation options
            
        Returns:
            PDF bytes or None if generation fails
        """
        result = self.generate_document('pdf', template_id, **options)
        return result.get('document_data') if result else None
    
    def _prepare_invoice_data_for_service(self) -> dict:
        """
        Prepare comprehensive invoice data for the invoice service
        
        Returns:
            Dictionary with all invoice data needed for document generation
        """
        # Get customer address data safely
        customer_address = {}
        if hasattr(self.customer, 'address'):
            customer_address = {
                'street': getattr(self.customer, 'address', ''),
                'city': getattr(self.customer, 'city', ''),
                'state': getattr(self.customer, 'state', ''),
                'postal_code': getattr(self.customer, 'postal_code', ''),
                'country': getattr(self.customer, 'country', ''),
            }
        
        return {
            'id': str(self.id),
            'organization_id': str(self.organization_id),
            'invoice_number': self.invoice_number,
            'title': self.subject,
            'description': self.description,
            'status': self.status,
            'customer': {
                'id': str(self.customer.id) if self.customer else '',
                'name': self.customer.full_name if self.customer else '',
                'email': self.customer.email if self.customer else '',
                'phone': getattr(self.customer, 'phone', ''),
                'billing_address': customer_address,
                'shipping_address': customer_address,  # Use same address for now
                'tax_id': getattr(self.customer, 'tax_id', ''),
            },
            'items': [
                {
                    'id': str(item.id),
                    'name': item.product.name if item.product else 'Unknown Product',
                    'description': item.description or '',
                    'quantity': float(item.quantity),
                    'unit_price': float(item.unit_price),
                    'discount_rate': float(item.discount_percent / 100) if item.discount_percent else 0.0,
                    'tax_rate': 0.0,  # Add tax rate field to InvoiceItem model if needed
                    'total': float(item.total),
                    'metadata': {}
                }
                for item in self.items.all()
            ],
            'subtotal': float(self.subtotal),
            'tax_rate': 0.0,  # Add tax rate field to Invoice model if needed
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'currency': 'USD',  # Add currency field to Invoice model if needed
            'issue_date': self.created_at.isoformat(),
            'due_date': self.due_date.isoformat(),
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'notes': self.terms_conditions or '',
            'metadata': {
                'quotation_id': str(self.quotation.id) if self.quotation else None,
                'quotation_number': self.quotation_number,
                'assigned_to': self.assigned_to,
                'source_service': 'sales-service'
            }
        }


class InvoiceItem(OrganizationModel):
    """Invoice item model for line items in invoices"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='invoice_items')
    description = models.TextField(blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        db_table = 'invoice_items'
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product.name}"

    def save(self, *args, **kwargs):
        # Calculate total
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount_percent / 100)
        self.total = subtotal - discount_amount
        super().save(*args, **kwargs)

    @property
    def product_name(self):
        return self.product.name if self.product else "" 