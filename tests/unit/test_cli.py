"""Тесты CLI-интерфейса."""

from contextlib import redirect_stderr, redirect_stdout
import io
import unittest

from tests.conftest import local_http_server

from net_speed_check.cli import main


class TestCli(unittest.TestCase):
    """Проверяет коды возврата и вывод CLI."""

    def test_cli_success(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with local_http_server(payload=b"Z" * 16_000) as (url, _):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main([url, "-n", "3", "--unit", "MB/s"])

        self.assertEqual(code, 0)
        self.assertEqual(stderr.getvalue(), "")
        output = stdout.getvalue()
        self.assertIn("[3/3]", output)
        self.assertIn("Итоги замера:", output)
        self.assertIn("MB/s", output)

    def test_cli_invalid_url_returns_2(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["not-a-valid-url"])

        self.assertEqual(code, 2)
        self.assertIn("Ошибка параметров:", stderr.getvalue())

    def test_cli_http_error_returns_1(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with local_http_server(payload=b"not found", status_code=404) as (url, _):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main([url, "-n", "1"])

        self.assertEqual(code, 1)
        self.assertIn("HTTP-ошибка", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
