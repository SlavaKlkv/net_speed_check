"""CLI-интерфейс для запуска замера скорости скачивания."""

import argparse
from collections.abc import Sequence
import sys
from urllib.error import HTTPError, URLError

from net_speed_check.formatting import (
    SUPPORTED_UNITS,
    format_request_line,
    format_summary,
)
from net_speed_check.measurement import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_REQUESTS_COUNT,
    DEFAULT_TIMEOUT_SECONDS,
    run_benchmark,
)


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="net-speed-check",
        description=(
            "Замеряет скорость скачивания, выполняя серию последовательных "
            "HTTP/HTTPS-запросов к указанному URL."
        ),
    )
    parser.add_argument(
        "url",
        help="HTTP/HTTPS-адрес ресурса для скачивания (например, тяжёлая картинка).",
    )
    parser.add_argument(
        "-n",
        "--requests",
        type=int,
        default=DEFAULT_REQUESTS_COUNT,
        help=f"Количество последовательных запросов (по умолчанию: {DEFAULT_REQUESTS_COUNT}).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Таймаут одного запроса в секундах (по умолчанию: {DEFAULT_TIMEOUT_SECONDS}).",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Размер буфера чтения в байтах (по умолчанию: {DEFAULT_CHUNK_SIZE}).",
    )
    parser.add_argument(
        "--unit",
        choices=SUPPORTED_UNITS,
        default="Mbps",
        help="Единицы измерения скорости в итоговом выводе (по умолчанию: Mbps).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Точка входа CLI. Возвращает код завершения процесса."""
    parser = build_parser()
    args = parser.parse_args(argv)

    print(f"Старт замера: {args.url} ({args.requests} последовательных запросов)")

    try:
        summary = run_benchmark(
            url=args.url,
            requests_count=args.requests,
            timeout=args.timeout,
            chunk_size=args.chunk_size,
            on_request_done=lambda result: print(
                format_request_line(result, args.requests),
                flush=True,
            ),
        )
    except ValueError as exc:
        print(f"Ошибка параметров: {exc}", file=sys.stderr)
        return 2
    except HTTPError as exc:
        print(f"HTTP-ошибка при запросе: {exc.code} {exc.reason}", file=sys.stderr)
        return 1
    except URLError as exc:
        print(f"Сетевая ошибка: {exc.reason}", file=sys.stderr)
        return 1
    except TimeoutError:
        print("Превышен таймаут ожидания ответа от сервера.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nЗамер прерван пользователем.", file=sys.stderr)
        return 130

    print(format_summary(summary, unit=args.unit))
    return 0
