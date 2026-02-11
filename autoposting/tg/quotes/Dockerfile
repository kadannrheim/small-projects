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

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Указываем переменные окружения (переопределяются через docker-compose)
# ENV BOT_TOKEN=""
# ENV CHANNEL_ID=""
# ENV LOG_LEVEL="INFO"

# Запускаем наш скрипт
CMD ["python", "src/bot.py"]