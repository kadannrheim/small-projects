#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль конфигурации Coaching Tools Bot
=======================================

Настройки для бота с коучинговыми инструментами.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv

# =============================================================================
# ЗАГРУЗКА .ENV ФАЙЛА
# =============================================================================

env_path = Path(__file__).parent.parent / '../.env'

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
    Конфигурация приложения для коучинговых инструментов.
    """
    
    # =========================================================================
    # TELEGRAM НАСТРОЙКИ (ОБЯЗАТЕЛЬНЫЕ)
    # =========================================================================
    
    tg_coaching_bot_token: str = field(
        default_factory=lambda: os.getenv('TG_COACHING_BOT_TOKEN', '')
    )
    """Токен бота от @BotFather для коучингового бота."""
    
    tg_coaching_channel_id: str = field(
        default_factory=lambda: os.getenv('TG_COACHING_CHANNEL_ID', '')
    )
    """ID канала для публикаций коучинговых инструментов."""
    
    # =========================================================================
    # НАСТРОЙКИ ПЛАНИРОВЩИКА
    # =========================================================================
    
    base_hour: int = field(
        default_factory=lambda: int(os.getenv('BASE_HOUR', '10'))
    )
    """Час базового времени публикации (0-23)."""
    
    base_minute: int = field(
        default_factory=lambda: int(os.getenv('BASE_MINUTE', '0'))
    )
    """Минута базового времени публикации (0-59)."""
    
    random_range_minutes: int = field(
        default_factory=lambda: int(os.getenv('RANDOM_RANGE_MINUTES', '30'))
    )
    """Диапазон случайного смещения в минутах."""
    
    # =========================================================================
    # НАСТРОЙКИ ФАЙЛОВ
    # =========================================================================
    
    tools_file: str = field(
        default_factory=lambda: os.getenv('TOOLS_FILE', 'data/coaching_tools.json')
    )
    """Путь к файлу с коучинговыми инструментами."""
    
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
    
    send_test_tool: bool = field(
        default_factory=lambda: os.getenv('SEND_TEST_TOOL', 'true').lower() == 'true'
    )
    """Отправлять тестовый инструмент при запуске."""
    
    # =========================================================================
    # МЕТОДЫ ПОСТ-ОБРАБОТКИ
    # =========================================================================
    
    def __post_init__(self):
        """Пост-инициализация: преобразование путей и создание директорий."""
        project_root = Path(__file__).parent.parent
        
        # Преобразуем относительные пути в абсолютные
        if not os.path.isabs(self.tools_file):
            self.tools_file = str(project_root / self.tools_file)
        
        if not os.path.isabs(self.history_file):
            self.history_file = str(project_root / self.history_file)
        
        if self.log_file and not os.path.isabs(self.log_file):
            self.log_file = str(project_root / self.log_file)
        
        # Создаем необходимые директории
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        data_dir = os.path.dirname(self.tools_file)
        if data_dir:
            Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # МЕТОДЫ ВАЛИДАЦИИ
    # =========================================================================
    
    def validate(self) -> bool:
        """Проверяет корректность конфигурации."""
        if not self.tg_coaching_bot_token:
            raise ValueError(
                "❌ TG_COACHING_BOT_TOKEN не указан.\n"
                "💡 Получите токен у @BotFather в Telegram"
            )
        
        if not self.tg_coaching_channel_id:
            raise ValueError(
                "❌ TG_COACHING_CHANNEL_ID не указан.\n"
                "💡 Укажите ID канала (например @channel или -1001234567890)"
            )
        
        if not 0 <= self.base_hour <= 23:
            raise ValueError(f"❌ base_hour должен быть от 0 до 23, получено {self.base_hour}")
        
        if not 0 <= self.base_minute <= 59:
            raise ValueError(f"❌ base_minute должен быть от 0 до 59, получено {self.base_minute}")
        
        return True
    
    def as_dict(self) -> dict:
        """Возвращает конфигурацию в виде словаря (без секретов)."""
        config_dict = {
            'tg_coaching_channel_id': self.tg_coaching_channel_id,
            'base_hour': self.base_hour,
            'base_minute': self.base_minute,
            'random_range_minutes': self.random_range_minutes,
            'tools_file': self.tools_file,
            'history_file': self.history_file,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'timezone': self.timezone,
            'request_timeout': self.request_timeout,
            'disable_notifications': self.disable_notifications,
            'send_test_tool': self.send_test_tool,
        }
        
        # Маскируем токен
        if self.tg_coaching_bot_token:
            token = self.tg_coaching_bot_token
            if len(token) > 10:
                masked = token[:6] + '...' + token[-4:]
            else:
                masked = '***'
            config_dict['tg_coaching_bot_token'] = masked
        
        return config_dict


# =============================================================================
# ГЛОБАЛЬНЫЙ ОБЪЕКТ КОНФИГУРАЦИИ
# =============================================================================

config = Config()