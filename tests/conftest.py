"""Общие хелперы и локальный HTTP-сервер для тестов."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading
from typing import Iterator

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@contextmanager
def local_http_server(
    payload: bytes = b"x" * 100_000,
    status_code: int = 200,
) -> Iterator[tuple[str, list[str]]]:
    """Поднимает локальный HTTP-сервер на случайном порту и логирует пути запросов."""
    seen_paths: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            seen_paths.append(self.path)
            self.send_response(status_code)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            # Подавляем шумный вывод HTTP-сервера в логах тестов.
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{port}/file.bin", seen_paths
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
