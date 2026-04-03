from django.test import SimpleTestCase, override_settings

from api.rag.utils import TenantResolver


@override_settings(RAG_DEFAULT_TENANT_ID="default-tenant")
class TenantResolverTests(SimpleTestCase):
    def test_uses_requested_tenant_for_superuser(self):
        tenant = TenantResolver.resolve(
            user={"is_superuser": True, "tenant_id": "tenant-a"},
            requested_tenant_id="tenant-b",
        )
        self.assertEqual(tenant, "tenant-b")

    def test_uses_user_tenant_for_non_superuser(self):
        tenant = TenantResolver.resolve(
            user={"is_superuser": False, "tenant_id": "tenant-a"},
            requested_tenant_id="tenant-b",
        )
        self.assertEqual(tenant, "tenant-a")

    def test_uses_default_when_no_tenant_info(self):
        tenant = TenantResolver.resolve(user={}, requested_tenant_id=None)
        self.assertEqual(tenant, "default-tenant")
