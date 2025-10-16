# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --- Dependencias del sistema (mínimas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

# --- (OPCIONAL) Si tu app genera PDFs con wkhtmltopdf, descomenta:
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     wkhtmltopdf fontconfig libxrender1 libxext6 libjpeg62-turbo libnss3 fonts-dejavu-core \
#     && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
# (asegúrate de tener requirements.txt con fastapi y uvicorn)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el código
COPY . .

# Variables por defecto (puedes sobreescribirlas en docker-compose)
ENV PORT=5055 \
    APP_MODULE=app.main:app \
    BACK_BASE=http://backend:8080 \
    EQUIPOS_PATH=/api/equipos \
    PLAYERS_BY_TEAM=/api/jugadores \
    MATCH_HISTORY=/api/partidos/historial

EXPOSE 5055

# Arranque: uvicorn con el módulo indicado
CMD ["sh", "-c", "uvicorn ${APP_MODULE} --host 0.0.0.0 --port ${PORT}"]
