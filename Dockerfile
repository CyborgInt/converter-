FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY svc/ ./svc/
COPY web/ ./web/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "svc.api:app", "--host", "0.0.0.0", "--port", "8000"]
