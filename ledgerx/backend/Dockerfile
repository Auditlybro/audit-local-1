FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app/core
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt* ./
RUN pip install --no-cache-dir uvicorn[standard] redis "fastapi>=0.100" "sqlalchemy>=2" "asyncpg" 2>/dev/null || true
COPY . .
EXPOSE 8000
WORKDIR /app/core
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
