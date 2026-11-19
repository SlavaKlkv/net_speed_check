"""Пакет для замера скорости скачивания по HTTP/HTTPS."""

from net_speed_check.measurement import (
    BenchmarkSummary,
    RequestResult,
    download_once,
    run_benchmark,
    validate_url,
)

__all__ = [
    "BenchmarkSummary",
    "RequestResult",
    "download_once",
    "run_benchmark",
    "validate_url",
]
