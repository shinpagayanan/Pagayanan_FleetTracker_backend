from rest_framework import serializers

from .models import (
    User,
    Asset,
    MaintenanceRequest,
    WorkOrder,
    MileageLog
)
from .models import AuditLog




class AssetSerializer(serializers.ModelSerializer):

    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            role="STAFF"
        ),
        required=False,
        allow_null=True
    )

    assigned_to_username = serializers.CharField(
        source="assigned_to.username",
        read_only=True
    )

    class Meta:
        model = Asset
        fields = [
            "id",
            "asset_code",
            "name",
            "asset_type",
            "photo",
            "purchase_date",
            "procurement_cost",
            "status",
            "plate_number",
            "current_mileage",
            "maintenance_interval",
            "assigned_to",
            "assigned_to_username",
        ]

        def to_representation(self, instance):

            data = super().to_representation(
                instance
            )

            request = self.context.get(
                "request"
            )

            if (
                request
                and hasattr(
                    request,
                    "user"
                )
                and request.user.is_authenticated
            ):

                if (
                    request.user.role
                    != User.MANAGER
                ):

                    data.pop(
                        "procurement_cost",
                        None
                    )

            return data


class MaintenanceRequestSerializer(
    serializers.ModelSerializer
):

    asset_name = serializers.CharField(
        source="asset.name",
        read_only=True
    )

    requested_by_username = serializers.CharField(
        source="requested_by.username",
        read_only=True
    )

    class Meta:
        model = MaintenanceRequest

        fields = [
            "id",
            "asset",
            "asset_name",
            "requested_by",
            "requested_by_username",
            "issue_description",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "requested_by",
            "requested_by_username",
            "status",
            "created_at",
        ]


class WorkOrderSerializer(serializers.ModelSerializer):

    asset_name = serializers.CharField(
        source="maintenance_request.asset.name",
        read_only=True
    )

    approved_by_username = serializers.CharField(
        source="approved_by.username",
        read_only=True
    )

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "maintenance_request",
            "asset_name",
            "approved_by",
            "approved_by_username",
            "work_description",
            "completed",
            "completion_date",
        ]

        read_only_fields = [
            "approved_by",
            "approved_by_username",
        ]

        


class MileageLogSerializer(serializers.ModelSerializer):

    asset_name = serializers.CharField(
        source="asset.name",
        read_only=True
    )

    submitted_by_username = serializers.CharField(
        source="submitted_by.username",
        read_only=True
    )

    class Meta:
        model = MileageLog

        fields = [
            "id",
            "asset",
            "asset_name",
            "submitted_by",
            "submitted_by_username",
            "mileage",
            "submitted_at",
        ]

        read_only_fields = [
            "submitted_by",
            "submitted_by_username",
            "submitted_at",
        ]

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=False
    )

    full_name = serializers.SerializerMethodField()

    class Meta:

        model = User

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "password",
            "role",
        ]

    def get_full_name(
        self,
        obj
    ):

        name = obj.get_full_name()

        return (
            name
            if name
            else obj.username
        )

    def create(
        self,
        validated_data
    ):

        password = validated_data.pop(
            "password"
        )

        user = User(
            **validated_data
        )

        user.set_password(
            password
        )

        user.save()

        return user

    def update(
        self,
        instance,
        validated_data
    ):

        password = validated_data.pop(
            "password",
            None
        )

        for key, value in (
            validated_data.items()
        ):

            setattr(
                instance,
                key,
                value
            )

        if password:

            instance.set_password(
                password
            )

        instance.save()

        return instance
    
class ManagerRequestSerializer(
    serializers.ModelSerializer
):

    asset_name = serializers.CharField(
        source="asset.name",
        read_only=True
    )

    requested_by_username = serializers.CharField(
        source="requested_by.username",
        read_only=True
    )

    class Meta:

        model = MaintenanceRequest

        fields = [
            "id",
            "asset",
            "asset_name",
            "requested_by",
            "requested_by_username",
            "issue_description",
            "status",
            "created_at",
        ]



class AuditLogSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:

        model = AuditLog

        fields = [
            "id",
            "username",
            "action",
            "model_name",
            "object_id",
            "ip_address",
            "timestamp",
            "details",
        ]