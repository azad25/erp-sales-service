"""
Quotation models for ERP Sales Service
"""
from django.db import models
from core.models import OrganizationModel


class Quotation(OrganizationModel):
    """Quotation model for sales quotations"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    opportunity = models.ForeignKey('opportunities.Opportunity', on_delete=models.CASCADE, related_name='quotations')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='quotations')
    quotation_number = models.CharField(max_length=50, unique=True)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    valid_until = models.DateField()
    terms_conditions = models.TextField(blank=True)
    assigned_to = models.CharField(max_length=100, blank=True)  # User ID

    class Meta:
        db_table = 'quotations'
        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotations'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['quotation_number']),
            models.Index(fields=['valid_until']),
        ]

    def __str__(self):
        return f"{self.quotation_number} - {self.subject}"

    def save(self, *args, **kwargs):
        # Auto-generate quotation number if not provided
        if not self.quotation_number:
            last_quotation = Quotation.objects.filter(
                organization_id=self.organization_id
            ).order_by('-quotation_number').first()
            
            if last_quotation:
                try:
                    last_number = int(last_quotation.quotation_number.split('-')[-1])
                    self.quotation_number = f"QT-{self.organization_id[:8]}-{last_number + 1:06d}"
                except (ValueError, IndexError):
                    self.quotation_number = f"QT-{self.organization_id[:8]}-000001"
            else:
                self.quotation_number = f"QT-{self.organization_id[:8]}-000001"
        
        super().save(*args, **kwargs)

    @property
    def customer_name(self):
        return self.customer.full_name if self.customer else ""

    @property
    def opportunity_name(self):
        return self.opportunity.name if self.opportunity else ""


class QuotationItem(OrganizationModel):
    """Quotation item model for line items in quotations"""
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='quotation_items')
    description = models.TextField(blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        db_table = 'quotation_items'
        verbose_name = 'Quotation Item'
        verbose_name_plural = 'Quotation Items'

    def __str__(self):
        return f"{self.quotation.quotation_number} - {self.product.name}"

    def save(self, *args, **kwargs):
        # Calculate total
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount_percent / 100)
        self.total = subtotal - discount_amount
        super().save(*args, **kwargs)

    @property
    def product_name(self):
        return self.product.name if self.product else "" 