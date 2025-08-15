"""
Core URLs for ERP Sales Service
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('status/', views.service_status, name='service_status'),
    path('metrics/', views.service_metrics, name='service_metrics'),
] 