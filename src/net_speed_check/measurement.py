"""Ядро последовательного замера скорости скачивания."""

from collections.abc import Callable
from dataclasses import dataclass
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_REQUESTS_COUNT = 10
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_CHUNK_SIZE = 65_536
USER_AGENT = "net-speed-check/0.1.0"


@dataclass(frozen=True, slots=True)
class RequestResult:
    """Результат одного последовательного HTTP-запроса."""

    index: int
    status_code: int
    bytes_downloaded: int
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class BenchmarkSummary:
    """Агрегированные метрики серии последовательных запросов."""

    url: str
    results: tuple[RequestResult, ...]

    @property
    def requests_count(self) -> int:
        """Количество выполненных запросов."""
        return len(self.results)

    @property
    def total_bytes(self) -> int:
        """Суммарный объём скачанных данных в байтах."""
        return sum(item.bytes_downloaded for item in self.results)

    @property
    def total_duration_seconds(self) -> float:
        """Суммарное время всех запросов в секундах."""
        return sum(item.duration_seconds for item in self.results)

    @property
    def average_duration_seconds(self) -> float:
        """Среднее время одного запроса в секундах."""
        if not self.results:
            return 0.0
        return self.total_duration_seconds / len(self.results)

    @property
    def speed_bytes_per_second(self) -> float:
        """Средняя скорость скачивания в байтах в секунду (B/s)."""
        if self.total_duration_seconds <= 0:
            return 0.0
        return self.total_bytes / self.total_duration_seconds

    @property
    def speed_mbps(self) -> float:
        """Средняя скорость скачивания в мегабитах в секунду (Mbps, 10^6 бит/с)."""
        return (self.speed_bytes_per_second * 8) / 1_000_000

    @property
    def speed_mb_per_second(self) -> float:
        """Средняя скорость скачивания в мегабайтах в секунду (MB/s, 10^6 байт/с)."""
        return self.speed_bytes_per_second / 1_000_000

    @property
    def speed_kb_per_second(self) -> float:
        """Средняя скорость скачивания в килобайтах в секунду (KB/s, 10^3 байт/с)."""
        return self.speed_bytes_per_second / 1_000


def validate_url(url: str) -> str:
    """Проверяет, что передан корректный HTTP/HTTPS URL."""
    cleaned = url.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(
            "Укажите корректный URL со схемой http:// или https:// "
            f"(получено: {url!r})."
        )
    return cleaned


def download_once(
    url: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> tuple[int, int, float]:
    """Выполняет один GET-запрос, дочитывает тело целиком и возвращает метрики.

    Возвращает кортеж (status_code, bytes_downloaded, duration_seconds).
    """
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            # Просим прокси и CDN не отдавать устаревший кэш, если это возможно.
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="GET",
    )

    started_at = time.perf_counter()
    bytes_downloaded = 0

    with urlopen(request, timeout=timeout) as response:
        status_code = getattr(response, "status", response.getcode())
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            bytes_downloaded += len(chunk)

    duration_seconds = time.perf_counter() - started_at
    return status_code, bytes_downloaded, duration_seconds


def run_benchmark(
    url: str,
    requests_count: int = DEFAULT_REQUESTS_COUNT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    on_request_done: Callable[[RequestResult], None] | None = None,
) -> BenchmarkSummary:
    """Последовательно выполняет серию запросов и возвращает итоговую сводку."""
    validated_url = validate_url(url)
    if requests_count < 1:
        raise ValueError("Количество запросов должно быть не меньше 1.")
    if timeout <= 0:
        raise ValueError("Таймаут должен быть положительным числом.")
    if chunk_size < 1:
        raise ValueError("Размер буфера чтения должен быть не меньше 1 байта.")

    results: list[RequestResult] = []
    for index in range(1, requests_count + 1):
        status_code, bytes_downloaded, duration_seconds = download_once(
            url=validated_url,
            timeout=timeout,
            chunk_size=chunk_size,
        )
        result = RequestResult(
            index=index,
            status_code=status_code,
            bytes_downloaded=bytes_downloaded,
            duration_seconds=duration_seconds,
        )
        results.append(result)
        if on_request_done is not None:
            on_request_done(result)

    return BenchmarkSummary(url=validated_url, results=tuple(results))
