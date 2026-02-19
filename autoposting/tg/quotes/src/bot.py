import json
import random
import schedule
import time
import signal
import sys
import datetime
import logging
from typing import List, Dict, Optional

from config import config
from utils import setup_logger, graceful_shutdown
from history import history

# Настройка логирования
logger = setup_logger(__name__, config.log_level, config.log_file)

def load_quotes() -> List[Dict]:
    """Загружает цитаты из JSON файла"""
    try:
        with open(config.quotes_file, 'r', encoding='utf-8') as file:
            quotes = json.load(file)
        logger.info(f"Загружено {len(quotes)} цитат")
        return quotes
    except FileNotFoundError:
        logger.error(f"Файл '{config.quotes_file}' не найден")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка JSON в файле '{config.quotes_file}': {e}")
        return []

# ============= ЕДИНСТВЕННАЯ ФУНКЦИЯ get_unique_quote =============
def get_unique_quote(quotes: List[Dict]) -> Dict:
    """Выбирает уникальную цитату. Если все использованы - начинает новый цикл"""
    
    # Получаем доступные цитаты (не публиковавшиеся 365 дней)
    available = history.get_available_quotes(quotes, days=365)
    
    # Если есть доступные - выбираем случайную
    if available:
        quote = random.choice(available)
        total = len(quotes)
        used = total - len(available)
        logger.info(f"📊 Использовано {used}/{total} цитат в этом цикле")
        return quote
    
    # Если нет доступных - СБРАСЫВАЕМ ИСТОРИЮ и начинаем заново
    logger.info("🔄 Все цитаты использованы! Начинаем новый годовой цикл...")
    history.reset_history()
    
    # Теперь все цитаты снова доступны
    return random.choice(quotes)
# ==================================================================

def format_quote(quote_data: Dict) -> str:
    """Форматирует цитату"""
    text = quote_data.get('text', '')
    author = quote_data.get('author', '')
    hashtag = quote_data.get('hashtag', '#цитаты')
    
    return f"{text}\n\n{author}\n\n{hashtag}"

def send_quote():
    """Выбирает цитату и отправляет ее в канал"""
    import requests
    
    quotes = load_quotes()
    
    if not quotes:
        logger.warning("Не могу отправить цитату. Список цитат пуст.")
        return
    
    # Получаем цитату (теперь всегда получаем)
    quote_data = get_unique_quote(quotes)
    formatted_quote = format_quote(quote_data)
    quote_text = quote_data.get('text', '')
    
    logger.info(f"Отправляю цитату: {quote_text[:50]}...")
    
    url = f'https://api.telegram.org/bot{config.tg_q_bot_token}/sendMessage'
    payload = {
        'chat_id': config.tg_q_channel_id,
        'text': formatted_quote
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Цитата успешно отправлена!")
            # Отмечаем цитату как опубликованную
            history.mark_published(quote_text)
            # Показываем статистику
            stats = history.get_stats()
            logger.info(f"📈 Всего уникальных публикаций: {stats['total']}")
        else:
            logger.error(f"❌ Ошибка Telegram API: {response.status_code}")
            logger.error(f"Детали: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Сетевая ошибка: {e}")
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")

def schedule_random_time() -> str:
    """Генерирует случайное время в диапазоне ±N минут от базового"""
    random_offset = random.randint(-config.random_range_minutes, config.random_range_minutes)
    
    total_minutes = config.base_hour * 60 + config.base_minute + random_offset
    
    # Корректируем границы суток
    total_minutes = max(0, min(total_minutes, 23 * 60 + 59))
    
    target_hour = total_minutes // 60
    target_minute = total_minutes % 60
    
    target_time = f"{target_hour:02d}:{target_minute:02d}"
    
    logger.info(f"🕒 Случайное время публикации: {target_time} "
                f"(смещение: {'+' if random_offset >= 0 else ''}{random_offset} минут)")
    
    return target_time

def setup_daily_schedule() -> str:
    """Настраивает ежедневное расписание со случайным временем"""
    schedule.clear()
    
    random_time = schedule_random_time()
    schedule.every().day.at(random_time).do(send_quote)
    
    return random_time

def main():
    """Основная функция запуска"""
    # Обработчики сигналов
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    logger.info("Бот-издатель цитат запущен...")
    logger.info(f"📅 Основное время: {config.base_hour:02d}:{config.base_minute:02d}")
    logger.info(f"🎲 Случайный диапазон: ±{config.random_range_minutes} минут")
    
    # Проверяем конфигурацию
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        logger.error("Проверьте .env файл и заполните все необходимые поля")
        sys.exit(1)
    
    # Проверяем загрузку цитат
    quotes = load_quotes()
    if not quotes:
        logger.error("Не удалось загрузить цитаты!")
        sys.exit(1)
    
    # Показываем статистику истории
    stats = history.get_stats()
    logger.info(f"📊 История публикаций: всего {stats['total']} цитат")
    if stats['last_30_days'] > 0:
        logger.info(f"📊 За последние 30 дней: {stats['last_30_days']} публикаций")
    
    # Тестовая отправка при старте
    logger.info("Отправляю тестовую цитату при старте...")
    send_quote()
    
    # Настраиваем расписание
    today_time = setup_daily_schedule()
    logger.info(f"✅ Сегодняшняя публикация запланирована на: {today_time}")
    
    # Основной цикл
    last_check_date = datetime.datetime.now().date()
    
    while True:
        current_date = datetime.datetime.now().date()
        if current_date != last_check_date:
            logger.info("📅 Новый день! Перепланирую публикацию...")
            new_time = setup_daily_schedule()
            logger.info(f"✅ Публикация запланирована на: {new_time}")
            last_check_date = current_date
        
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()