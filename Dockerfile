FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/uploads /app/instance && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

CMD ["sh", "-c", "flask --app run.py db upgrade && gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 4 wsgi:app"]
