import traceback
import logging

from django.http.response import Http404
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import connections
from rest_framework.response import Response
from rest_framework import status, exceptions
from django.utils.translation import gettext as _

from config import settings

logger = logging.getLogger(__name__)

def format_errors(errors):
    if isinstance(errors, dict):
        errors = {
            "message": {
                k: (
                    " ".join([_(str(m)) for m in v])
                    if isinstance(v, (list, tuple))
                    else _(str(v))
                )
                for k, v in errors.items()
            }
        }
    elif isinstance(errors, (list, tuple)):
        errors = {"message": " ".join([_(str(m)) for m in errors])}
    return errors

def set_rollback():
    for db in connections.all():
        if db.settings_dict.get("ATOMIC_REQUESTS") and db.in_atomic_block:
            db.set_rollback(True)

def _extract_file_and_line(exc):
    tb = traceback.extract_tb(exc.__traceback__)
    if not tb:
        return None, None
    last = tb[-1]
    return last.filename, last.lineno

def custom_exception_handler(exc, context):
    request = context.get("request")

    is_ajax = request and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not is_ajax:
        raise exc   

    if isinstance(exc, ObjectDoesNotExist):
        model = getattr(exc, 'model', None)
        model_name = model.__name__ if model else 'Object'
        message = _("%s matching query does not exist.") % model_name
        exc = exceptions.NotFound(detail=message)
    if isinstance(exc, Http404):
        exc = exceptions.NotFound(*exc.args)
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied(*exc.args)

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = format_errors(exc.detail)
                
        else:
            data = {
                "message": _(str(exc.detail))
            }
        
        data.setdefault("success", False)

        set_rollback()

        if settings.DEBUG:
            filename, lineno = _extract_file_and_line(exc)
            data["file"] = filename
            data["line"] = lineno

        return Response(data, status=exc.status_code, headers=headers)

    logger.error("Unhandled exception", exc_info=exc)

    data = {
        "success": False,
        "message": _(str(exc))
    }
    if settings.DEBUG:
            filename, lineno = _extract_file_and_line(exc)
            data["file"] = filename
            data["line"] = lineno

    set_rollback()
    return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
