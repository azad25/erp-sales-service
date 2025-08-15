"""
Core models for ERP Sales Service
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """Base model with common fields for all models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='%(class)s_updated'
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class OrganizationModel(BaseModel):
    """Base model for organization-scoped models"""
    organization_id = models.UUIDField()
    organization_name = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization_id']),
            models.Index(fields=['organization_id', 'is_active']),
        ]


class AuditLog(BaseModel):
    """Audit log for tracking changes"""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
    ]

    model_name = models.CharField(max_length=100)
    object_id = models.UUIDField()
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    organization_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['organization_id', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"{self.action} on {self.model_name} {self.object_id}"


class SystemConfiguration(BaseModel):
    """System configuration settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_encrypted = models.BooleanField(default=False)
    category = models.CharField(max_length=50, default='general')

    class Meta:
        db_table = 'system_configurations'
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'

    def __str__(self):
        return self.key 