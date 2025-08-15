"""
Customer models for ERP Sales Service
"""
from django.db import models
from core.models import OrganizationModel


class Customer(OrganizationModel):
    """Customer model for sales customers"""
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('government', 'Government'),
        ('non_profit', 'Non-Profit'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')

    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        indexes = [
            models.Index(fields=['customer_type']),
            models.Index(fields=['email']),
            models.Index(fields=['company']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() 