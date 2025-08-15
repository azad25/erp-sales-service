"""
Product models for ERP Sales Service
"""
from django.db import models
from core.models import OrganizationModel


class Product(OrganizationModel):
    """Product model for sales products"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    stock_quantity = models.IntegerField(default=0)
    min_stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=20, default='piece')  # piece, kg, liter, etc.

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} - {self.sku}"

    @property
    def stock_status(self):
        if self.stock_quantity <= 0:
            return "out_of_stock"
        elif self.stock_quantity <= self.min_stock:
            return "low_stock"
        else:
            return "in_stock" 