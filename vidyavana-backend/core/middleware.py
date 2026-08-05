import logging
import time

logger = logging.getLogger("vidyavana")


class RequestLoggingMiddleware:
    """Logs method, path, status code, and duration for every request under /api/."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start_time) * 1000

        if request.path.startswith("/api/"):
            log_level = logging.INFO if response.status_code < 400 else logging.WARNING
            logger.log(
                log_level,
                "%s %s -> %s (%.2fms)",
                request.method,
                request.get_full_path(),
                response.status_code,
                duration_ms,
            )

        return response
