from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import uvicorn
from svc import core

app = FastAPI()

app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/")
def root():
    return RedirectResponse(url="/ui")

@app.get("/ui", response_class=HTMLResponse)
def ui():
    with open("web/index.html", encoding="utf-8") as f:
        return f.read()

@app.post("/convert", response_class=PlainTextResponse)
async def convert(
    src_format: str = Form(...),
    dst_format: str = Form(...),
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    pretty: Optional[bool] = Form(True),
):
    final_delimiter = ","

    if file:
        content = (await file.read()).decode("utf-8")
    elif text:
        content = text
    else:
        raise HTTPException(status_code=400, detail="No data")

    try:
        src, dst = src_format.lower(), dst_format.lower()
        if src == dst:
            return content

        if src == "csv" and dst == "json":
            data = core.csv_to_json(content, delimiter=final_delimiter)
            return core.write_json(data, pretty=pretty)
        elif src == "csv" and dst == "yaml":
            return core.csv_to_yaml(content, delimiter=final_delimiter)
        elif src == "json" and dst == "csv":
            return core.json_to_csv(content, delimiter=final_delimiter)
        elif src == "json" and dst == "yaml":
            return core.json_to_yaml(content)
        elif src == "yaml" and dst == "json":
            return core.write_json(core.yaml_to_json(content), pretty=pretty)
        elif src == "yaml" and dst == "csv":
            return core.yaml_to_csv(content, delimiter=final_delimiter)

        raise ValueError("Invalid format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
