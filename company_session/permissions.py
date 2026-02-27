from rest_framework.permissions import BasePermission


class IsAdminUserToken(BasePermission):
    """
    Permite usuarios reales del sistema (CustomUser).
    Un participant token NO tiene request.user autenticado como usuario real.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsParticipantToken(BasePermission):
    def has_permission(self, request, view):
        return isinstance(getattr(request, "auth", None), dict) and request.auth.get("type") == "participant"

