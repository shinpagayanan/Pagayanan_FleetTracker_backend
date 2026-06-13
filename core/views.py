from rest_framework import viewsets
from rest_framework.decorators import api_view

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from .mixins import (
    AuditMixin
)

from django.utils import timezone

from .audit import log_event

from .models import (
    Asset,
    MaintenanceRequest,
    WorkOrder,
    MileageLog,
    User,
    AuditLog
)

from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.decorators import (
    permission_classes
)

from .serializers import (
    AssetSerializer,
    MaintenanceRequestSerializer,
    WorkOrderSerializer,
    MileageLogSerializer,
    UserSerializer,
    AuditLogSerializer
)
from .permissions import (
    IsManager,
    IsAuditorReadOnly,
    CanCreateMaintenanceRequest,
    CanSubmitMileage
)
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import SAFE_METHODS

from django.db.models import F

from .filters import (
    AssetFilter,
    MaintenanceRequestFilter,
)



from rest_framework.exceptions import ValidationError

from rest_framework.decorators import action

from rest_framework import status

from rest_framework_simplejwt.views import (
    TokenObtainPairView
)
from rest_framework.response import Response
from rest_framework import status
from axes.handlers.proxy import AxesProxyHandler


class CustomTokenObtainPairView(
    TokenObtainPairView
):

    def post(self, request, *args, **kwargs):

        print("TOKEN ENDPOINT HIT")

        if AxesProxyHandler.is_locked(request):
            return Response(
                {
                    "detail":
                    "Too many failed login attempts."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().post(
            request,
            *args,
            **kwargs
        )
class AssetViewSet(
    AuditMixin,
    viewsets.ModelViewSet
):

    audit_model_name = "Asset"

    queryset = Asset.objects.all()

    serializer_class = AssetSerializer

    filterset_class = AssetFilter

    def get_queryset(self):

        user = self.request.user

        queryset = Asset.objects.select_related(
            "assigned_to"
        )

        # Manager sees everything

        if user.role == "MANAGER":

            return queryset

        # Auditor sees everything (read only)

        if user.role == "AUDITOR":

            return queryset

        # Staff only sees assigned assets

        return queryset.filter(
            assigned_to=user
        )

    def get_permissions(self):

        if self.request.method in SAFE_METHODS:

            return [IsAuditorReadOnly()]

        return [IsManager()]

    @action(
        detail=True,
        methods=["post", "patch"]
    )
    def assign(
        self,
        request,
        pk=None
    ):

        if request.user.role != "MANAGER":

            return Response(
                {
                    "detail":
                    "Permission denied"
                },
                status=403
            )

        asset = self.get_object()

        user_id = request.data.get(
            "user_id"
        )

        try:

           user = User.objects.get(
                id=user_id,
                role="STAFF"
            )

        except User.DoesNotExist:

            return Response(
                {
                    "detail":
                    "User not found"
                },
                status=404
            )

        asset.assigned_to = user

        asset.save()

        log_event(
            request,
            "ASSIGN",
            "Asset",
            asset.id
        )

        return Response(
            {
                "message":
                (
                    f"{asset.name} assigned "
                    f"to {user.username}"
                )
            }
        )

    @action(
        detail=True,
        methods=["post"]
    )
    def unassign(
        self,
        request,
        pk=None
    ):

        if request.user.role != "MANAGER":

            return Response(
                {
                    "detail":
                    "Permission denied"
                },
                status=403
            )

        asset = self.get_object()

        asset.assigned_to = None

        asset.save()

        log_event(
            request,
            "UNASSIGN",
            "Asset",
            asset.id
        )

        return Response(
            {
                "message":
                "Asset unassigned"
            }
        )

    @action(
        detail=False,
        methods=["post"]
    )
    def bulk_assign(
        self,
        request
    ):

        if request.user.role != "MANAGER":

            return Response(
                {
                    "detail":
                    "Permission denied"
                },
                status=403
            )

        ids = request.data.get(
            "ids",
            []
        )

        user_id = request.data.get(
            "user_id"
        )

        try:

            user = User.objects.get(
                id=user_id,
                role="STAFF"
            )

        except User.DoesNotExist:

            return Response(
                {
                    "detail":
                    "User not found"
                },
                status=404
            )

        assets = Asset.objects.filter(
            id__in=ids
        )

        count = 0

        for asset in assets:

            asset.assigned_to = user

            asset.save()

            log_event(
                request,
                "BULK_ASSIGN",
                "Asset",
                asset.id
            )

            count += 1

        return Response(
            {
                "assigned":
                count
            }
        )
class MaintenanceRequestViewSet(
    AuditMixin,
    viewsets.ModelViewSet
):
    audit_model_name = "MaintenanceRequest"

    queryset = MaintenanceRequest.objects.all()

    serializer_class = (
        MaintenanceRequestSerializer
    )

    filterset_class = (
        MaintenanceRequestFilter
    )

    permission_classes = [
        CanCreateMaintenanceRequest
    ]

    def perform_create(
        self,
        serializer
    ):

        asset = serializer.validated_data["asset"]

        user = self.request.user

        # Staff can only request maintenance
        # for assets assigned to them

        if (
            user.role == "STAFF"
            and asset.assigned_to != user
        ):
            raise ValidationError(
                {
                    "asset":
                    (
                        "You can only submit "
                        "maintenance requests for "
                        "assets assigned to you."
                    )
                }
            )

        obj = serializer.save(
            requested_by=user
        )

        self.audit_create(obj)

    def get_queryset(self):

        user = self.request.user

        scope = self.request.query_params.get(
            "scope",
            "mine"
        )

        queryset = (
            MaintenanceRequest.objects
            .select_related(
                "asset",
                "requested_by"
            )
        )

        if user.role == "MANAGER":
            return queryset

        if user.role == "AUDITOR":
            return queryset

        # STAFF

        if scope == "all":

            return queryset.none()

        return queryset.filter(
            requested_by=user
        )

    @action(
        detail=True,
        methods=["post"]
    )
    def approve(
        self,
        request,
        pk=None
    ):

        if request.user.role != "MANAGER":

            return Response(
                {
                    "detail":
                    "Permission denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        maintenance_request = (
            self.get_object()
        )

        if (
            maintenance_request.status
            != MaintenanceRequest.PENDING
        ):

            return Response(
                {
                    "detail":
                    "Request already processed"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if hasattr(
            maintenance_request,
            "workorder"
        ):

            return Response(
                {
                    "detail":
                    "Work order already exists"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        maintenance_request.status = (
            MaintenanceRequest.APPROVED
        )

        maintenance_request.save()

        WorkOrder.objects.create(
            maintenance_request=
                maintenance_request,

            approved_by=
                request.user,

            work_description=
                maintenance_request.issue_description
                
                
        )

        log_event(
            request,
            "APPROVE",
            "MaintenanceRequest",
            maintenance_request.id
        )

        return Response(
            {
                "message":
                (
                    "Request approved "
                    "and work order created"
                )
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"]
    )
    def reject(
        self,
        request,
        pk=None
    ):

        if request.user.role != "MANAGER":

            return Response(
                {
                    "detail":
                    "Permission denied"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        maintenance_request = (
            self.get_object()
        )

        if (
            maintenance_request.status
            != MaintenanceRequest.PENDING
        ):

            return Response(
                {
                    "detail":
                    "Request already processed"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        maintenance_request.status = (
            MaintenanceRequest.REJECTED
        )

        maintenance_request.save()

        log_event(
            request,
            "REJECT",
            "MaintenanceRequest",
            maintenance_request.id
        )

        return Response(
            {
                "message":
                "Request rejected"
            },
            status=status.HTTP_200_OK
        )
        

        maintenance_request = self.get_object()

        maintenance_request.status = (
            MaintenanceRequest.REJECTED
        )

        maintenance_request.save()


        return Response(
            {
                "message":
                "Request rejected"
            }
        )
    

class WorkOrderViewSet( AuditMixin,viewsets.ModelViewSet):
    audit_model_name = "WorkOrder"

    queryset = WorkOrder.objects.all()

    serializer_class = WorkOrderSerializer

    def get_queryset(self):

        user = self.request.user

        scope = self.request.query_params.get(
            "scope",
            "mine"
        )

        queryset = (
            WorkOrder.objects
            .select_related(
                "maintenance_request",
                "approved_by"
            )
        )

        if user.role in [
            "MANAGER",
            "AUDITOR"
        ]:
            return queryset

        # STAFF

        if scope == "all":

            return queryset.none()

        return queryset.filter(
            maintenance_request__requested_by=user
        )


    def get_permissions(self):

        if self.request.method in SAFE_METHODS:
            return [IsAuditorReadOnly()]

        return [IsManager()]
    def perform_create(self, serializer):

        maintenance_request = serializer.validated_data[
            "maintenance_request"
        ]

        if maintenance_request.status != "APPROVED":

            raise ValidationError(
                "Maintenance request must be approved first."
            )

        obj = serializer.save(
            approved_by=self.request.user
        )

        self.audit_create(obj)
    @action(
    detail=True,
    methods=["post"]
    )
    def complete(
        self,
        request,
        pk=None
    ):

        if request.user.role != "MANAGER":

            return Response(
                {
                    "detail":
                    "Permission denied"
                },
                status=403
            )

        work_order = self.get_object()

        if work_order.completed:

            return Response(
                {
                    "detail":
                    "Work order already completed"
                },
                status=400
            )

        work_order.completed = True

        work_order.completion_date = (
            timezone.now().date()
        )

        work_order.save()

        maintenance_request = (
            work_order.maintenance_request
        )

        maintenance_request.status = (
            MaintenanceRequest.COMPLETED
        )

        maintenance_request.save()

        log_event(
            request,
            "COMPLETE",
            "WorkOrder",
            work_order.id
        )

        return Response(
            {
                "message":
                "Work order completed",

                "completion_date":
                work_order.completion_date
            }
        )

    
@method_decorator(
    ratelimit(
        key="user",
        rate="3/m",
        method="POST",
        block=True
    ),
    name="create"
)
class MileageLogViewSet(AuditMixin,viewsets.ModelViewSet):

    audit_model_name = "MileageLog"

    queryset = MileageLog.objects.all()

    serializer_class = MileageLogSerializer

    permission_classes = [
        CanSubmitMileage
    ]

    def perform_create(self, serializer):

        mileage_log = serializer.save(
            submitted_by=self.request.user
        )

        self.audit_create(
            mileage_log
        )


        asset = mileage_log.asset

        asset.current_mileage = mileage_log.mileage

        asset.save()
    def get_queryset(self):

        user = self.request.user

        scope = self.request.query_params.get(
            "scope",
            "mine"
        )

        queryset = (
            MileageLog.objects
            .select_related(
                "asset",
                "submitted_by"
            )
        )

        if user.role in [
            "MANAGER",
            "AUDITOR"
        ]:
            return queryset

        # STAFF

        if scope == "all":

            return queryset.none()

        return queryset.filter(
            submitted_by=user
        )

class DashboardSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        # =========================
        # MANAGER
        # =========================

        if user.role == "MANAGER":

            total_assets = Asset.objects.count()

            total_requests = (
                MaintenanceRequest.objects.count()
            )

            total_work_orders = (
                WorkOrder.objects.count()
            )

            fleet_value = (
                Asset.objects.aggregate(
                    total=Sum(
                        "procurement_cost"
                    )
                )["total"]
                or 0
            )

            pending_requests = (
                MaintenanceRequest.objects.filter(
                    status="PENDING"
                ).count()
            )

            return Response({

                "role": "MANAGER",

                "total_assets":
                    total_assets,

                "total_requests":
                    total_requests,

                "total_work_orders":
                    total_work_orders,

                "pending_requests":
                    pending_requests,

                "fleet_value":
                    fleet_value,
            })

        # =========================
        # AUDITOR
        # =========================

        elif user.role == "AUDITOR":

            return Response({

                "role": "AUDITOR",

                "total_assets":
                    Asset.objects.count(),

                "total_requests":
                    MaintenanceRequest.objects.count(),

                "total_work_orders":
                    WorkOrder.objects.count(),

                # no fleet value
                # no procurement costs
            })

        # =========================
        # STAFF
        # =========================

        return Response({

            "role": "STAFF",

            "my_requests":
                MaintenanceRequest.objects.filter(
                    requested_by=user
                ).count(),

            "pending_requests":
                MaintenanceRequest.objects.filter(
                    requested_by=user,
                    status="PENDING"
                ).count(),

            "approved_requests":
                MaintenanceRequest.objects.filter(
                    requested_by=user,
                    status="APPROVED"
                ).count(),

            "completed_requests":
                MaintenanceRequest.objects.filter(
                    requested_by=user,
                    status="COMPLETED"
                ).count(),

            "mileage_logs":
                MileageLog.objects.filter(
                    submitted_by=user
                ).count(),
        })
class MaintenanceAlertAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        due_assets = Asset.objects.filter(
            asset_type="VEHICLE",
            current_mileage__gte=F(
                "maintenance_interval"
            )
        )

        data = []

        for asset in due_assets:

            data.append({
                "id": asset.id,
                "asset_code": asset.asset_code,
                "name": asset.name,
                "current_mileage": asset.current_mileage,
                "maintenance_interval":
                    asset.maintenance_interval,
            })

        return Response(data)


class CurrentUserAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request
    ):

        return Response({
            "id":
                request.user.id,

            "username":
                request.user.username,

            "first_name":
                request.user.first_name,

            "last_name":
                request.user.last_name,

            "full_name":
                request.user.get_full_name(),

            "email":
                request.user.email,

            "role":
                request.user.role,
        })
    

from rest_framework import viewsets

class UserViewSet(
    viewsets.ModelViewSet
):

    queryset = User.objects.all()

    serializer_class = UserSerializer

    permission_classes = [
        IsManager
    ]

    def get_queryset(self):

        user = self.request.user

        if user.role != "MANAGER":

            return User.objects.none()

        return User.objects.all()
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_dashboard(
    request
):
    if request.user.role != "STAFF":

        return Response(
            {
                "detail":
                "Permission denied"
            },
            status=403
        )

    user = request.user

    return Response({

        "my_requests":
        MaintenanceRequest.objects.filter(
            requested_by=user
        ).count(),

        "pending_requests":
        MaintenanceRequest.objects.filter(
            requested_by=user,
            status="PENDING"
        ).count(),

        "completed_requests":
        MaintenanceRequest.objects.filter(
            requested_by=user,
            status="COMPLETED"
        ).count(),

        "recent_requests":
        MaintenanceRequestSerializer(
            MaintenanceRequest.objects.filter(
                requested_by=user
            ).order_by("-created_at")[:5],
            many=True
        ).data,

        "recent_mileage_logs":
        MileageLogSerializer(
            MileageLog.objects.filter(
                submitted_by=user
            ).order_by("-submitted_at")[:5],
            many=True
        ).data
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def auditor_dashboard(
    request
):
    if request.user.role != "AUDITOR":

        return Response(
            {
                "detail":
                "Permission denied"
            },
            status=403
        )
    

    return Response({

        "total_assets":
        Asset.objects.count(),

        "total_requests":
        MaintenanceRequest.objects.count(),

        "total_workorders":
        WorkOrder.objects.count(),

        "recent_requests":
        MaintenanceRequestSerializer(
            MaintenanceRequest.objects.order_by(
                "-created_at"
            )[:5],
            many=True
        ).data,

        "recent_workorders":
        WorkOrderSerializer(
            WorkOrder.objects.order_by(
                "-id"
            )[:5],
            many=True
        ).data
    })




class AssetReportAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        if request.user.role == "STAFF":

            return Response(
                {
                    "detail":
                    "Not authorized"
                },
                status=403
            )

        assets = Asset.objects.all()

        asset_records = []

        for asset in assets:

            record = {

                "id":
                    asset.id,

                "asset_code":
                    asset.asset_code,

                "name":
                    asset.name,

                "asset_type":
                    asset.asset_type,

                "status":
                    asset.status,

                "purchase_date":
                    asset.purchase_date,
            }

            if request.user.role == "MANAGER":

                record[
                    "procurement_cost"
                ] = (
                    asset.procurement_cost
                )

            asset_records.append(
                record
            )

        response = {

            "summary": {

                "total_assets":
                    assets.count(),

                "vehicles":
                    assets.filter(
                        asset_type="VEHICLE"
                    ).count(),

                "it_equipment":
                    assets.filter(
                        asset_type="IT"
                    ).count(),

                "active_assets":
                    assets.filter(
                        status="ACTIVE"
                    ).count(),

                "inactive_assets":
                    assets.exclude(
                        status="ACTIVE"
                    ).count(),
            },

            "assets":
                asset_records,
        }

        if request.user.role == "MANAGER":

            response["summary"][
                "fleet_value"
            ] = (
                assets.aggregate(
                    total=Sum(
                        "procurement_cost"
                    )
                )["total"]
                or 0
            )

        return Response(
            response
        )

class MaintenanceReportAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        if request.user.role == "STAFF":

            return Response(
                {
                    "detail":
                    "Not authorized"
                },
                status=403
            )

        requests = (
            MaintenanceRequest.objects
            .select_related(
                "asset",
                "requested_by"
            )
        )

        request_records = []

        for item in requests:

            request_records.append({

                "id":
                    item.id,

                "asset":
                    item.asset.name,

                "requested_by":
                    item.requested_by.username,

                "status":
                    item.status,

                "created_at":
                    item.created_at,
            })

        return Response({

            "summary": {

                "total_requests":
                    requests.count(),

                "pending":
                    requests.filter(
                        status="PENDING"
                    ).count(),

                "approved":
                    requests.filter(
                        status="APPROVED"
                    ).count(),

                "rejected":
                    requests.filter(
                        status="REJECTED"
                    ).count(),

                "completed":
                    requests.filter(
                        status="COMPLETED"
                    ).count(),
            },

            "requests":
                request_records,
        })
    
class WorkOrderReportAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        if request.user.role == "STAFF":

            return Response(
                {
                    "detail":
                    "Not authorized"
                },
                status=403
            )

        workorders = (
            WorkOrder.objects
            .select_related(
                "maintenance_request",
                "approved_by"
            )
        )

        completed_count = (
            workorders.filter(
                completed=True
            ).count()
        )

        total_count = (
            workorders.count()
        )

        completion_rate = 0

        if total_count:

            completion_rate = round(
                (
                    completed_count
                    / total_count
                ) * 100,
                2
            )

        workorder_records = []

        for workorder in workorders:

            workorder_records.append({

                "id":
                    workorder.id,

                "maintenance_request":
                    workorder.maintenance_request.id,

                "approved_by":
                    workorder.approved_by.username,

                "completed":
                    workorder.completed,

                "completion_date":
                    workorder.completion_date,
            })

        return Response({

            "summary": {

                "total_work_orders":
                    total_count,

                "completed":
                    completed_count,

                "pending":
                    total_count
                    - completed_count,

                "completion_rate":
                    completion_rate,
            },

            "workorders":
                workorder_records,
        })
    
from .models import MileageLog


class MileageReportAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        if request.user.role == "STAFF":

            return Response(
                {
                    "detail":
                    "Not authorized"
                },
                status=403
            )

        logs = (
            MileageLog.objects
            .select_related(
                "asset",
                "submitted_by"
            )
        )

        log_records = []

        highest_mileage = (
            MileageLog.objects
            .order_by(
                "-mileage"
            )
            .first()
        )

        for log in logs:

            log_records.append({

                "id":
                    log.id,

                "asset":
                    log.asset.name,

                "submitted_by":
                    log.submitted_by.username,

                "mileage":
                    log.mileage,

                "submitted_at":
                    log.submitted_at,
            })

        response = {

            "summary": {

                "total_logs":
                    logs.count(),

                "vehicles_logged":
                    logs.values(
                        "asset"
                    )
                    .distinct()
                    .count(),
            },

            "logs":
                log_records,
        }

        if highest_mileage:

            response[
                "highest_mileage_vehicle"
            ] = {

                "asset":
                    highest_mileage.asset.name,

                "mileage":
                    highest_mileage.mileage,
            }

        return Response(
            response
        )
    
class AuditLogViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = (
        AuditLog.objects
        .select_related("user")
        .order_by("-timestamp")
    )

    serializer_class = (
        AuditLogSerializer
    )

    permission_classes = [
        IsManager
    ]