from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManager(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "MANAGER"
        )
class IsAuditorReadOnly(BasePermission):

    def has_permission(self, request, view):

        if request.user.role == "AUDITOR":
            return request.method in SAFE_METHODS

        return True
class CanCreateMaintenanceRequest(BasePermission):

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return request.user.role in [
            "STAFF",
            "MANAGER"
        ]
class CanSubmitMileage(BasePermission):

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return request.user.role in [
            "STAFF",
            "MANAGER"
        ]