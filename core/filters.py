import django_filters

from .models import Asset
from .models import MaintenanceRequest

class AssetFilter(django_filters.FilterSet):

    purchase_date_from = django_filters.DateFilter(
        field_name="purchase_date",
        lookup_expr="gte"
    )

    purchase_date_to = django_filters.DateFilter(
        field_name="purchase_date",
        lookup_expr="lte"
    )

    class Meta:
        model = Asset

        fields = [
            "asset_type",
            "status",
        ]   
class MaintenanceRequestFilter(
    django_filters.FilterSet
):

    created_from = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="gte"
    )

    created_to = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="lte"
    )

    class Meta:
        model = MaintenanceRequest

        fields = [
            "status",
        ]