from rest_framework.permissions import BasePermission

class IsAdminUserStrict(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsStaffUser(BasePermission):
    """
    Permite solo usuarios autenticados con is_staff=True.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)
    
class IsParticipantToken(BasePermission):
    def has_permission(self, request, view):
        auth = getattr(request, "auth", None)
        if not auth:
            return False

        try:
            token_type = auth.get("type")
        except Exception:
            token_type = None

        return token_type == "participant"