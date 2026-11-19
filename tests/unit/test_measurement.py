"""Тесты модуля замера скорости скачивания."""

import unittest

from tests.conftest import local_http_server

from net_speed_check.measurement import (
    BenchmarkSummary,
    RequestResult,
    run_benchmark,
    validate_url,
)


class TestMeasurement(unittest.TestCase):
    """Проверяет валидацию, расчёт метрик и последовательные запросы."""

    def test_validate_url_accepts_http_and_https(self) -> None:
        self.assertEqual(
            validate_url("  https://example.com/image.jpg  "),
            "https://example.com/image.jpg",
        )
        self.assertEqual(
            validate_url("http://localhost:8080/data"),
            "http://localhost:8080/data",
        )

    def test_validate_url_rejects_invalid_scheme_or_host(self) -> None:
        for bad_url in ("ftp://example.com/file", "example.com/file", "https://", ""):
            with self.subTest(url=bad_url):
                with self.assertRaises(ValueError):
                    validate_url(bad_url)

    def test_benchmark_summary_metrics(self) -> None:
        # 2 запроса по 500_000 байт за 0.5 с каждый => 1_000_000 байт за 1.0 с
        # Скорость: 1 MB/s = 8 Mbps = 1000 KB/s
        summary = BenchmarkSummary(
            url="https://example.com/file.bin",
            results=(
                RequestResult(1, 200, 500_000, 0.5),
                RequestResult(2, 200, 500_000, 0.5),
            ),
        )
        self.assertEqual(summary.requests_count, 2)
        self.assertEqual(summary.total_bytes, 1_000_000)
        self.assertAlmostEqual(summary.total_duration_seconds, 1.0)
        self.assertAlmostEqual(summary.average_duration_seconds, 0.5)
        self.assertAlmostEqual(summary.speed_bytes_per_second, 1_000_000.0)
        self.assertAlmostEqual(summary.speed_mbps, 8.0)
        self.assertAlmostEqual(summary.speed_mb_per_second, 1.0)
        self.assertAlmostEqual(summary.speed_kb_per_second, 1_000.0)

    def test_run_benchmark_executes_ten_sequential_requests(self) -> None:
        payload = b"A" * 64_000
        observed_indices: list[int] = []

        with local_http_server(payload=payload) as (url, seen_paths):
            summary = run_benchmark(
                url=url,
                requests_count=10,
                chunk_size=8_192,
                on_request_done=lambda item: observed_indices.append(item.index),
            )

        self.assertEqual(len(seen_paths), 10)
        self.assertEqual(observed_indices, list(range(1, 11)))
        self.assertEqual(summary.requests_count, 10)
        self.assertEqual(summary.total_bytes, len(payload) * 10)
        self.assertGreater(summary.total_duration_seconds, 0.0)
        self.assertGreater(summary.speed_mbps, 0.0)

    def test_run_benchmark_rejects_invalid_arguments(self) -> None:
        with self.assertRaises(ValueError):
            run_benchmark("https://example.com", requests_count=0)
        with self.assertRaises(ValueError):
            run_benchmark("https://example.com", timeout=0)
        with self.assertRaises(ValueError):
            run_benchmark("https://example.com", chunk_size=0)


if __name__ == "__main__":
    unittest.main()
