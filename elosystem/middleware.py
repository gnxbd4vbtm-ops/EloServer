import json
import logging
import time
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse


LOG_PATH = Path(settings.BASE_DIR) / "request.log"
logger = logging.getLogger("elosystem.request")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = TimedRotatingFileHandler(
        LOG_PATH,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=True,
    )
    handler.suffix = "%Y-%m-%d"
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


class RequestLoggingMiddleware:
    """Log each request into request.log."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.log_path = LOG_PATH

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start_time = time.monotonic()
        response = self.get_response(request)
        duration = time.monotonic() - start_time
        self.log_request(request, response, duration)
        return response

    def log_request(self, request: HttpRequest, response: HttpResponse, duration: float) -> None:
        timestamp = datetime.now(timezone.utc).astimezone().isoformat()
        ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR") or "-"
        if "," in ip:
            ip = ip.split(",")[0].strip()

        protocol = request.META.get("SERVER_PROTOCOL", "HTTP/1.1")
        request_line = f"{request.method} {request.get_full_path()} {protocol}"

        status = getattr(response, "status_code", "-")

        size = response.get("Content-Length")
        if size is None:
            if hasattr(response, "content"):
                try:
                    size = len(response.content)
                except Exception:
                    size = 0
            else:
                size = 0
        else:
            try:
                size = int(size)
            except (TypeError, ValueError):
                size = 0

        xff_chain = request.META.get("HTTP_X_FORWARDED_FOR", "-")
        if xff_chain and xff_chain != "-":
            ip = xff_chain.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "-")

        user_agent = request.META.get("HTTP_USER_AGENT", "-")
        referer = request.META.get("HTTP_REFERER", "-")

        entry = {
            "timestamp": timestamp,
            "remote_addr": ip,
            "x_forwarded_for": xff_chain,
            "request_line": request_line,
            "status": status,
            "response_size": size,
            "user_agent": user_agent,
            "referer": referer,
            "duration_seconds": round(duration, 3),
        }

        try:
            logger.info(json.dumps(entry, ensure_ascii=False))
        except Exception:
            
            pass
