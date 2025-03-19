from rest_framework.mixins import ListModelMixin
from rest_framework.request import Request
from ..drf.views import Endpoint
from ..models import Permission
from ..serializers.permission import PermissionSerializer


__all__ = ['PermissionListEndpoint']


class PermissionListEndpoint(ListModelMixin, Endpoint):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    pagination_class = None

    def get(self, request: Request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
