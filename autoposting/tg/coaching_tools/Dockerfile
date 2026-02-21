#!/usr/bin/env dockerfile
# =============================================================================
# DOCKERFILE ДЛЯ COACHING TOOLS BOT
# =============================================================================

FROM python:3.11-alpine

LABEL maintainer="kadannr <kadannr@gmail.com>" \
      version="1.0.0" \
      description="Telegram bot for coaching tools"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Europe/Moscow

RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache tzdata ca-certificates && \
    rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN addgroup -g 1000 -S botgroup && \
    adduser -u 1000 -S botuser -G botgroup

COPY src/ ./src/
COPY data/ ./data/

RUN mkdir -p /app/logs && \
    chown -R botuser:botgroup /app && \
    chmod 755 /app/logs

USER botuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["python", "src/bot.py"]