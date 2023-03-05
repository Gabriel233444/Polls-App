from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsAdminOrStaff(permissions.BasePermission):
    """
       Allows access only to  Admin or Staff(user type 1 and 2 ) users.

    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.role == 'admin' \
               or request.user.role == 'staff' and request.user.is_staff
        # return request.user and request.user.is_active and request.user.role == 'admin' \
        #        or request.user.role == 'staff' and request.user.is_staff


class IsSuperAdmin(permissions.BasePermission):
    """
       Allows access only to  Admin or Staff(user type 1 and 2 ) users.

    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active and request.user.is_superuser and request.user.is_staff


class IdentityIsVerified(permissions.BasePermission):
    """
       Allows access only to users with verified identity.

    """
    message = 'Please verify your identity to complete this action'

    def has_permission(self, request, view):
        if request.user and request.user.is_active and request.user.email_verified and request.user.password_updated:
            return True
        else:
            raise PermissionDenied(detail=self.message)
