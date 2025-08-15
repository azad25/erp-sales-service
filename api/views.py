"""
API Views for ERP Sales Service
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from datetime import timedelta

from core.models import OrganizationModel
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.quotations.models import Quotation
from apps.invoices.models import Invoice
from apps.customers.models import Customer
from apps.products.models import Product

from .serializers import (
    LeadSerializer, OpportunitySerializer, QuotationSerializer,
    InvoiceSerializer, CustomerSerializer, ProductSerializer,
    SalesDashboardSerializer
)


class HealthCheckView(APIView):
    """Health check endpoint for API"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'ERP Sales Service API',
            'timestamp': timezone.now().isoformat(),
        })


class SalesDashboardView(APIView):
    """Sales dashboard endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get organization from request headers or user
        organization_id = request.headers.get('X-Organization-ID')
        if not organization_id:
            return Response(
                {'error': 'Organization ID required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get period from query params
        period = request.query_params.get('period', 'monthly')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Calculate date range
        if not start_date or not end_date:
            end_date = timezone.now()
            if period == 'daily':
                start_date = end_date - timedelta(days=30)
            elif period == 'weekly':
                start_date = end_date - timedelta(weeks=12)
            elif period == 'monthly':
                start_date = end_date - timedelta(days=365)
            else:  # yearly
                start_date = end_date - timedelta(days=365*3)
        else:
            start_date = timezone.datetime.fromisoformat(start_date)
            end_date = timezone.datetime.fromisoformat(end_date)
        
        # Get dashboard data
        dashboard_data = self._get_dashboard_data(
            organization_id, start_date, end_date, period
        )
        
        serializer = SalesDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    def _get_dashboard_data(self, organization_id, start_date, end_date, period):
        """Get dashboard data for the given period"""
        # Get counts
        total_leads = Lead.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).count()
        
        total_opportunities = Opportunity.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).count()
        
        total_customers = Customer.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).count()
        
        # Get revenue data
        revenue_data = Invoice.objects.filter(
            organization_id=organization_id,
            is_active=True,
            status='paid',
            paid_date__range=[start_date, end_date]
        ).aggregate(
            total_revenue=Sum('total_amount'),
            total_invoices=Count('id')
        )
        
        total_revenue = revenue_data['total_revenue'] or 0
        total_invoices = revenue_data['total_invoices'] or 0
        
        # Calculate conversion rate
        conversion_rate = 0
        if total_leads > 0:
            converted_leads = Lead.objects.filter(
                organization_id=organization_id,
                is_active=True,
                status='converted'
            ).count()
            conversion_rate = (converted_leads / total_leads) * 100
        
        # Calculate average deal size
        average_deal_size = 0
        if total_opportunities > 0:
            total_opportunity_value = Opportunity.objects.filter(
                organization_id=organization_id,
                is_active=True
            ).aggregate(total=Sum('amount'))['total'] or 0
            average_deal_size = total_opportunity_value / total_opportunities
        
        return {
            'total_revenue': total_revenue,
            'total_opportunities': total_opportunities,
            'total_leads': total_leads,
            'total_customers': total_customers,
            'conversion_rate': conversion_rate,
            'average_deal_size': average_deal_size,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
        }


class SalesReportsView(APIView):
    """Sales reports endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get organization from request headers
        organization_id = request.headers.get('X-Organization-ID')
        if not organization_id:
            return Response(
                {'error': 'Organization ID required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report_type = request.query_params.get('type', 'summary')
        
        if report_type == 'summary':
            return self._get_summary_report(organization_id)
        elif report_type == 'performance':
            return self._get_performance_report(organization_id)
        elif report_type == 'pipeline':
            return self._get_pipeline_report(organization_id)
        else:
            return Response(
                {'error': 'Invalid report type'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_summary_report(self, organization_id):
        """Get summary report"""
        # Implementation for summary report
        return Response({'message': 'Summary report'})
    
    def _get_performance_report(self, organization_id):
        """Get performance report"""
        # Implementation for performance report
        return Response({'message': 'Performance report'})
    
    def _get_pipeline_report(self, organization_id):
        """Get pipeline report"""
        # Implementation for pipeline report
        return Response({'message': 'Pipeline report'})


class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet for Lead model"""
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'source', 'assigned_to']
    search_fields = ['first_name', 'last_name', 'email', 'company']
    ordering_fields = ['created_at', 'estimated_value', 'first_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization"""
        organization_id = self.request.headers.get('X-Organization-ID')
        if organization_id:
            return Lead.objects.filter(
                organization_id=organization_id,
                is_active=True
            )
        return Lead.objects.none()
    
    @action(detail=True, methods=['post'])
    def convert_to_opportunity(self, request, pk=None):
        """Convert lead to opportunity"""
        lead = self.get_object()
        # Implementation for converting lead to opportunity
        return Response({'message': 'Lead converted to opportunity'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get lead statistics"""
        organization_id = request.headers.get('X-Organization-ID')
        if not organization_id:
            return Response(
                {'error': 'Organization ID required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stats = Lead.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).aggregate(
            total_leads=Count('id'),
            new_leads=Count('id', filter=Q(status='new')),
            qualified_leads=Count('id', filter=Q(status='qualified')),
            converted_leads=Count('id', filter=Q(status='converted')),
        )
        
        return Response(stats)


class OpportunityViewSet(viewsets.ModelViewSet):
    """ViewSet for Opportunity model"""
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['stage', 'assigned_to']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'amount', 'expected_close_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization"""
        organization_id = self.request.headers.get('X-Organization-ID')
        if organization_id:
            return Opportunity.objects.filter(
                organization_id=organization_id,
                is_active=True
            )
        return Opportunity.objects.none()
    
    @action(detail=True, methods=['post'])
    def create_quotation(self, request, pk=None):
        """Create quotation from opportunity"""
        opportunity = self.get_object()
        # Implementation for creating quotation
        return Response({'message': 'Quotation created'})
    
    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Get sales pipeline data"""
        organization_id = request.headers.get('X-Organization-ID')
        if not organization_id:
            return Response(
                {'error': 'Organization ID required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pipeline = Opportunity.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).values('stage').annotate(
            count=Count('id'),
            total_value=Sum('amount')
        )
        
        return Response(pipeline)


class QuotationViewSet(viewsets.ModelViewSet):
    """ViewSet for Quotation model"""
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'assigned_to']
    search_fields = ['quotation_number', 'subject']
    ordering_fields = ['created_at', 'total_amount', 'valid_until']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization"""
        organization_id = self.request.headers.get('X-Organization-ID')
        if organization_id:
            return Quotation.objects.filter(
                organization_id=organization_id,
                is_active=True
            )
        return Quotation.objects.none()
    
    @action(detail=True, methods=['post'])
    def convert_to_invoice(self, request, pk=None):
        """Convert quotation to invoice"""
        quotation = self.get_object()
        # Implementation for converting quotation to invoice
        return Response({'message': 'Quotation converted to invoice'})


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'assigned_to']
    search_fields = ['invoice_number', 'subject']
    ordering_fields = ['created_at', 'total_amount', 'due_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization"""
        organization_id = self.request.headers.get('X-Organization-ID')
        if organization_id:
            return Invoice.objects.filter(
                organization_id=organization_id,
                is_active=True
            )
        return Invoice.objects.none()
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        # Implementation for marking invoice as paid
        return Response({'message': 'Invoice marked as paid'})


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer model"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer_type']
    search_fields = ['first_name', 'last_name', 'email', 'company']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization"""
        organization_id = self.request.headers.get('X-Organization-ID')
        if organization_id:
            return Customer.objects.filter(
                organization_id=organization_id,
                is_active=True
            )
        return Customer.objects.none()


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['created_at', 'price', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by organization"""
        organization_id = self.request.headers.get('X-Organization-ID')
        if organization_id:
            return Product.objects.filter(
                organization_id=organization_id,
                is_active=True
            )
        return Product.objects.none()
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        organization_id = request.headers.get('X-Organization-ID')
        if not organization_id:
            return Response(
                {'error': 'Organization ID required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        low_stock_products = Product.objects.filter(
            organization_id=organization_id,
            is_active=True,
            stock_quantity__lte=F('min_stock')
        )
        
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data) 