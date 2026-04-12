ARG BASE_IMAGE=openenv-base:latest
FROM ${BASE_IMAGE}

WORKDIR /app/env

COPY pyproject.toml .
COPY . .

RUN pip install --no-cache-dir -e .

ENV PYTHONPATH="/app/env:$PYTHONPATH"

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
