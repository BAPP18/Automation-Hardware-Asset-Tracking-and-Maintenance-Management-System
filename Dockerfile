FROM python:3.11-slim

WORKDIR /app

COPY "Automation Hardware Asset Tracking and Maintenance Management System/asset-management-system/requirements.txt" .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY "Automation Hardware Asset Tracking and Maintenance Management System/asset-management-system/" .

ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY=it-asset-tracker-secret-key-2024

RUN mkdir -p /app/database

EXPOSE 8000

CMD gunicorn --workers 1 --threads 2 --timeout 180 'app:create_app()' --bind 0.0.0.0:$PORT