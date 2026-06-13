from .models import AuditLog


def log_event(
    request,
    action,
    model_name,
    object_id="",
    details=""
):

    AuditLog.objects.create(

        user=(
            request.user
            if request.user.is_authenticated
            else None
        ),

        action=action,

        model_name=model_name,

        object_id=str(object_id),

        ip_address=request.META.get(
            "REMOTE_ADDR"
        ),

        details=details,
    )