<div align="center">

# net_speed_check

![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue)
![Dependencies: stdlib](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen)
![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)

</div>

Консольная утилита на Python для замера скорости скачивания по HTTP/HTTPS.  
Последовательно выполняет 10 запросов к указанному URL (например, тяжёлой картинке или файлу), дожидается полного ответа на каждый, считает среднее время запроса, общий объём скачанных данных и печатает скорость скачивания.

Условие тестового задания сохранено в [docs/TASK.md](docs/TASK.md).

## Особенности реализации

- **Без внешних зависимостей** — используется только стандартная библиотека Python (`urllib.request`, `time.perf_counter`, `argparse`, `dataclasses`).
- **Потоковое чтение чанками** — тело ответа читается до конца блоками по 64 KB и не удерживается целиком в оперативной памяти.
- **Монотонные часы** — время каждого запроса измеряется через `time.perf_counter()`, что исключает скачки системного времени.
- **Антикэш-заголовки** — в запросах передаются `Cache-Control: no-cache` и `Pragma: no-cache`.

## Единицы измерения скорости

По умолчанию скорость выводится в **мегабитах в секунду (`Mbps`)** — стандартной единице измерения пропускной способности интернет-канала (десятичная система СИ: `1 Mbps = 1 000 000 бит/с`, `1 байт = 8 бит`):

```text
speed_mbps = (total_bytes * 8) / total_duration_seconds / 1_000_000
```

При необходимости через флаг `--unit` можно переключить вывод на:

| Значение `--unit` | Единица | Формула |
| --- | --- | --- |
| `Mbps` *(по умолчанию)* | Мегабиты в секунду | `(total_bytes * 8) / total_duration_seconds / 1_000_000` |
| `MB/s` | Мегабайты в секунду | `total_bytes / total_duration_seconds / 1_000_000` |
| `KB/s` | Килобайты в секунду | `total_bytes / total_duration_seconds / 1_000` |

Объём данных в выводе форматируется в десятичных единицах (`1 KB = 1 000 B`, `1 MB = 1 000 000 B`), а в скобках дополнительно указывается точное число байт.

## Требования

- Python **3.14+** (проверено на `Python 3.14.10`).

## Установка и запуск

### Быстрый запуск без установки

```bash
git clone https://github.com/SlavaKlkv/net_speed_check.git
cd net_speed_check
python3 speed_check.py https://speed.cloudflare.com/__down?bytes=1000000
```

### Запуск с дополнительными параметрами

```bash
python3 speed_check.py https://speed.cloudflare.com/__down?bytes=1000000 --unit MB/s --timeout 20
```

### Установка как CLI-команды (опционально)

```bash
pip install -e .
net-speed-check https://speed.cloudflare.com/__down?bytes=1000000
```

## Параметры CLI

| Аргумент | По умолчанию | Описание |
| --- | --- | --- |
| `url` | *(обязательный)* | HTTP/HTTPS-адрес ресурса для скачивания |
| `-n`, `--requests` | `10` | Количество последовательных запросов |
| `--timeout` | `30.0` | Таймаут одного запроса в секундах |
| `--chunk-size` | `65536` | Размер буфера чтения ответа в байтах |
| `--unit` | `Mbps` | Единицы измерения скорости (`Mbps`, `MB/s`, `KB/s`) |

## Пример вывода

```text
Старт замера: https://speed.cloudflare.com/__down?bytes=1000000 (10 последовательных запросов)
[ 1/10] HTTP 200 | 1.00 MB | 0.241 s
[ 2/10] HTTP 200 | 1.00 MB | 0.198 s
...
[10/10] HTTP 200 | 1.00 MB | 0.205 s

Итоги замера:
  URL:                     https://speed.cloudflare.com/__down?bytes=1000000
  Запросов выполнено:      10
  Общий объём данных:      10.00 MB (10,000,000 B)
  Суммарное время:         2.114 s
  Среднее время запроса:   0.211 s
  Скорость скачивания:     37.84 Mbps
```

## Тесты

Тесты поднимают локальный HTTP-сервер и не требуют доступа в интернет:

```bash
python3 -m unittest discover -s tests -v
```

## Структура проекта

```text
net_speed_check/
├── docs/
│   └── TASK.md                 # Условие тестового задания
├── src/
│   └── net_speed_check/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py              # CLI-интерфейс и обработка ошибок
│       ├── formatting.py       # Форматирование размеров, скорости и сводки
│       └── measurement.py      # Последовательные запросы и расчёт метрик
├── tests/
│   ├── conftest.py             # Локальный HTTP-сервер для тестов
│   └── unit/
│       ├── test_cli.py
│       ├── test_formatting.py
│       └── test_measurement.py
├── speed_check.py              # Точка входа для запуска без установки
├── pyproject.toml
├── LICENSE
└── README.md
```

## Лицензия

[MIT](LICENSE)
