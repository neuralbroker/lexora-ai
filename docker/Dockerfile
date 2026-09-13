FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
# NOTE: alembic/ intentionally not copied — the directory does not exist yet.
# Runtime uses Base.metadata.create_all; add alembic/ + alembic.ini back when migrations are initialized.
COPY .env.example .env

RUN mkdir -p /app/data/faiss /app/uploads

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
