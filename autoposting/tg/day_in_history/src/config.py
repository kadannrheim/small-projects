#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль конфигурации "День в истории"
=====================================

Настройки для бота с историческими постами.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv

# =============================================================================
# ЗАГРУЗКА .ENV ФАЙЛА
# =============================================================================

env_path = Path(__file__).parent.parent / '.env'

if env_path.exists():
    load_dotenv(env_path, override=False)
    print(f"✅ Загружен .env файл: {env_path}")
else:
    print(f"⚠️ .env файл не найден по пути: {env_path}")


# =============================================================================
# КЛАСС КОНФИГУРАЦИИ
# =============================================================================

@dataclass
class Config:
    """
    Конфигурация приложения для бота "День в истории".
    """
    
    # =========================================================================
    # TELEGRAM НАСТРОЙКИ (ОБЯЗАТЕЛЬНЫЕ)
    # =========================================================================
    
    tg_bot_token: str = field(
        default_factory=lambda: os.getenv('TG_BOT_TOKEN', '')
    )
    """Токен бота от @BotFather."""
    
    tg_channel_id: str = field(
        default_factory=lambda: os.getenv('TG_CHANNEL_ID', '')
    )
    """ID канала для публикаций."""
    
    # =========================================================================
    # НАСТРОЙКИ ПЛАНИРОВЩИКА
    # =========================================================================
    
    publish_hour: int = field(
        default_factory=lambda: int(os.getenv('PUBLISH_HOUR', '10'))
    )
    """Час публикации (0-23)."""
    
    publish_minute: int = field(
        default_factory=lambda: int(os.getenv('PUBLISH_MINUTE', '0'))
    )
    """Минута публикации (0-59)."""
    
    # =========================================================================
    # НАСТРОЙКИ ФАЙЛОВ
    # =========================================================================
    
    data_file: str = field(
        default_factory=lambda: os.getenv('DATA_FILE', 'data/day_in_history.json')
    )
    """Путь к файлу с постами."""
    
    history_file: str = field(
        default_factory=lambda: os.getenv('HISTORY_FILE', 'data/history.json')
    )
    """Путь к файлу истории публикаций."""
    
    # =========================================================================
    # НАСТРОЙКИ ЛОГИРОВАНИЯ
    # =========================================================================
    
    log_level: str = field(
        default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO')
    )
    """Уровень логирования."""
    
    log_file: str = field(
        default_factory=lambda: os.getenv('LOG_FILE', 'logs/bot.log')
    )
    """Путь к файлу логов."""
    
    # =========================================================================
    # ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ
    # =========================================================================
    
    timezone: str = field(
        default_factory=lambda: os.getenv('TIMEZONE', 'Europe/Moscow')
    )
    """Часовой пояс для планировщика."""
    
    request_timeout: int = field(
        default_factory=lambda: int(os.getenv('REQUEST_TIMEOUT', '10'))
    )
    """Таймаут запросов к Telegram API в секундах."""
    
    disable_notifications: bool = field(
        default_factory=lambda: os.getenv('DISABLE_NOTIFICATIONS', 'false').lower() == 'true'
    )
    """Отключать уведомления в Telegram."""
    
    send_test_post: bool = field(
        default_factory=lambda: os.getenv('SEND_TEST_POST', 'true').lower() == 'true'
    )
    """Отправлять тестовый пост при запуске."""
    
    # =========================================================================
    # МЕТОДЫ ПОСТ-ОБРАБОТКИ
    # =========================================================================
    
    def __post_init__(self):
        """Пост-инициализация: преобразование путей и создание директорий."""
        project_root = Path(__file__).parent.parent
        
        # Преобразуем относительные пути в абсолютные
        if not os.path.isabs(self.data_file):
            self.data_file = str(project_root / self.data_file)
        
        if not os.path.isabs(self.history_file):
            self.history_file = str(project_root / self.history_file)
        
        if self.log_file and not os.path.isabs(self.log_file):
            self.log_file = str(project_root / self.log_file)
        
        # Создаем необходимые директории
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        data_dir = os.path.dirname(self.data_file)
        if data_dir:
            Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # МЕТОДЫ ВАЛИДАЦИИ
    # =========================================================================
    
    def validate(self) -> bool:
        """Проверяет корректность конфигурации."""
        if not self.tg_bot_token:
            raise ValueError(
                "❌ TG_BOT_TOKEN не указан.\n"
                "💡 Получите токен у @BotFather в Telegram"
            )
        
        if not self.tg_channel_id:
            raise ValueError(
                "❌ TG_CHANNEL_ID не указан.\n"
                "💡 Укажите ID канала (например @channel или -1001234567890)"
            )
        
        if not 0 <= self.publish_hour <= 23:
            raise ValueError(f"❌ publish_hour должен быть от 0 до 23, получено {self.publish_hour}")
        
        if not 0 <= self.publish_minute <= 59:
            raise ValueError(f"❌ publish_minute должен быть от 0 до 59, получено {self.publish_minute}")
        
        return True
    
    def as_dict(self) -> dict:
        """Возвращает конфигурацию в виде словаря (без секретов)."""
        config_dict = {
            'tg_channel_id': self.tg_channel_id,
            'publish_hour': self.publish_hour,
            'publish_minute': self.publish_minute,
            'data_file': self.data_file,
            'history_file': self.history_file,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'timezone': self.timezone,
            'request_timeout': self.request_timeout,
            'disable_notifications': self.disable_notifications,
            'send_test_post': self.send_test_post,
        }
        
        # Маскируем токен
        if self.tg_bot_token:
            token = self.tg_bot_token
            if len(token) > 10:
                masked = token[:6] + '...' + token[-4:]
            else:
                masked = '***'
            config_dict['tg_bot_token'] = masked
        
        return config_dict


# =============================================================================
# ГЛОБАЛЬНЫЙ ОБЪЕКТ КОНФИГУРАЦИИ
# =============================================================================

config = Config()