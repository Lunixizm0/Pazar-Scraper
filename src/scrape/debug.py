"""Opt-in, stderr-only diagnostics for scraper execution."""

import json
import sys
from contextvars import ContextVar
from time import perf_counter
from typing import Any

_debug_enabled: ContextVar[bool] = ContextVar("scrape_debug_enabled", default=False)
_http_body_enabled: ContextVar[bool] = ContextVar(
    "scrape_http_body_enabled", default=False
)


def set_debug(enabled: bool, *, http_body: bool = False) -> None:
    """Enable or disable debug output for the current execution context."""
    _debug_enabled.set(enabled)
    _http_body_enabled.set(enabled and http_body)


def is_debug_enabled() -> bool:
    return _debug_enabled.get()


def _debug_http_body(response: Any, *, method: str, url: str) -> None:
    if not _http_body_enabled.get():
        return

    try:
        body = response.text
    except Exception:
        content = getattr(response, "content", b"") or b""
        body = content.decode("utf-8", errors="replace")

    try:
        formatted_body = json.dumps(json.loads(body), ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        formatted_body = body

    print(
        f"[debug] http.body.start: method={method!r} url={url!r}", file=sys.stderr
    )
    print(formatted_body, file=sys.stderr)
    print(
        f"[debug] http.body.end: method={method!r} url={url!r}", file=sys.stderr
    )


def _display(value: Any) -> str:
    text = repr(value)
    return text if len(text) <= 240 else f"{text[:237]}..."


def debug(event: str, **details: Any) -> None:
    if not is_debug_enabled():
        return
    suffix = " ".join(f"{key}={_display(value)}" for key, value in details.items())
    print(f"[debug] {event}{': ' if suffix else ''}{suffix}", file=sys.stderr)


def request_get(requests_module: Any, url: str, **kwargs: Any) -> Any:
    """Perform and describe an HTTP GET, without logging request headers."""
    started = perf_counter()
    debug("http.request", url=url, params=kwargs.get("params"), timeout=kwargs.get("timeout"))
    try:
        response = requests_module.get(url, **kwargs)
    except Exception as exc:
        debug("http.error", url=url, error=f"{type(exc).__name__}: {exc}", elapsed_ms=round((perf_counter() - started) * 1000, 1))
        raise

    debug(
        "http.response",
        url=url,
        status=response.status_code,
        bytes=len(getattr(response, "content", b"") or b""),
        elapsed_ms=round((perf_counter() - started) * 1000, 1),
    )
    _debug_http_body(response, method="GET", url=url)
    return response


class DebugRequests:

    def __init__(self, requests_module: Any) -> None:
        self._requests = requests_module

    def get(self, url: str, **kwargs: Any) -> Any:
        return request_get(self._requests, url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        started = perf_counter()
        debug("http.request", method="POST", url=url, params=kwargs.get("params"), timeout=kwargs.get("timeout"))
        try:
            response = self._requests.post(url, **kwargs)
        except Exception as exc:
            debug("http.error", method="POST", url=url, error=f"{type(exc).__name__}: {exc}", elapsed_ms=round((perf_counter() - started) * 1000, 1))
            raise
        debug("http.response", method="POST", url=url, status=response.status_code, elapsed_ms=round((perf_counter() - started) * 1000, 1))
        _debug_http_body(response, method="POST", url=url)
        return response
