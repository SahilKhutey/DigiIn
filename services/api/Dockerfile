FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml ./
COPY app ./app

RUN pip install --no-cache-dir .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
