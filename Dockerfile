FROM python:3.11-slim

WORKDIR /app

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models.py .
COPY scenarios.py .
COPY graders.py .
COPY server/app.py .
COPY server/bug_triage_environment.py .

ENV PORT=7860
ENV HOST=0.0.0.0
ENV MAX_CONCURRENT_ENVS=100

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
