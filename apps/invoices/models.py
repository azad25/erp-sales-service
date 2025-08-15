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