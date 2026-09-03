import json
import os
import sys
from contextvars import ContextVar
from time import perf_counter
from typing import Any

_LEVELS = {"ERROR": 40, "WARN": 30, "INFO": 20, "DEBUG": 10}

# ANSI colors
_COLORS = {
    "ERROR": "\033[1;31m",  # bold red
    "WARN": "\033[1;33m",  # bold yellow
    "INFO": "\033[1;36m",  # bold cyan
    "DEBUG": "\033[2;90m",  # dim gray
}
_RESET = "\033[0m"

_debug_enabled: ContextVar[bool] = ContextVar("scrape_debug_enabled", default=False)
_http_body_enabled: ContextVar[bool] = ContextVar(
    "scrape_http_body_enabled", default=False
)
_min_level: ContextVar[str] = ContextVar("scrape_debug_level", default="DEBUG")


def _use_color() -> bool:
    return bool(getattr(sys.stderr, "isatty", lambda: False)()) and not os.environ.get(
        "NO_COLOR"
    )


def set_debug(enabled: bool, *, http_body: bool = False, level: str = "DEBUG") -> None:

    _debug_enabled.set(enabled)
    _http_body_enabled.set(enabled and http_body)
    _min_level.set(level.upper() if level.upper() in _LEVELS else "DEBUG")


def is_debug_enabled() -> bool:
    return _debug_enabled.get()


def _emit(level: str, message: str) -> None:
    if not is_debug_enabled():
        return
    if _LEVELS.get(level, 10) < _LEVELS.get(_min_level.get(), 20):
        return
    tag = f"{level:<5}"
    if _use_color():
        print(
            f"{_COLORS[level]}[{tag}]{_RESET} {message}",
            file=sys.stderr,
        )
    else:
        print(f"[{tag}] {message}", file=sys.stderr)


def _body_text(response: Any) -> str:
    try:
        body = response.text
    except Exception:
        content = getattr(response, "content", b"") or b""
        body = content.decode("utf-8", errors="replace")
    try:
        return json.dumps(json.loads(body), ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return body


def _http_body(response: Any, *, method: str, url: str) -> None:
    if not _http_body_enabled.get():
        return
    print(f"[http.body] {method} {url}", file=sys.stderr)
    print(_body_text(response), file=sys.stderr)


def _display(value: Any) -> str:
    text = repr(value)
    return text if len(text) <= 240 else f"{text[:237]}..."


def debug(event: str, *, level: str = "DEBUG", **details: Any) -> None:
    """Log an event at the given (default DEBUG) severity."""
    suffix = " ".join(f"{key}={_display(value)}" for key, value in details.items())
    _emit(level, f"{event}{': ' if suffix else ''}{suffix}")


def error(event: str, **details: Any) -> None:
    debug(event, level="ERROR", **details)


def warn(event: str, **details: Any) -> None:
    debug(event, level="WARN", **details)


def info(event: str, **details: Any) -> None:
    debug(event, level="INFO", **details)


def _request_common(requests_module: Any, method: str, url: str, kwargs: Any) -> Any:
    started = perf_counter()
    body = kwargs.get("json")
    if body is None and kwargs.get("data") is not None:
        try:
            body = json.loads(kwargs["data"])
        except (TypeError, ValueError):
            body = kwargs["data"]
    debug(
        "http.request",
        method=method,
        url=url,
        params=kwargs.get("params"),
        timeout=kwargs.get("timeout"),
        body=_display(body) if body is not None else None,
    )
    try:
        response = getattr(requests_module, method.lower())(url, **kwargs)
    except Exception as exc:
        error(
            "http.error",
            method=method,
            url=url,
            error=f"{type(exc).__name__}: {exc}",
            elapsed_ms=round((perf_counter() - started) * 1000, 1),
        )
        raise

    elapsed_ms = round((perf_counter() - started) * 1000, 1)
    if response.status_code >= 400:
        error(
            "http.response",
            method=method,
            url=url,
            status=response.status_code,
            elapsed_ms=elapsed_ms,
        )
    else:
        debug(
            "http.response",
            method=method,
            url=url,
            status=response.status_code,
            bytes=len(getattr(response, "content", b"") or b""),
            elapsed_ms=elapsed_ms,
        )
    _http_body(response, method=method, url=url)
    return response


def request_get(requests_module: Any, url: str, **kwargs: Any) -> Any:
    return _request_common(requests_module, "GET", url, kwargs)


class DebugRequests:
    def __init__(self, requests_module: Any) -> None:
        self._requests = requests_module

    def get(self, url: str, **kwargs: Any) -> Any:
        return _request_common(self._requests, "GET", url, kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        return _request_common(self._requests, "POST", url, kwargs)
