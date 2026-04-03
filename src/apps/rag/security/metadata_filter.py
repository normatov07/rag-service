from __future__ import annotations

from copy import deepcopy


class MetadataSecurityFilter:
    ALLOWED_KEYS = {
        "type",
        "url",
        "url_unique_id",
        "source",
        "format",
        "id",
        "uuid",
        "permission",
        "department",
        "division",
        "user_id",
        "group",
    }

    @classmethod
    def sanitize(cls, metadata: dict | None) -> dict:
        if not metadata:
            return {}
        data = deepcopy(metadata)
        sanitized: dict = {}
        for key, value in data.items():
            if key not in cls.ALLOWED_KEYS:
                continue
            sanitized_value = cls._sanitize_value(value)
            if sanitized_value in (None, ""):
                continue
            sanitized[key] = sanitized_value
        return sanitized

    @classmethod
    def _sanitize_value(cls, value):
        if isinstance(value, str):
            return value.replace("\x00", "")
        if isinstance(value, list):
            return [cls._sanitize_value(item) for item in value]
        if isinstance(value, dict):
            return {k: cls._sanitize_value(v) for k, v in value.items()}
        return value

    @classmethod
    def with_user_scope(cls, metadata: dict, user: dict) -> dict:
        secured = dict(metadata)

        department = (user.get("department") or {}).get("code") if isinstance(user, dict) else None
        division = (user.get("division") or {}).get("code") if isinstance(user, dict) else None
        group_name = (user.get("group") or {}).get("name") if isinstance(user, dict) else None
        user_id = user.get("id") if isinstance(user, dict) else None

        if department:
            secured["department"] = department
        if division:
            secured["division"] = division
        if group_name:
            secured["group"] = group_name
        if user_id:
            secured["user_id"] = user_id

        return secured

    @classmethod
    def user_scope(cls, user: dict | None) -> dict:
        if not isinstance(user, dict):
            return {}

        scope: dict = {}
        department = (user.get("department") or {}).get("code")
        division = (user.get("division") or {}).get("code")
        group_name = (user.get("group") or {}).get("name")
        user_id = user.get("id")

        if department:
            scope["department"] = department
        if division:
            scope["division"] = division
        if group_name:
            scope["group"] = group_name
        if user_id is not None:
            scope["user_id"] = user_id

        return scope

    @classmethod
    def is_payload_allowed_for_user(cls, payload: dict | None, user: dict | None) -> bool:
        if not isinstance(payload, dict):
            return False

        scope = cls.user_scope(user)
        if not scope:
            return True

        for key, user_value in scope.items():
            payload_value = payload.get(key)
            if payload_value in (None, ""):
                # Unscoped documents stay visible within tenant.
                continue
            if str(payload_value) != str(user_value):
                return False

        return True
