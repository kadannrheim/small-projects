# Используем легковесный Python образ
FROM python:3.11-sli

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY src/ ./src/
COPY data/ ./data/

# Создаем пользователя ДО создания папки логов
RUN useradd -m -u 1000 botuser

# Создаем папку для логов и назначаем владельца
RUN mkdir -p /app/logs && \
    chown -R botuser:botuser /app && \
    chmod 755 /app/logs

# Переключаемся на пользователя
USER botuser

# Запускаем наш скрипт
CMD ["python", "src/bot.py"]