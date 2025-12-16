# CSV ↔ JSON ↔ YAML Converter

Утилита на Python для конвертации данных между форматами **CSV**, **JSON** и **YAML**. Проект поддерживает работу через **CLI** и **HTTP API (FastAPI)**, а также полностью готов к запуску в **Docker**.

Проект выполнен как индивидуальная учебная работа с соблюдением требований к структуре репозитория, контейнеризации и документации.

---

## Быстрый старт

```bash
git clone https://github.com/CyborgInt/converter-.git
cd converter-
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m svc --help
```

---

## Требования

- Python 3.11+
- pip
- (опционально) Docker / Docker Compose для контейнерного запуска

Все внешние зависимости зафиксированы в `requirements.txt`.

---

## Варианты запуска

### 1) Запуск в Docker

```bash
docker build -t csvjsonyaml-converter .
docker run --rm -p 8000:8000 csvjsonyaml-converter
```

После запуска HTTP API будет доступно по адресу:
```
http://localhost:8000/
```

---

### 2) Docker Compose

```bash
docker compose up --build
```

Пробрасывается порт `8000`. Значение порта можно изменить через файл `.env`.

---

### 3) Локальный запуск без Docker

```bash
python -m svc --serve
```

Сервер будет доступен по адресу:
```
http://localhost:8000/
```

---

## CLI‑конвертация

Примеры использования утилиты командной строки:

```bash
# CSV → JSON
python -m svc --from csv --to json -i data.csv -o data.json

# JSON → YAML
python -m svc --from json --to yaml -i data.json

# YAML → CSV
python -m svc --from yaml --to csv -i data.yaml -o data.csv
```

Если файл ввода не указан, данные читаются из `stdin`. Если файл вывода не указан — результат выводится в `stdout`.

---

## HTTP API

### `GET /`

Проверка доступности сервиса.

Ответ:
```text
CSV <-> JSON <-> YAML converter. Use POST /convert
```

---

### `POST /convert`

Конвертация данных между форматами.

**Параметры (multipart/form-data):**
- `src_format` — исходный формат (`csv`, `json`, `yaml`)
- `dst_format` — целевой формат (`csv`, `json`, `yaml`)
- `file` — загружаемый файл (опционально)
- `text` — текстовые данные (если файл не передан)
- `delimiter` — разделитель CSV (по умолчанию `,`)
- `pretty` — форматированный JSON (`true` / `false`)

Пример запроса:
```bash
curl -X POST http://localhost:8000/convert \
  -F src_format=csv \
  -F dst_format=json \
  -F file=@example.csv
```

---

## Поддержка YAML

Для работы с YAML используется библиотека **PyYAML**:
- загрузка: `yaml.safe_load`
- сериализация: `yaml.safe_dump`

Поддерживаемые преобразования:
- CSV → YAML
- YAML → CSV
- JSON → YAML
- YAML → JSON

---

## Переменные окружения

- `HOST_PORT` — порт, на который пробрасывается HTTP API при запуске через Docker Compose (по умолчанию `8000`).

Пример файла `.env.example`:
```env
HOST_PORT=8000
```

---

## Структура проекта

```
.
├── svc/
│   ├── api.py        # FastAPI HTTP API
│   ├── cli.py        # CLI-обёртка
│   ├── core.py       # Ядро конвертации
│   └── __init__.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Полезно знать

- CSV не хранит типы данных, поэтому все значения читаются как строки.
- Автоматическое приведение типов намеренно не используется для сохранения исходных данных.
- Проект поддерживает одинаковую логику конвертации для CLI и HTTP API.

---

## Ссылки

- GitHub: https://github.com/CyborgInt/converter-

