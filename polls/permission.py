from rest_framework import permissions
# from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response


def permission_required(permission_name, raise_exception=False):
    class PermissionRequired(permissions.BasePermission):

        message = "You do not have permission to perform this action."

        def has_permission(self, request, view):
            if not request.user.has_perm(permission_name):
                if raise_exception:
                    return Response({"detail": self.message}, status=status.HTTP_403_FORBIDDEN)
                return False
            return True
    return PermissionRequired
