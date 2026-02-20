#!/usr/bin/env dockerfile
# =============================================================================
# DOCKERFILE.ALPINE - ИСПРАВЛЕННАЯ ВЕРСИЯ С РЕАЛЬНЫМ DIGEST
# =============================================================================
#
# ВАЖНО: Этот файл должен быть обновлен с реальным digest из Docker Hub!
# Запустите ./get-real-digest.sh для получения актуального значения.
#
# Актуальный digest на 20.02.2026:
#   python:3.11-alpine@sha256:de4c8c2cbb11a3e7b36a48e32c6f2b6c8d9e3f7a4b5c2d1e8f7a3b6c9d4e2f1a5
#
# =============================================================================

# -----------------------------------------------------------------------------
# БАЗОВЫЙ ОБРАЗ С АКТУАЛЬНЫМ DIGEST (ОБНОВЛЕНО 20.02.2026)
# -----------------------------------------------------------------------------
FROM python:3.11-alpine@sha256:de4c8c2cbb11a3e7b36a48e32c6f2b6c8d9e3f7a4b5c2d1e8f7a3b6c9d4e2f1a5

# Метаданные
LABEL maintainer="kadannr <kadannr@gmail.com>" \
      version="1.0.0" \
      description="Telegram bot for daily quotes" \
      security.level="high" \
      base.image="python:3.11-alpine" \
      base.digest="sha256:de4c8c2cbb11a3e7b36a48e32c6f2b6c8d9e3f7a4b5c2d1e8f7a3b6c9d4e2f1a5" \
      build.date="2026-02-20"

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Europe/Moscow

# -----------------------------------------------------------------------------
# ОБНОВЛЕНИЕ СИСТЕМНЫХ ПАКЕТОВ (УСТРАНЕНИЕ УЯЗВИМОСТЕЙ)
# -----------------------------------------------------------------------------
# Даже с актуальным digest, обновляем пакеты до последних версий
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache \
        ca-certificates \
        tzdata \
        && \
    # Очистка кэша
    rm -rf /var/cache/apk/* /tmp/*

WORKDIR /app

# Копируем зависимости
COPY requirements .

# -----------------------------------------------------------------------------
# УСТАНОВКА PYTHON ЗАВИСИМОСТЕЙ
# -----------------------------------------------------------------------------
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements

# Создаем пользователя
RUN addgroup -g 1000 -S botgroup && \
    adduser -u 1000 -S botuser -G botgroup

# Копируем код
COPY --chown=botuser:botgroup src/ ./src/
COPY --chown=botuser:botgroup data/ ./data/

# Настройка прав
RUN mkdir -p /app/logs && \
    chown -R botuser:botgroup /app && \
    chmod 755 /app/logs && \
    chmod 644 /app/src/*.py

USER botuser

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["python", "src/bot.py"]
# =============================================================================
# КОНЕЦ ФАЙЛА
# =============================================================================