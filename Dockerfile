FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY ["Automation Hardware Asset Tracking and Maintenance Management System/asset-management-system/requirements.txt", "./requirements.txt"]
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ["Automation Hardware Asset Tracking and Maintenance Management System/asset-management-system/", "./"]

RUN mkdir -p /app/database /app/uploads /app/exports \
    && chown -R appuser:appuser /app

USER appuser

ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["sh", "-c", "gunicorn --config gunicorn.conf.py --workers 1 --threads 2 --timeout 180 'app:create_app()' --bind 0.0.0.0:$PORT"]
