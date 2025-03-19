from django.urls import path
from ..endpoints.user_tenants import (
    UserTenantListEndpoint,
    UserTenantItemEndpoint,
)

urlpatterns = [
    path('', UserTenantListEndpoint.as_view()),
    path('<pk>/', UserTenantItemEndpoint.as_view()),
]
