FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY models.py .
COPY scenarios.py .
COPY graders.py .
COPY __init__.py .
COPY server/app.py .
COPY server/bug_triage_environment.py .
COPY server/__init__.py server_init.py

ENV PORT=7860
ENV HOST=0.0.0.0
ENV WORKERS=1
ENV MAX_CONCURRENT_ENVS=100

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
