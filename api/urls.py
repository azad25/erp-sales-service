"""
API URLs for ERP Sales Service
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'leads', views.LeadViewSet, basename='lead')
router.register(r'opportunities', views.OpportunityViewSet, basename='opportunity')
router.register(r'quotations', views.QuotationViewSet, basename='quotation')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'products', views.ProductViewSet, basename='product')

app_name = 'api'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Dashboard and reporting
    path('dashboard/', views.SalesDashboardView.as_view(), name='dashboard'),
    path('reports/', views.SalesReportsView.as_view(), name='reports'),
    
    # Authentication
    path('auth/', include('rest_framework.urls')),
    
    # Health check
    path('health/', views.HealthCheckView.as_view(), name='health'),
] 