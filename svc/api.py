"""
FastAPI HTTP API для конвертации.
Endpoints:
  POST /convert - multipart/form-data: file (or text), src_format, dst_format, delimiter (optional), pretty (optional)
  GET / - простая запись о сервисе
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
from typing import Optional
from svc import core
import logging

logger = logging.getLogger("svc.api")
app = FastAPI(title="CSV<->JSON<->YAML Converter", version="1.0")


@app.get("/", response_class=PlainTextResponse)
def root():
    return "CSV <-> JSON <-> YAML converter. Use POST /convert"


@app.post("/convert", response_class=PlainTextResponse)
async def convert(
    src_format: str = Form(...),
    dst_format: str = Form(...),
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    delimiter: Optional[str] = Form(","),
    pretty: Optional[bool] = Form(True),
):
    src_format = src_format.lower()
    dst_format = dst_format.lower()
    if file is None and (text is None or text == ""):
        raise HTTPException(status_code=400, detail="Provide file upload or text form field.")
    if file:
        content = (await file.read()).decode("utf-8")
    else:
        content = text
    try:
        # reuse CLI conversion logic
        if src_format == dst_format:
            result = content
        else:
            # delegate to core via same conversion mapping
            if src_format == "csv" and dst_format == "json":
                data = core.csv_to_json(content, delimiter=delimiter)
                result = core.write_json(data, pretty=pretty)
            elif src_format == "csv" and dst_format == "yaml":
                result = core.csv_to_yaml(content, delimiter=delimiter)
            elif src_format == "json" and dst_format == "csv":
                result = core.json_to_csv(content, delimiter=delimiter)
            elif src_format == "json" and dst_format == "yaml":
                result = core.json_to_yaml(content)
            elif src_format == "yaml" and dst_format == "json":
                data = core.yaml_to_json(content)
                result = core.write_json(data, pretty=pretty)
            elif src_format == "yaml" and dst_format == "csv":
                result = core.yaml_to_csv(content, delimiter=delimiter)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported conversion: {src_format}->{dst_format}")
    except Exception as e:
        logger.exception("Conversion error")
        raise HTTPException(status_code=400, detail=str(e))
    return PlainTextResponse(content=result, media_type="text/plain; charset=utf-8")


def run_from_cli():
    """Запускает uvicorn (используется при python -m svc --serve)"""
    uvicorn.run("svc.api:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run_from_cli()
