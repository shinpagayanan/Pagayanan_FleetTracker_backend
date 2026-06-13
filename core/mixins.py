from .audit import log_event


class AuditMixin:

    audit_model_name = ""

    def audit_create(
        self,
        obj
    ):
        log_event(
            self.request,
            "CREATE",
            self.audit_model_name,
            obj.id
        )

    def audit_update(
        self,
        obj
    ):
        log_event(
            self.request,
            "UPDATE",
            self.audit_model_name,
            obj.id
        )

    def audit_delete(
        self,
        obj_id
    ):
        log_event(
            self.request,
            "DELETE",
            self.audit_model_name,
            obj_id
        )

    def perform_create(
        self,
        serializer
    ):
        obj = serializer.save()

        self.audit_create(obj)

        return obj

    def perform_update(
        self,
        serializer
    ):
        obj = serializer.save()

        self.audit_update(obj)

        return obj

    def perform_destroy(
        self,
        instance
    ):
        obj_id = instance.id

        instance.delete()

        self.audit_delete(obj_id)