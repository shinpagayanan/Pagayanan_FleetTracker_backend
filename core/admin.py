from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    Asset,
    MaintenanceRequest,
    WorkOrder,
    MileageLog,
    AuditLog
)


from django.contrib.auth.admin import UserAdmin

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Role Information",
            {
                "fields": (
                    "role",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Role Information",
            {
                "fields": (
                    "role",
                )
            },
        ),
    )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):

    list_display = (
        "asset_code",
        "name",
        "asset_type",
        "assigned_to",
        "status",
        "purchase_date",
        "procurement_cost",

    )

    list_filter = (
        "asset_type",
        "status",
        "assigned_to",
    )

    search_fields = (
        "asset_code",
        "name",
        "plate_number",
        "assigned_to__username",
    )


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "asset",
        "requested_by",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "asset__name",
        "requested_by__username",
        "issue_description",
    )


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "maintenance_request",
        "approved_by",
        "completed",
        "completion_date",
    )

    list_filter = (
        "completed",
        "completion_date",
    )


@admin.register(MileageLog)
class MileageLogAdmin(admin.ModelAdmin):

    list_display = (
        "asset",
        "submitted_by",
        "mileage",
        "submitted_at",
    )

    list_filter = (
        "submitted_at",
    )

admin.site.register(
    AuditLog
)