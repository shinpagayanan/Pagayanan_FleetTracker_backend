from rest_framework.routers import DefaultRouter

from .views import (
    AssetViewSet,
    MaintenanceRequestViewSet,
    WorkOrderViewSet,
    MileageLogViewSet, UserViewSet
    
)
from .views import (
    DashboardSummaryAPIView,
    MaintenanceAlertAPIView,
    AssetReportAPIView,
    MaintenanceReportAPIView,
    WorkOrderReportAPIView,
     MileageReportAPIView,
     AuditLogViewSet

)

from .views import CurrentUserAPIView
from django.urls import path

router = DefaultRouter()

router.register(
    "assets",
    AssetViewSet
)

router.register(
    "requests",
    MaintenanceRequestViewSet
)

router.register(
    "workorders",
    WorkOrderViewSet
)

router.register(
    "mileage",
    MileageLogViewSet
)


router.register(
    "users",
    UserViewSet
)

router.register(
    r"audit-logs",
    AuditLogViewSet,
    basename="auditlogs"
)
urlpatterns = router.urls + [

    path(
        "dashboard/",
        DashboardSummaryAPIView.as_view(),
        name="dashboard-summary"
    ),

    path(
        "alerts/",
        MaintenanceAlertAPIView.as_view(),
        name="maintenance-alerts"
    ),
path(
    "current-user/",
    CurrentUserAPIView.as_view(),
    name="current-user"
    
),
path(
        "reports/assets/",
        AssetReportAPIView.as_view(),
        name="asset-report-api"
    ),

    path(
        "reports/maintenance/",
        MaintenanceReportAPIView.as_view(),
        name="maintenance-report-api"
    ),

    path(
        "reports/workorders/",
        WorkOrderReportAPIView.as_view(),
        name="workorder-report-api"
    ),
    path(
    "reports/assets/",
    AssetReportAPIView.as_view(),
    name="asset-report-api"
),

path(
    "reports/maintenance/",
    MaintenanceReportAPIView.as_view(),
    name="maintenance-report-api"
),

path(
    "reports/workorders/",
    WorkOrderReportAPIView.as_view(),
    name="workorder-report-api"
),

path(
    "reports/mileage/",
    MileageReportAPIView.as_view(),
    name="mileage-report-api"
),
]