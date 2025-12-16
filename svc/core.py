"""
core.py
Ядро конвертера: функции для чтения/записи CSV, JSON, YAML и конвертации между ними.
"""

from typing import List, Any, Dict, Union
import csv
import json
import io
import yaml
import logging

logger = logging.getLogger("svc.core")
logging.basicConfig(level=logging.INFO)


def read_csv(text: str, delimiter: str = ",") -> List[Dict[str, Any]]:
    """
    Читает CSV из строки и возвращает список словарей.
    """
    f = io.StringIO(text)
    reader = csv.DictReader(f, delimiter=delimiter)
    rows = [dict(row) for row in reader]
    logger.debug("CSV rows read: %d", len(rows))
    return rows


def write_csv(rows: List[Dict[str, Any]], delimiter: str = ",") -> str:
    """
    Пишет список словарей в CSV-строку.
    Использует объединение всех ключей как заголовков.
    """
    if not rows:
        return ""
    # collect all keys
    fieldnames = []
    for r in rows:
        for k in r.keys():
            if k not in fieldnames:
                fieldnames.append(k)
    f = io.StringIO()
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return f.getvalue()


def read_json(text: str) -> Union[List[Any], Dict[str, Any]]:
    """
    Загружает JSON из строки.
    """
    return json.loads(text)


def write_json(data: Union[List[Any], Dict[str, Any]], pretty: bool = True, ensure_ascii: bool = False) -> str:
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=ensure_ascii)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=ensure_ascii)


def read_yaml(text: str) -> Any:
    """
    Загружает YAML (поддерживает несколько документов; возвращает первый, если несколько).
    """
    loaded = yaml.safe_load(text)
    return loaded


def write_yaml(data: Any, default_flow_style: bool = False) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


# Высокоуровневые трансформации

def csv_to_json(csv_text: str, delimiter: str = ",") -> List[Dict[str, Any]]:
    rows = read_csv(csv_text, delimiter=delimiter)
    # Попытка автоматического приведения чисел/булевых значений не производим — сохраняем как строки.
    return rows


def json_to_csv(json_text: str, delimiter: str = ",") -> str:
    data = read_json(json_text)
    if isinstance(data, dict):
        # один объект -> один ряд
        rows = [data]
    elif isinstance(data, list):
        # список объектов
        rows = data
    else:
        raise ValueError("JSON must be an object or an array of objects to convert to CSV.")
    # ensure rows are list of dicts
    if not all(isinstance(r, dict) for r in rows):
        raise ValueError("To convert to CSV, JSON elements must be objects (dict).")
    return write_csv(rows, delimiter=delimiter)


def yaml_to_json(yaml_text: str) -> Any:
    data = read_yaml(yaml_text)
    return data


def json_to_yaml(json_text: str) -> str:
    data = read_json(json_text)
    return write_yaml(data)


def csv_to_yaml(csv_text: str, delimiter: str = ",") -> str:
    rows = csv_to_json(csv_text, delimiter=delimiter)
    return write_yaml(rows)


def yaml_to_csv(yaml_text: str, delimiter: str = ",") -> str:
    data = read_yaml(yaml_text)
    # If it's a list of dicts -> write rows
    if isinstance(data, list) and all(isinstance(r, dict) for r in data):
        return write_csv(data, delimiter=delimiter)
    if isinstance(data, dict):
        # single dict -> one row
        return write_csv([data], delimiter=delimiter)
    raise ValueError("YAML root must be a mapping or a sequence of mappings to convert to CSV.")
