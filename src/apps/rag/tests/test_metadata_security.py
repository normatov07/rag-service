from django.test import SimpleTestCase

from apps.rag.security.metadata_filter import MetadataSecurityFilter


class MetadataSecurityFilterTests(SimpleTestCase):
    def test_sanitize_keeps_only_allowed_keys(self):
        source = {
            "type": "file",
            "department": "DEP-1",
            "group": "admins",
            "unknown": "drop-me",
            "empty": "",
        }

        sanitized = MetadataSecurityFilter.sanitize(source)

        self.assertIn("type", sanitized)
        self.assertIn("department", sanitized)
        self.assertIn("group", sanitized)
        self.assertNotIn("unknown", sanitized)
        self.assertNotIn("empty", sanitized)

    def test_with_user_scope_overrides_filter_values(self):
        metadata = {
            "department": "OTHER",
            "division": "OTHER",
            "group": "OTHER",
            "user_id": 999,
        }
        user = {
            "id": 12,
            "department": {"code": "DEP-12"},
            "division": {"code": "DIV-34"},
            "group": {"name": "ops"},
        }

        secured = MetadataSecurityFilter.with_user_scope(metadata, user)

        self.assertEqual(secured["department"], "DEP-12")
        self.assertEqual(secured["division"], "DIV-34")
        self.assertEqual(secured["group"], "ops")
        self.assertEqual(secured["user_id"], 12)
