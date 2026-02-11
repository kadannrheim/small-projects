import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем .env файл из текущей директории
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

@dataclass
class Config:
    """Конфигурация приложения"""
    # Telegram
    bot_token: str = os.getenv('TG_Q_BOT_TOKEN', '')
    channel_id: str = os.getenv('TG_Q_CHANNEL_ID', '')
    
    # Scheduler
    base_hour: int = int(os.getenv('BASE_HOUR', '9'))
    base_minute: int = int(os.getenv('BASE_MINUTE', '0'))
    random_range_minutes: int = int(os.getenv('RANDOM_RANGE_MINUTES', '30'))
    
    # Files
    quotes_file: str = os.getenv('QUOTES_FILE', 'data/quotes.json')
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', 'bot.log')
    
    def validate(self) -> bool:
        """Проверяет обязательные поля"""
        if not self.bot_token:
            raise ValueError("TG_Q_BOT_TOKEN не указан в .env файле")
        if not self.channel_id:
            raise ValueError("TG_Q_CHANNEL_ID не указан в .env файле")
        return True

# Глобальный объект конфигурации
config = Config()