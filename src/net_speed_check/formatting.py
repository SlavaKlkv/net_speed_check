"""Форматирование результатов замера для консольного вывода."""

from typing import Literal

from net_speed_check.measurement import BenchmarkSummary, RequestResult

SpeedUnit = Literal["Mbps", "MB/s", "KB/s"]
SUPPORTED_UNITS: tuple[SpeedUnit, ...] = ("Mbps", "MB/s", "KB/s")


def format_bytes(num_bytes: int) -> str:
    """Форматирует размер в байтах в человекочитаемый вид (десятичные единицы)."""
    if num_bytes < 1_000:
        return f"{num_bytes} B"
    if num_bytes < 1_000_000:
        return f"{num_bytes / 1_000:.2f} KB"
    if num_bytes < 1_000_000_000:
        return f"{num_bytes / 1_000_000:.2f} MB"
    return f"{num_bytes / 1_000_000_000:.2f} GB"


def format_speed(summary: BenchmarkSummary, unit: SpeedUnit = "Mbps") -> str:
    """Возвращает строку скорости скачивания в выбранных единицах."""
    if unit == "Mbps":
        return f"{summary.speed_mbps:.2f} Mbps"
    if unit == "MB/s":
        return f"{summary.speed_mb_per_second:.2f} MB/s"
    if unit == "KB/s":
        return f"{summary.speed_kb_per_second:.2f} KB/s"
    raise ValueError(f"Неподдерживаемая единица измерения скорости: {unit!r}")


def format_request_line(result: RequestResult, total_requests: int) -> str:
    """Форматирует строку прогресса для одного завершённого запроса."""
    width = len(str(total_requests))
    return (
        f"[{result.index:>{width}}/{total_requests}] "
        f"HTTP {result.status_code} | "
        f"{format_bytes(result.bytes_downloaded)} | "
        f"{result.duration_seconds:.3f} s"
    )


def format_summary(summary: BenchmarkSummary, unit: SpeedUnit = "Mbps") -> str:
    """Формирует итоговый блок статистики замера."""
    lines = [
        "",
        "Итоги замера:",
        f"  URL:                     {summary.url}",
        f"  Запросов выполнено:      {summary.requests_count}",
        f"  Общий объём данных:      {format_bytes(summary.total_bytes)} ({summary.total_bytes:,} B)",
        f"  Суммарное время:         {summary.total_duration_seconds:.3f} s",
        f"  Среднее время запроса:   {summary.average_duration_seconds:.3f} s",
        f"  Скорость скачивания:     {format_speed(summary, unit)}",
    ]
    return "\n".join(lines)
