from django.urls import path
from ..endpoints.members import (
    MemberListEndpoint,
    MemberItemEndpoint,
    MemberGroupsEndpoint,
    MemberGroupItemEndpoint,
    MemberPermissionsEndpoint,
    MemberPermissionItemEndpoint,
)

urlpatterns = [
    path('', MemberListEndpoint.as_view()),
    path('<pk>/', MemberItemEndpoint.as_view()),
    path('<member_id>/groups/', MemberGroupsEndpoint.as_view()),
    path('<member_id>/permissions/', MemberPermissionsEndpoint.as_view()),
    path('<member_id>/groups/<pk>/', MemberGroupItemEndpoint.as_view()),
    path('<member_id>/permissions/<pk>/', MemberPermissionItemEndpoint.as_view()),
]
