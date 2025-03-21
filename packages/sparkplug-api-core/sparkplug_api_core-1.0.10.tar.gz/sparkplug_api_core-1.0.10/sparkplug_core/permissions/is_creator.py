# django
from django.views import View

# contrib
from rest_framework.request import Request

# app
from .is_authenticated import IsAuthenticated


class IsCreator(IsAuthenticated):
    def has_object_permission(
        self,
        request: Request,
        view: View,  # noqa: ARG002
        obj,  # noqa: ANN001
    ) -> bool:
        return obj.creator_id == request.user.id
