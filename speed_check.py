#!/usr/bin/env python3
"""Точка входа для быстрого запуска скрипта без установки пакета."""

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from net_speed_check.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
