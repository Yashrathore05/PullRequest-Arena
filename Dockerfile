ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

WORKDIR /app/env

COPY pyproject.toml .
COPY . .

RUN pip install --no-cache-dir -e .

ENV PYTHONPATH="/app/env:$PYTHONPATH"

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health', timeout=3)" || exit 1

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
