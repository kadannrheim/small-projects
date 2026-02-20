import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем .env файл
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

@dataclass
class Config:
    """Конфигурация приложения"""
    # Telegram
    tg_q_bot_token: str = os.getenv('TG_Q_BOT_TOKEN', '')
    tg_q_channel_id: str = os.getenv('TG_Q_CHANNEL_ID', '')
    
    # Scheduler
    base_hour: int = int(os.getenv('TG_Q_BASE_HOUR', '9'))
    base_minute: int = int(os.getenv('TG_Q_BASE_MINUTE', '0'))
    random_range_minutes: int = int(os.getenv('TG_Q_RANDOM_RANGE_MINUTES', '30'))
    
    # Files
    quotes_file: str = os.getenv('QUOTES_FILE', '../data/quotes365.json')
    history_file: str = os.getenv('HISTORY_FILE', '../data/published_history.json')  # Новый файл истории
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', 'bot.log')
    
    def validate(self) -> bool:
        """Проверяет обязательные поля"""
        if not self.tg_q_bot_token:
            raise ValueError("TG_Q_BOT_TOKEN не указан в .env файле")
        if not self.tg_q_channel_id:
            raise ValueError("TG_Q_CHANNEL_ID не указан в .env файле")
        return True

# Глобальный объект конфигурации
config = Config()