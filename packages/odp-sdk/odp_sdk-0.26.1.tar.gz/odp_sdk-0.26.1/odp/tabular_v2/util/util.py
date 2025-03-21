import re
import time
from contextlib import contextmanager
from contextvars import ContextVar
from math import log2
from typing import Callable

IEC_UNITS = ["KiB", "MiB", "GiB", "TiB"]


_RE_ID_AND_DOTS = re.compile(r"[a-zA-Z][a-zA-Z0-9_\\.]*")


class FieldNotFound(Exception):
    def __init__(self, field: str):
        super().__init__(f"Field '{field}' not found")


def is_valid_id(s: str) -> bool:
    return _RE_ID_AND_DOTS.fullmatch(s) is not None


def size2human(size: int) -> str:
    if size == 0:
        return "0B"
    p = int(log2(size) // 10.0)

    if p < 1:
        return f"{size}B"
    if p > len(IEC_UNITS):
        p = len(IEC_UNITS)
    converted_size = size / 1024**p
    return f"{converted_size:.1f}{IEC_UNITS[p - 1]}"


_TIMED: ContextVar = ContextVar("timed", default=None)


@contextmanager
def timing(name: str):
    t0 = time.perf_counter()
    old = _TIMED.get()
    if old is None:
        old = lambda k, v: None
    inner = 0.0

    def inc(name, elapsed):
        nonlocal inner
        old(name, elapsed)
        inner += elapsed

    _TIMED.set(inc)
    try:
        yield
    finally:
        _TIMED.set(old)
        elapsed = time.perf_counter() - t0 - inner
        if old is not None:
            old(name, elapsed)


@contextmanager
def start_timing(name: str, cb: Callable[[str, float], None]):
    old = _TIMED.get()
    _TIMED.set(cb)
    try:
        with timing(name):
            yield
    finally:
        _TIMED.set(old)
