import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("vidyavana")


class ServiceUnavailableError(drf_exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable. Please try again shortly."
    default_code = "service_unavailable"


def _flatten_errors(detail):
    """Normalize DRF's error detail (which can be a dict, list, or string) into a flat list."""
    errors = []

    if isinstance(detail, dict):
        for field, messages in detail.items():
            if isinstance(messages, (list, tuple)):
                for message in messages:
                    errors.append({"field": field, "message": str(message)})
            else:
                errors.append({"field": field, "message": str(messages)})
    elif isinstance(detail, (list, tuple)):
        for message in detail:
            errors.append({"field": "non_field_errors", "message": str(message)})
    else:
        errors.append({"field": "detail", "message": str(detail)})

    return errors


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to produce a consistent
    { success, error: { code, message, errors } } envelope for every error response.
    """
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = drf_exceptions.PermissionDenied()

    response = exception_handler(exc, context)

    view = context.get("view")
    request = context.get("request")
    view_name = view.__class__.__name__ if view else "UnknownView"

    if response is not None:
        error_code = getattr(exc, "default_code", "error")
        detail = getattr(exc, "detail", "An error occurred")
        message = "Validation failed" if isinstance(detail, (dict, list)) else str(detail)

        payload = {
            "success": False,
            "error": {
                "code": error_code,
                "status_code": response.status_code,
                "message": message,
                "errors": _flatten_errors(detail),
            },
        }
        response.data = payload

        log_level = logging.WARNING if response.status_code < 500 else logging.ERROR
        logger.log(
            log_level,
            "%s failed on %s: %s [%s]",
            request.method if request else "UNKNOWN",
            view_name,
            response.status_code,
            payload["error"]["errors"],
        )
        return response

    # Unhandled (non-DRF) exception -> 500
    logger.exception("Unhandled exception in %s: %s", view_name, exc)
    return Response(
        {
            "success": False,
            "error": {
                "code": "internal_server_error",
                "status_code": 500,
                "message": "An unexpected error occurred. Our team has been notified.",
                "errors": [],
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
