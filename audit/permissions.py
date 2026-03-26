from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        # Thabbet ennou l-user m-connecti w el Role mte3ou 'ADMIN'
        # (Thabbet f-el Model User mte3ek chnowa esm el field mta' l-role)
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')