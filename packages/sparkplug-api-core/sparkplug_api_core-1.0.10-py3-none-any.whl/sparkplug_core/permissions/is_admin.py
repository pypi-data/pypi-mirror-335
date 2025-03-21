# django
from django.views import View

# contrib
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsAdmin(BasePermission):
    """
    Allows access only to admin users.

    User must be active, authenticated, and staff.
    """

    def has_permission(
        self,
        request: Request,
        view: View,  # noqa: ARG002
    ) -> bool:
        user = request.user

        if not user:
            return False

        return all([
            user.is_active,
            user.is_authenticated,
            user.is_staff,
        ])
