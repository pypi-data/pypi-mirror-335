from rest_framework.request import Request
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from ..drf.filters import IncludeFilter
from ..drf.views import AuthenticatedEndpoint
from ..models import Member
from ..serializers.member import UserTenantsSerializer

__all__ = [
    'UserTenantListEndpoint',
    'UserTenantItemEndpoint',
]


class UserTenantListEndpoint(ListModelMixin, AuthenticatedEndpoint):
    serializer_class = UserTenantsSerializer
    filter_backends = [IncludeFilter]
    include_prefetch_related_fields = ['groups', 'permissions', 'groups__permissions']
    queryset = Member.objects.select_related('tenant').all()

    def get_queryset(self):
        status = self.request.query_params.get('status')
        queryset = self.queryset.filter(user=self.request.user)
        if status == 'waiting':
            queryset = queryset.filter(status=Member.InviteStatus.WAITING)
        elif status == 'active':
            queryset = queryset.filter(status=Member.InviteStatus.ACTIVE)
        return queryset.all()

    def get(self, request: Request, *args, **kwargs):
        """List all the current user's tenants."""
        return self.list(request, *args, **kwargs)


class UserTenantItemEndpoint(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, AuthenticatedEndpoint):
    serializer_class = UserTenantsSerializer
    queryset = Member.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get(self, request: Request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request: Request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request: Request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
