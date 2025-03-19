from typing import Type, Optional
from django.apps import apps
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .member import Member
from ..db import CachedManager
from ..settings import saas_settings


class TenantManager(CachedManager):
    natural_key = ['slug']

    def create(self, slug: str, owner: Optional[AbstractUser] = None, **kwargs):
        kwargs.setdefault('region', saas_settings.DEFAULT_REGION)
        tenant = super().create(slug=slug, owner=owner, **kwargs)
        # initial with owner membership
        if owner:
            name = owner.get_full_name() or owner.get_username()
            Member.objects.update_or_create(
                user=owner,
                tenant=tenant,
                defaults={
                    'name': name,
                    'is_owner': True,
                    'status': Member.InviteStatus.ACTIVE,
                },
            )
        return tenant

    def get_by_slug(self, slug: str):
        return self.get_from_cache_by_natural_key(slug)


class AbstractTenant(models.Model):
    slug = models.SlugField(
        unique=True,
        help_text='Identity of the tenant, e.g. <slug>.example.com',
    )
    region = models.CharField(max_length=24, blank=True, default='')
    environment = models.CharField(max_length=48, blank=True, default='')
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    objects = TenantManager()

    class Meta:
        verbose_name = _('tenant')
        verbose_name_plural = _('tenants')
        abstract = True

    def __str__(self):
        return self.slug

    def natural_key(self):
        return (self.slug,)


class Tenant(AbstractTenant):
    objects = TenantManager['Tenant']()

    class Meta(AbstractTenant.Meta):
        swappable = 'SAAS_TENANT_MODEL'
        db_table = 'saas_tenant'
        ordering = ['created_at']


def get_tenant_model() -> Type[Tenant]:
    return apps.get_model(settings.SAAS_TENANT_MODEL)
