"""
Opportunity models for ERP Sales Service
"""
from django.db import models
from core.models import OrganizationModel


class Opportunity(OrganizationModel):
    """Opportunity model for sales opportunities"""
    STAGE_CHOICES = [
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]

    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE, related_name='opportunities')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='prospecting')
    probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    expected_close_date = models.DateField()
    assigned_to = models.CharField(max_length=100, blank=True)  # User ID

    class Meta:
        db_table = 'opportunities'
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
        indexes = [
            models.Index(fields=['stage']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['expected_close_date']),
            models.Index(fields=['amount']),
        ]

    def __str__(self):
        return f"{self.name} - {self.stage}"

    @property
    def lead_name(self):
        return self.lead.full_name if self.lead else "" 