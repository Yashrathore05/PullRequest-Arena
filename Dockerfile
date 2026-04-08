# PullRequest Arena — Dockerfile
# Containerized OpenEnv environment for HuggingFace Spaces deployment

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY env.py .
COPY grader.py .
COPY tasks.json .
COPY inference.py .
COPY openenv.yaml .
COPY README.md .

# HuggingFace Spaces expects port 7860
EXPOSE 7860

# Health check to verify the server is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')" || exit 1

# Start the Flask server
CMD ["python", "env.py"]
