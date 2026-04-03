from __future__ import annotations

from django.conf import settings


class TenantResolver:
    @staticmethod
    def resolve(user: dict | None, requested_tenant_id: str | None = None) -> str:
        user_tenant = None
        if isinstance(user, dict):
            user_tenant = user.get("tenant_id")
            tenant_obj = user.get("tenant")
            if not user_tenant and isinstance(tenant_obj, dict):
                user_tenant = tenant_obj.get("id") or tenant_obj.get("code")

            if user.get("is_superuser"):
                return requested_tenant_id or user_tenant or settings.RAG_DEFAULT_TENANT_ID

            if user_tenant:
                return user_tenant

        return requested_tenant_id or settings.RAG_DEFAULT_TENANT_ID
