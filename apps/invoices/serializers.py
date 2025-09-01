"""
Invoice serializers for ERP Sales Service
"""
from rest_framework import serializers
from .models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice items"""
    
    product_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'product', 'product_name', 'description', 
            'quantity', 'unit_price', 'discount_percent', 'total',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices"""
    
    items = InvoiceItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(read_only=True)
    quotation_number = serializers.CharField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'quotation', 'customer', 'customer_name', 'quotation_number',
            'invoice_number', 'subject', 'description', 'subtotal', 'tax_amount',
            'discount_amount', 'total_amount', 'status', 'due_date', 'paid_date',
            'terms_conditions', 'assigned_to', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'subtotal', 'tax_amount', 'total_amount',
            'customer_name', 'quotation_number', 'created_at', 'updated_at'
        ]


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invoices"""
    
    items = InvoiceItemSerializer(many=True)
    
    class Meta:
        model = Invoice
        fields = [
            'quotation', 'customer', 'subject', 'description', 
            'discount_amount', 'due_date', 'terms_conditions', 
            'assigned_to', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        return invoice


class DocumentGenerationSerializer(serializers.Serializer):
    """Serializer for document generation requests"""
    
    format = serializers.ChoiceField(
        choices=['pdf', 'html', 'json'],
        default='pdf'
    )
    template_id = serializers.CharField(required=False, allow_blank=True)
    options = serializers.DictField(required=False, default=dict)


class TemplateSerializer(serializers.Serializer):
    """Serializer for invoice templates"""
    
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    html_template = serializers.CharField()
    css_styles = serializers.CharField(required=False, allow_blank=True)
    variables = serializers.DictField(required=False, default=dict)
    is_default = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)