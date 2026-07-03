FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY ./app /app/app
RUN adduser --disabled-password --gecos "" appuser || true
USER appuser
EXPOSE 8000
ENV DATABASE_URL="postgresql+asyncpg://postgres:postgres@control_db:5432/postgres"
COPY wait_for_db.py /app/wait_for_db.py
COPY ../seed_data.py /app/seed_data.py
CMD ["bash", "-lc", "python /app/wait_for_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
