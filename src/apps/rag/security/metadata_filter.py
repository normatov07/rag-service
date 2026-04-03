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
        return {k: v for k, v in data.items() if k in cls.ALLOWED_KEYS and v not in (None, "")}

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
