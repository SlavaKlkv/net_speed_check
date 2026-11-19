"""Тесты форматирования консольного вывода."""

import unittest

from tests.conftest import SRC_DIR  # noqa: F401

from net_speed_check.formatting import (
    format_bytes,
    format_request_line,
    format_speed,
    format_summary,
)
from net_speed_check.measurement import BenchmarkSummary, RequestResult


class TestFormatting(unittest.TestCase):
    """Проверяет форматирование объёма данных, скорости и итоговой сводки."""

    def test_format_bytes(self) -> None:
        self.assertEqual(format_bytes(512), "512 B")
        self.assertEqual(format_bytes(1_500), "1.50 KB")
        self.assertEqual(format_bytes(2_500_000), "2.50 MB")
        self.assertEqual(format_bytes(3_000_000_000), "3.00 GB")

    def test_format_speed_units(self) -> None:
        summary = BenchmarkSummary(
            url="https://example.com/file.bin",
            results=(RequestResult(1, 200, 1_000_000, 1.0),),
        )
        self.assertEqual(format_speed(summary, "Mbps"), "8.00 Mbps")
        self.assertEqual(format_speed(summary, "MB/s"), "1.00 MB/s")
        self.assertEqual(format_speed(summary, "KB/s"), "1000.00 KB/s")

    def test_format_request_line_and_summary(self) -> None:
        result = RequestResult(1, 200, 500_000, 0.25)
        line = format_request_line(result, total_requests=10)
        self.assertIn("[ 1/10]", line)
        self.assertIn("HTTP 200", line)
        self.assertIn("500.00 KB", line)

        summary = BenchmarkSummary(
            url="https://example.com/file.bin",
            results=(result,),
        )
        text = format_summary(summary, unit="Mbps")
        self.assertIn("Итоги замера:", text)
        self.assertIn("Среднее время запроса:", text)
        self.assertIn("Скорость скачивания:", text)
        self.assertIn("16.00 Mbps", text)


if __name__ == "__main__":
    unittest.main()
