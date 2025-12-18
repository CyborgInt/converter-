from typing import List, Any, Dict, Union
import csv
import json
import io
import yaml
import logging

logger = logging.getLogger("svc.core")
logging.basicConfig(level=logging.INFO)


def read_csv(text: str, delimiter: str = ",") -> List[Dict[str, Any]]:
    f = io.StringIO(text)
    reader = csv.DictReader(f, delimiter=delimiter)
    rows = [dict(row) for row in reader]
    logger.debug("Прочитано строк CSV: %d", len(rows))
    return rows


def write_csv(rows: List[Dict[str, Any]], delimiter: str = ",") -> str:
    if not rows:
        return ""
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
    return json.loads(text)


def write_json(data: Union[List[Any], Dict[str, Any]], pretty: bool = True, ensure_ascii: bool = False) -> str:
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=ensure_ascii)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=ensure_ascii)


def read_yaml(text: str) -> Any:
    loaded = yaml.safe_load(text)
    return loaded


def write_yaml(data: Any, default_flow_style: bool = False) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)



def csv_to_json(csv_text: str, delimiter: str = ",") -> List[Dict[str, Any]]:
    rows = read_csv(csv_text, delimiter=delimiter)
    return rows


def json_to_csv(json_text: str, delimiter: str = ",") -> str:
    data = read_json(json_text)
    if isinstance(data, dict):
        rows = [data]
    elif isinstance(data, list):
        rows = data
    else:
        raise ValueError("JSON должен быть объектом или массивом объектов для преобразования в CSV.")
    if not all(isinstance(r, dict) for r in rows):
        raise ValueError("Для преобразования в CSV элементы JSON должны быть объектами (dict).")
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
    if isinstance(data, list) and all(isinstance(r, dict) for r in data):
        return write_csv(data, delimiter=delimiter)
    if isinstance(data, dict):
        return write_csv([data], delimiter=delimiter)
    raise ValueError("Корень YAML должен быть словарём или списком словарей для преобразования в CSV.")
