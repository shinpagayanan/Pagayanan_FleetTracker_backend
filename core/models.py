
from django.db import models
from django.contrib.auth.models import AbstractUser


# ==================================================
# USER
# ==================================================

class User(AbstractUser):
    STAFF = "STAFF"
    AUDITOR = "AUDITOR"
    MANAGER = "MANAGER"

    ROLE_CHOICES = [
        (STAFF, "Staff"),
        (AUDITOR, "Auditor"),
        (MANAGER, "Manager"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STAFF
    )

    def __str__(self):
        return self.username


# ==================================================
# ASSET
# Vehicles and IT Equipment
# ==================================================

class Asset(models.Model):
    VEHICLE = "VEHICLE"
    IT = "IT"

    TYPE_CHOICES = [
        (VEHICLE, "Vehicle"),
        (IT, "IT Equipment"),
    ]

    asset_code = models.CharField(
        max_length=30,
        unique=True
    )

    name = models.CharField(max_length=100)

    asset_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    photo = models.ImageField(
        upload_to="assets/",
        blank=True,
        null=True
    )

    purchase_date = models.DateField()

    procurement_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        default="ACTIVE"
    )

    plate_number = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    current_mileage = models.PositiveIntegerField(
        default=0
    )

    maintenance_interval = models.PositiveIntegerField(
        default=5000
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_assets"
    )

    def __str__(self):
        return self.name



class MaintenanceRequest(models.Model):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (COMPLETED, "Completed"),
    ]

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="requests"
    )

    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submitted_requests"
    )

    issue_description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Request #{self.id}"




class WorkOrder(models.Model):
    maintenance_request = models.OneToOneField(
        MaintenanceRequest,
        on_delete=models.CASCADE
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="approved_orders"
    )

    work_description = models.TextField()

    completed = models.BooleanField(
        default=False
    )

    completion_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"WO-{self.id}"

class MileageLog(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        limit_choices_to={"asset_type": "VEHICLE"}
    )

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    mileage = models.PositiveIntegerField()

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.asset.name} - {self.mileage}"
    
class AuditLog(models.Model):

    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("LOGIN", "Login"),
        ("APPROVE", "Approve"),
        ("REJECT", "Reject"),
        ("COMPLETE", "Complete"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    model_name = models.CharField(
        max_length=100
    )

    object_id = models.CharField(
        max_length=50,
        blank=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    details = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f"{self.timestamp} "
            f"{self.user} "
            f"{self.action}"
        )