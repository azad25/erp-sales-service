"""
Serializers for ERP Sales Service API
"""
from rest_framework import serializers
from django.db import models

from core.models import OrganizationModel
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.quotations.models import Quotation, QuotationItem
from apps.invoices.models import Invoice, InvoiceItem
from apps.customers.models import Customer
from apps.products.models import Product


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for Lead model"""
    full_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id', 'organization_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'company', 'position', 'source', 'status',
            'estimated_value', 'description', 'assigned_to', 'created_at',
            'updated_at', 'is_active', 'created_by_name', 'updated_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name', 'updated_by_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return ""

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return ""


class OpportunitySerializer(serializers.ModelSerializer):
    """Serializer for Opportunity model"""
    lead_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id', 'organization_id', 'lead_id', 'lead_name', 'name', 'description',
            'amount', 'stage', 'probability', 'expected_close_date', 'assigned_to',
            'created_at', 'updated_at', 'is_active', 'created_by_name', 'updated_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name', 'updated_by_name']

    def get_lead_name(self, obj):
        if obj.lead:
            return f"{obj.lead.first_name} {obj.lead.last_name}".strip()
        return ""

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return ""

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return ""


class QuotationItemSerializer(serializers.ModelSerializer):
    """Serializer for QuotationItem model"""
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = QuotationItem
        fields = [
            'id', 'product_id', 'product_name', 'description', 'quantity',
            'unit_price', 'discount_percent', 'total'
        ]
        read_only_fields = ['id', 'total']

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return ""

    def validate(self, data):
        """Validate quotation item data"""
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        
        if data.get('unit_price', 0) < 0:
            raise serializers.ValidationError("Unit price cannot be negative")
        
        return data


class QuotationSerializer(serializers.ModelSerializer):
    """Serializer for Quotation model"""
    items = QuotationItemSerializer(many=True, read_only=True)
    customer_name = serializers.SerializerMethodField()
    opportunity_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = [
            'id', 'organization_id', 'opportunity_id', 'opportunity_name',
            'customer_id', 'customer_name', 'quotation_number', 'subject',
            'description', 'items', 'subtotal', 'tax_amount', 'discount_amount',
            'total_amount', 'status', 'valid_until', 'terms_conditions',
            'assigned_to', 'created_at', 'updated_at', 'is_active',
            'created_by_name', 'updated_by_name'
        ]
        read_only_fields = [
            'id', 'quotation_number', 'subtotal', 'total_amount', 'created_at',
            'updated_at', 'created_by_name', 'updated_by_name'
        ]

    def get_customer_name(self, obj):
        if obj.customer:
            return f"{obj.customer.first_name} {obj.customer.last_name}".strip()
        return ""

    def get_opportunity_name(self, obj):
        if obj.opportunity:
            return obj.opportunity.name
        return ""

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return ""

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return ""


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceItem model"""
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'product_id', 'product_name', 'description', 'quantity',
            'unit_price', 'discount_percent', 'total'
        ]
        read_only_fields = ['id', 'total']

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return ""

    def validate(self, data):
        """Validate invoice item data"""
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        
        if data.get('unit_price', 0) < 0:
            raise serializers.ValidationError("Unit price cannot be negative")
        
        return data


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model"""
    items = InvoiceItemSerializer(many=True, read_only=True)
    customer_name = serializers.SerializerMethodField()
    quotation_number = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'organization_id', 'quotation_id', 'quotation_number',
            'customer_id', 'customer_name', 'invoice_number', 'subject',
            'description', 'items', 'subtotal', 'tax_amount', 'discount_amount',
            'total_amount', 'status', 'due_date', 'paid_date', 'terms_conditions',
            'assigned_to', 'created_at', 'updated_at', 'is_active',
            'created_by_name', 'updated_by_name'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'subtotal', 'total_amount', 'created_at',
            'updated_at', 'created_by_name', 'updated_by_name'
        ]

    def get_customer_name(self, obj):
        if obj.customer:
            return f"{obj.customer.first_name} {obj.customer.last_name}".strip()
        return ""

    def get_quotation_number(self, obj):
        if obj.quotation:
            return obj.quotation.quotation_number
        return ""

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return ""

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return ""


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    full_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'organization_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'company', 'address', 'city', 'state', 'country',
            'postal_code', 'tax_number', 'customer_type', 'created_at',
            'updated_at', 'is_active', 'created_by_name', 'updated_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name', 'updated_by_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return ""

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return ""


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'organization_id', 'name', 'description', 'sku', 'category',
            'price', 'cost', 'stock_quantity', 'min_stock', 'unit', 'is_active',
            'created_at', 'updated_at', 'created_by_name', 'updated_by_name',
            'stock_status'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name', 'updated_by_name']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return ""

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return ""

    def get_stock_status(self, obj):
        if obj.stock_quantity <= 0:
            return "out_of_stock"
        elif obj.stock_quantity <= obj.min_stock:
            return "low_stock"
        else:
            return "in_stock"


class SalesDashboardSerializer(serializers.Serializer):
    """Serializer for Sales Dashboard data"""
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_opportunities = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_deal_size = serializers.DecimalField(max_digits=15, decimal_places=2)
    period = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField() 