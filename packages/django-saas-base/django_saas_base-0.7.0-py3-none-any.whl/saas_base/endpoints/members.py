from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.mixins import ListModelMixin
from ..settings import saas_settings
from ..drf.views import TenantEndpoint
from ..drf.filters import TenantIdFilter, IncludeFilter
from ..mail import SendEmailMixin
from ..serializers.member import (
    MemberSerializer,
    MemberInviteSerializer,
    MemberDetailSerializer,
)
from ..serializers.group import GroupSerializer
from ..serializers.permission import PermissionSerializer
from ..models import Member, Group, Permission
from ..signals import member_invited

__all__ = [
    'MemberListEndpoint',
    'MemberItemEndpoint',
    'MemberGroupsEndpoint',
    'MemberPermissionsEndpoint',
    'MemberGroupItemEndpoint',
    'MemberPermissionItemEndpoint',
]


class MemberListEndpoint(SendEmailMixin, ListModelMixin, TenantEndpoint):
    email_template_id = 'invite_member'
    email_subject = _("You've Been Invited to Join %s")

    serializer_class = MemberSerializer
    filter_backends = [TenantIdFilter, IncludeFilter]
    queryset = Member.objects.all()
    resource_name = 'tenant'
    resource_http_method_actions = {
        'GET': 'read',
        'POST': 'admin',
    }
    include_select_related_fields = ['user']
    include_prefetch_related_fields = ['groups', 'permissions', 'groups__permissions']

    def get_email_subject(self):
        return self.email_subject % str(self.request.tenant)

    def get(self, request: Request, *args, **kwargs):
        """List all members in the tenant."""
        return self.list(request, *args, **kwargs)

    def post(self, request: Request, *args, **kwargs):
        """Invite a member to join the tenant."""
        tenant_id = self.get_tenant_id()
        context = self.get_serializer_context()
        serializer = MemberInviteSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        member = serializer.save(tenant_id=tenant_id, inviter=request.user)

        member_invited.send(self.__class__, member=member, request=request)
        self.send_email(
            [member.invite_email],
            inviter=request.user,
            member=member,
            tenant=request.tenant,
            invite_link=saas_settings.MEMBER_INVITE_LINK % str(member.id),
        )
        data = MemberSerializer(member).data
        return Response(data)


class MemberItemEndpoint(TenantEndpoint):
    serializer_class = MemberDetailSerializer
    queryset = Member.objects.all()
    resource_name = 'tenant'

    def get(self, request: Request, *args, **kwargs):
        """Retrieve the information of a member."""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.prefetch_related('groups', 'permissions', 'groups__permissions')
        member = self.get_object_or_404(queryset, pk=kwargs['pk'])
        self.check_object_permissions(request, member)
        serializer = self.get_serializer(member)
        return Response(serializer.data)

    def delete(self, request: Request, *args, **kwargs):
        """Remove a member from the tenant."""
        queryset = self.filter_queryset(self.get_queryset())
        member = self.get_object_or_404(queryset, pk=kwargs['pk'])
        self.check_object_permissions(request, member)
        if member.is_owner:
            queryset = Member.objects.filter(tenant_id=self.get_tenant_id(), is_owner=True)
            if not queryset.count():
                raise PermissionDenied(_('The tenant should contain at lease 1 owner.'))
        member.delete()
        return Response(status=204)


class _MemberEndpoint(TenantEndpoint):
    resource_http_method_actions = {
        'GET': 'read',
        'POST': 'admin',
        'DELETE': 'admin',
    }

    def get_member(self, member_id) -> Member:
        try:
            member = Member.objects.get_from_cache_by_pk(member_id)
            if member.tenant_id != self.get_tenant_id():
                raise NotFound()
        except Member.DoesNotExist:
            raise NotFound()
        self.check_object_permissions(self.request, member)
        return member

    def list(self, request: Request, *args, **kwargs):
        member = self.get_member(kwargs['member_id'])
        queryset = self.get_queryset().filter(member=member)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def replace(self, request: Request, field_name: str, **kwargs):
        member = self.get_member(kwargs['member_id'])
        queryset = self.filter_queryset(self.get_queryset())
        items = queryset.filter(pk__in=request.data).all()
        getattr(member, field_name).set(items)
        return Response(status=204)

    def destroy(self, request: Request, field_name: str, **kwargs):
        obj = self.get_object_or_404(self.get_queryset(), pk=kwargs['pk'])
        member = self.get_member(kwargs['member_id'])
        if obj.member_id != member.pk:
            raise NotFound()
        getattr(member, field_name).remove(obj)
        return Response(status=204)


class MemberGroupsEndpoint(_MemberEndpoint):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def get(self, request: Request, *args, **kwargs):
        """List all groups of the selected member."""
        return self.list(request, *args, **kwargs)

    def post(self, request: Request, *args, **kwargs):
        """Reset groups of the selected member."""
        return self.replace(request, field_name='groups', **kwargs)


class MemberPermissionsEndpoint(_MemberEndpoint):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()

    def get(self, request: Request, *args, **kwargs):
        """List all permissions of the selected member."""
        return self.list(request, *args, **kwargs)

    def post(self, request: Request, *args, **kwargs):
        """Reset permissions of the selected member."""
        return self.replace(request, field_name='permissions', **kwargs)


class MemberGroupItemEndpoint(_MemberEndpoint):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def delete(self, request: Request, *args, **kwargs):
        """Remove a group of the selected member."""
        return self.destroy(request, field_name='groups', **kwargs)


class MemberPermissionItemEndpoint(_MemberEndpoint):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()

    def delete(self, request: Request, *args, **kwargs):
        """Remove a permission of the selected member."""
        return self.destroy(request, field_name='permissions', **kwargs)
