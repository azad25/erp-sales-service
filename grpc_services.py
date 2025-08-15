"""
gRPC Service Implementation for ERP Sales Service
"""
import grpc
from google.protobuf import empty_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from django.utils import timezone
from django.db import transaction, models
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# Import generated gRPC modules (these will be generated from proto files)
# from proto.sales import sales_pb2, sales_pb2_grpc

# Import Django models
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.quotations.models import Quotation, QuotationItem
from apps.invoices.models import Invoice, InvoiceItem
from apps.customers.models import Customer
from apps.products.models import Product


class SalesServiceServicer:
    """gRPC service implementation for Sales Service"""

    def _datetime_to_timestamp(self, dt):
        """Convert Django datetime to protobuf timestamp"""
        if dt is None:
            return None
        timestamp = Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp

    def _timestamp_to_datetime(self, timestamp):
        """Convert protobuf timestamp to Django datetime"""
        if timestamp is None:
            return None
        return timestamp.ToDatetime()

    def _get_user_from_context(self, context):
        """Extract user information from gRPC context"""
        # This would be implemented based on your authentication mechanism
        # For now, we'll use metadata from the context
        metadata = dict(context.invocation_metadata())
        user_id = metadata.get('user-id', '')
        organization_id = metadata.get('organization-id', '')
        return user_id, organization_id

    def HealthCheck(self, request, context):
        """Health check endpoint"""
        try:
            # Basic health check
            return {
                'success': True,
                'message': "Sales Service is healthy"
            }
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {
                'success': False,
                'error': str(e)
            }

    # Lead Management
    def CreateLead(self, request, context):
        """Create a new lead"""
        try:
            user_id, organization_id = self._get_user_from_context(context)
            
            with transaction.atomic():
                lead = Lead.objects.create(
                    organization_id=request.organization_id,
                    organization_name="",  # Would be fetched from auth service
                    first_name=request.first_name,
                    last_name=request.last_name,
                    email=request.email,
                    phone=request.phone,
                    company=request.company,
                    position=request.position,
                    source=request.source,
                    estimated_value=request.estimated_value,
                    description=request.description,
                    assigned_to=request.assigned_to,
                    created_by_id=user_id if user_id else None,
                )

            return {
                'id': str(lead.id),
                'organization_id': str(lead.organization_id),
                'first_name': lead.first_name,
                'last_name': lead.last_name,
                'email': lead.email,
                'phone': lead.phone or "",
                'company': lead.company or "",
                'position': lead.position or "",
                'source': lead.source or "",
                'status': lead.status or "",
                'estimated_value': float(lead.estimated_value or 0),
                'description': lead.description or "",
                'assigned_to': lead.assigned_to or "",
                'created_at': self._datetime_to_timestamp(lead.created_at),
                'updated_at': self._datetime_to_timestamp(lead.updated_at),
                'is_active': lead.is_active,
            }

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def GetLead(self, request, context):
        """Get a lead by ID"""
        try:
            lead = Lead.objects.get(
                id=request.id,
                organization_id=request.organization_id,
                is_active=True
            )

            return {
                'id': str(lead.id),
                'organization_id': str(lead.organization_id),
                'first_name': lead.first_name,
                'last_name': lead.last_name,
                'email': lead.email,
                'phone': lead.phone or "",
                'company': lead.company or "",
                'position': lead.position or "",
                'source': lead.source or "",
                'status': lead.status or "",
                'estimated_value': float(lead.estimated_value or 0),
                'description': lead.description or "",
                'assigned_to': lead.assigned_to or "",
                'created_at': self._datetime_to_timestamp(lead.created_at),
                'updated_at': self._datetime_to_timestamp(lead.updated_at),
                'is_active': lead.is_active,
            }

        except ObjectDoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Lead not found")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def UpdateLead(self, request, context):
        """Update a lead"""
        try:
            user_id, organization_id = self._get_user_from_context(context)
            
            with transaction.atomic():
                lead = Lead.objects.get(
                    id=request.id,
                    organization_id=request.organization_id,
                    is_active=True
                )

                # Update fields
                lead.first_name = request.first_name
                lead.last_name = request.last_name
                lead.email = request.email
                lead.phone = request.phone
                lead.company = request.company
                lead.position = request.position
                lead.source = request.source
                lead.status = request.status
                lead.estimated_value = request.estimated_value
                lead.description = request.description
                lead.assigned_to = request.assigned_to
                lead.updated_by_id = user_id if user_id else None
                lead.save()

            return {
                'id': str(lead.id),
                'organization_id': str(lead.organization_id),
                'first_name': lead.first_name,
                'last_name': lead.last_name,
                'email': lead.email,
                'phone': lead.phone or "",
                'company': lead.company or "",
                'position': lead.position or "",
                'source': lead.source or "",
                'status': lead.status or "",
                'estimated_value': float(lead.estimated_value or 0),
                'description': lead.description or "",
                'assigned_to': lead.assigned_to or "",
                'created_at': self._datetime_to_timestamp(lead.created_at),
                'updated_at': self._datetime_to_timestamp(lead.updated_at),
                'is_active': lead.is_active,
            }

        except ObjectDoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Lead not found")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def DeleteLead(self, request, context):
        """Delete a lead (soft delete)"""
        try:
            user_id, organization_id = self._get_user_from_context(context)
            
            with transaction.atomic():
                lead = Lead.objects.get(
                    id=request.id,
                    organization_id=request.organization_id,
                    is_active=True
                )
                lead.is_active = False
                lead.is_deleted = True
                lead.updated_by_id = user_id if user_id else None
                lead.save()

            return {
                'success': True,
                'message': "Lead deleted successfully"
            }

        except ObjectDoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Lead not found")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def ListLeads(self, request, context):
        """List leads with filtering and pagination"""
        try:
            queryset = Lead.objects.filter(
                organization_id=request.organization_id,
                is_active=True
            )

            # Apply filters
            if request.search:
                queryset = queryset.filter(
                    models.Q(first_name__icontains=request.search) |
                    models.Q(last_name__icontains=request.search) |
                    models.Q(email__icontains=request.search) |
                    models.Q(company__icontains=request.search)
                )

            if request.status:
                queryset = queryset.filter(status=request.status)

            if request.assigned_to:
                queryset = queryset.filter(assigned_to=request.assigned_to)

            # Get total count
            total_count = queryset.count()

            # Apply pagination
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 20
            offset = (page - 1) * page_size

            leads = queryset[offset:offset + page_size]

            # Convert to protobuf messages
            lead_messages = []
            for lead in leads:
                lead_messages.append({
                    'id': str(lead.id),
                    'organization_id': str(lead.organization_id),
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'email': lead.email,
                    'phone': lead.phone or "",
                    'company': lead.company or "",
                    'position': lead.position or "",
                    'source': lead.source or "",
                    'status': lead.status or "",
                    'estimated_value': float(lead.estimated_value or 0),
                    'description': lead.description or "",
                    'assigned_to': lead.assigned_to or "",
                    'created_at': self._datetime_to_timestamp(lead.created_at),
                    'updated_at': self._datetime_to_timestamp(lead.updated_at),
                    'is_active': lead.is_active,
                })

            return {
                'leads': lead_messages,
                'total_count': total_count,
                'page': page,
                'page_size': page_size
            }

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    # Opportunity Management (similar pattern)
    def CreateOpportunity(self, request, context):
        """Create a new opportunity"""
        try:
            user_id, organization_id = self._get_user_from_context(context)
            
            with transaction.atomic():
                opportunity = Opportunity.objects.create(
                    organization_id=request.organization_id,
                    organization_name="",
                    lead_id=request.lead_id,
                    name=request.name,
                    description=request.description,
                    amount=request.amount,
                    stage=request.stage,
                    probability=request.probability,
                    expected_close_date=self._timestamp_to_datetime(request.expected_close_date),
                    assigned_to=request.assigned_to,
                    created_by_id=user_id if user_id else None,
                )

            return {
                'id': str(opportunity.id),
                'organization_id': str(opportunity.organization_id),
                'lead_id': str(opportunity.lead_id),
                'name': opportunity.name,
                'description': opportunity.description,
                'amount': float(opportunity.amount),
                'stage': opportunity.stage,
                'probability': float(opportunity.probability),
                'expected_close_date': self._datetime_to_timestamp(opportunity.expected_close_date),
                'assigned_to': opportunity.assigned_to or "",
                'created_at': self._datetime_to_timestamp(opportunity.created_at),
                'updated_at': self._datetime_to_timestamp(opportunity.updated_at),
                'is_active': opportunity.is_active,
            }

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    # Add other opportunity methods (GetOpportunity, UpdateOpportunity, etc.)
    # Add quotation methods
    # Add invoice methods
    # Add customer methods
    # Add product methods
    # Add dashboard methods

    def GetSalesDashboard(self, request, context):
        """Get sales dashboard data"""
        try:
            # This would implement dashboard logic
            # For now, return basic structure
            return {
                'total_revenue': 0.0,
                'total_opportunities': 0.0,
                'total_leads': 0,
                'total_customers': 0,
                'conversion_rate': 0.0,
                'average_deal_size': 0.0,
                'chart_data': [],
                'top_performers': [],
                'recent_activities': []
            }

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise 