# CSV ↔ JSON ↔ YAML Converter

**Кратко:** утилита на Python для конвертации между CSV, JSON и YAML. Поддерживает запуск в виде CLI и HTTP API (FastAPI). Проект подготовлен для контейнеризации (Docker).

## Требования
- Python 3.11+ (корректно работает и с 3.10)
- Docker (для контейнерной сборки)
- (опционально) pre-commit, black, isort, ruff

Установленные зависимости перечислены в `requirements.txt`.

---

## Локальная установка (рекомендуется в виртуальном окружении)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

