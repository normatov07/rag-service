from config.permissions import HasUserPermission


class CanQueryRagPermission(HasUserPermission):
    required_permissions = ["can_rag_query"]


class CanReembedRagPermission(HasUserPermission):
    required_permissions = ["can_rag_reembed_manage"]
