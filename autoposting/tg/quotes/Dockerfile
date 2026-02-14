# Используем легковесный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements

# Копируем исходный код
COPY src/ ./src/
COPY data/ ./data/

# Создаем пользователя и группу с UID/GID 1000 (стандартный для Ubuntu)
RUN groupadd -g 1000 botgroup && \
    useradd -m -u 1000 -g botgroup botuser

# Создаем папку для логов и даем права
RUN mkdir -p /app/logs && \
    chown -R botuser:botgroup /app && \
    chmod 755 /app/logs

# Переключаемся на пользователя
USER botuser

# Запускаем наш скрипт
CMD ["python", "src/bot.py"]