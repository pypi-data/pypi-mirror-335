from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from ..drf.serializers import ModelSerializer
from ..models import Member, UserEmail
from .tenant import TenantSerializer
from .permission import PermissionSerializer
from .group import GroupSerializer
from .user import UserSerializer


class MemberSerializer(ModelSerializer):
    user = UserSerializer(required=False, read_only=True)
    inviter = UserSerializer(required=False, read_only=True)
    groups = GroupSerializer(required=False, many=True, read_only=True)
    permissions = PermissionSerializer(required=False, many=True, read_only=True)

    class Meta:
        model = Member
        exclude = ['tenant']
        include_only_fields = ['user', 'groups', 'permissions']


class MemberInviteSerializer(ModelSerializer):
    invite_email = serializers.EmailField(required=True)

    class Meta:
        model = Member
        fields = ['name', 'invite_email', 'is_owner']

    def validate_invite_email(self, email: str):
        view = self.context['view']
        tenant_id = view.get_tenant_id()
        if Member.objects.filter(tenant_id=tenant_id, invite_email=email).count():
            raise ValidationError(_('This email has already been invited.'))
        return email

    def create(self, validated_data):
        email = validated_data['invite_email']
        try:
            user_email = UserEmail.objects.get_by_email(email)
            validated_data['user_id'] = user_email.user_id
            validated_data['status'] = Member.InviteStatus.WAITING
        except UserEmail.DoesNotExist:
            pass
        request = self.context['request']
        validated_data['inviter'] = request.user
        return super().create(validated_data)


class MemberDetailSerializer(ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Member
        exclude = ['tenant', 'user']


class UserTenantsSerializer(ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Member
        exclude = ['user', 'inviter', 'invite_email']
        read_only_fields = [
            'inviter',
            'invite_email',
            'is_owner',
            'created_at',
        ]
        include_only_fields = ['groups', 'permissions']

    def validate_status(self, status):
        # user agree to join the tenant
        if status != Member.InviteStatus.ACTIVE:
            raise ValidationError(_('Invalid status value.'))
        return status
