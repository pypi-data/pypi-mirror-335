from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiExample, extend_schema
from drf_spectacular.extensions import OpenApiViewExtension


class AuthResponseSerializer(serializers.Serializer):
    next = serializers.CharField()


class PasswordLogInEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.auth.PasswordLogInEndpoint'

    def view_replacement(self):
        class FixedPasswordLogInEndpoint(self.target_class):
            @extend_schema(summary='Log In', responses={200: AuthResponseSerializer})
            def post(self, *args, **kwargs):
                pass

        return FixedPasswordLogInEndpoint


class LogoutEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.auth.LogoutEndpoint'

    def view_replacement(self):
        class FixedLogoutEndpoint(self.target_class):
            @extend_schema(summary='Log Out', request=None, responses={200: AuthResponseSerializer})
            def post(self, *args, **kwargs):
                pass

        return FixedLogoutEndpoint


class SignupConfirmEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.auth.SignupConfirmEndpoint'

    def view_replacement(self):
        class FixedSignupConfirmEndpoint(self.target_class):
            @extend_schema(summary='Sign Up', responses={200: AuthResponseSerializer})
            def post(self, *args, **kwargs):
                pass

        return FixedSignupConfirmEndpoint


class SignupRequestEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.auth.SignupRequestEndpoint'

    def view_replacement(self):
        class FixedSignupRequestEndpoint(self.target_class):
            @extend_schema(summary='Request to Sign-up', responses={204: None})
            def post(self, *args, **kwargs):
                pass

        return FixedSignupRequestEndpoint


class PasswordResetEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.password.PasswordResetEndpoint'

    def view_replacement(self):
        class FixedPasswordResetEndpoint(self.target_class):
            @extend_schema(summary='Password Reset', responses={200: AuthResponseSerializer})
            def post(self, *args, **kwargs):
                pass

        return FixedPasswordResetEndpoint


class PasswordForgotEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.password.PasswordForgotEndpoint'

    def view_replacement(self):
        class FixedPasswordForgotEndpoint(self.target_class):
            @extend_schema(summary='Password Forgot', responses={204: None})
            def post(self, *args, **kwargs):
                pass

        return FixedPasswordForgotEndpoint


id_parameter = OpenApiParameter(
    'id',
    type=str,
    location=OpenApiParameter.PATH,
    required=True,
)

member_id_parameter = OpenApiParameter(
    'member_id',
    type=str,
    location=OpenApiParameter.PATH,
    required=True,
)


class MemberGroupsEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.members.MemberGroupsEndpoint'

    def view_replacement(self):
        class Fixed(self.target_class):
            @extend_schema(
                operation_id='members_groups_list',
                summary='List Member Groups',
                parameters=[member_id_parameter],
            )
            def get(self, *args, **kwargs):
                pass

            @extend_schema(
                operation_id='members_groups_reset',
                summary='Reset Member Groups',
                parameters=[member_id_parameter],
                request=OpenApiTypes.UUID,
                responses={204: None},
                examples=[
                    OpenApiExample(
                        'Example 1',
                        value=['497f6eca-6276-4993-bfeb-53cbbbba6f08'],
                        request_only=True,
                    ),
                ],
            )
            def post(self, *args, **kwargs):
                pass

        return Fixed


class MemberGroupItemEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.members.MemberGroupItemEndpoint'

    def view_replacement(self):
        class Fixed(self.target_class):
            @extend_schema(
                operation_id='members_groups_remove',
                summary='Remove Member Group',
                parameters=[member_id_parameter, id_parameter],
            )
            def delete(self, *args, **kwargs):
                pass

        return Fixed


class MemberPermissionsEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.members.MemberPermissionsEndpoint'

    def view_replacement(self):
        class Fixed(self.target_class):
            @extend_schema(
                operation_id='members_permissions_list',
                summary='List Member Permissions',
                parameters=[member_id_parameter],
            )
            def get(self, *args, **kwargs):
                pass

            @extend_schema(
                operation_id='members_permissions_reset',
                summary='Reset Member Permissions',
                parameters=[member_id_parameter],
                request=OpenApiTypes.UUID,
                responses={204: None},
                examples=[
                    OpenApiExample(
                        'Example 1',
                        value=['tenant.read', 'tenant.admin'],
                        request_only=True,
                    ),
                ],
            )
            def post(self, *args, **kwargs):
                pass

        return Fixed


class MemberPermissionItemEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.members.MemberPermissionItemEndpoint'

    def view_replacement(self):
        class Fixed(self.target_class):
            @extend_schema(
                operation_id='members_permissions_remove',
                summary='Remove Member Permission',
                parameters=[member_id_parameter, id_parameter],
            )
            def delete(self, *args, **kwargs):
                pass

        return Fixed
