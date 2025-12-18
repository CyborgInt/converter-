import argparse
import sys
from . import core
import logging

logger = logging.getLogger("svc.cli")


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="svc", description="Конвертер CSV ↔ JSON ↔ YAML")
    p.add_argument("--from", dest="src_format", choices=["csv", "json", "yaml"], required=False,
                   help="Исходный формат.")
    p.add_argument("--to", dest="dst_format", choices=["csv", "json", "yaml"], required=False,
                   help="Целевой формат.")
    p.add_argument("--input", "-i", dest="input_file", help="Файл-источник (если не задано, читаем из stdin).")
    p.add_argument("--output", "-o", dest="output_file", help="Файл вывода (если не задано, пишем в stdout).")
    p.add_argument("--delimiter", "-d", dest="delimiter", default=",", help="Разделитель для CSV (по умолчанию ',').")
    p.add_argument("--pretty", action="store_true", help="Форматированный вывод JSON (для json).")
    p.add_argument("--serve", action="store_true", help="Запустить HTTP API (uvicorn должен быть установлен).")
    return p.parse_args(argv)


def read_input(path: str = None) -> str:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def write_output(data: str, path: str = None):
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
    else:
        sys.stdout.write(data)


def convert_text(src_fmt: str, dst_fmt: str, text: str, delimiter: str = ",", pretty: bool = True) -> str:
    src_fmt = src_fmt.lower()
    dst_fmt = dst_fmt.lower()
    if src_fmt == dst_fmt:
        return text
    if src_fmt == "csv" and dst_fmt == "json":
        data = core.csv_to_json(text, delimiter=delimiter)
        return core.write_json(data, pretty=pretty)
    if src_fmt == "csv" and dst_fmt == "yaml":
        return core.csv_to_yaml(text, delimiter=delimiter)
    if src_fmt == "json" and dst_fmt == "csv":
        return core.json_to_csv(text, delimiter=delimiter)
    if src_fmt == "json" and dst_fmt == "yaml":
        return core.json_to_yaml(text)
    if src_fmt == "yaml" and dst_fmt == "json":
        data = core.yaml_to_json(text)
        return core.write_json(data, pretty=pretty)
    if src_fmt == "yaml" and dst_fmt == "csv":
        return core.yaml_to_csv(text, delimiter=delimiter)
    raise ValueError(f"Неподдерживаемое преобразование: {src_fmt} -> {dst_fmt}")


def main(argv=None):
    args = parse_args(argv)
    if args.serve:
        from .api import run_from_cli
        run_from_cli()
        return

    if not args.src_format or not args.dst_format:
        print("Ошибка: для CLI необходимо указать параметры --from и --to (если не используется --serve).", file=sys.stderr)
        sys.exit(2)

    text = read_input(args.input_file)
    try:
        out = convert_text(args.src_format, args.dst_format, text, delimiter=args.delimiter, pretty=args.pretty)
    except Exception as e:
        logger.error("Ошибка конвертации: %s", e)
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    write_output(out, args.output_file)


if __name__ == "__main__":
    main()
