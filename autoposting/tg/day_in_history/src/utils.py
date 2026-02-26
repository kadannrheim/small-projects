#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль утилит для бота "День в истории"
========================================

Содержит вспомогательные функции:
    - Настройка логирования
    - Graceful shutdown обработчик
"""

import logging
import sys
import signal
from typing import Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(
    name: str, 
    level: str = "INFO", 
    log_file: Optional[str] = None,
    max_bytes: int = 10_485_760,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Настраивает и возвращает логгер с обработчиками для консоли и файла.
    
    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_file: Путь к файлу логов (если None, только консоль)
        max_bytes: Максимальный размер файла лога до ротации
        backup_count: Количество хранимых backup файлов
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    
    # Преобразуем строковый уровень в константу logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Предотвращаем дублирование записей
    if logger.handlers:
        logger.handlers.clear()
    
    # Создание форматтера
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    logger.addHandler(console_handler)
    
    # Файловый обработчик (если указан путь)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(numeric_level)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось создать файл лога: {e}")
    
    return logger


def graceful_shutdown(signum: int, frame) -> None:
    """
    Обработчик сигналов для корректного завершения.
    
    Args:
        signum: Номер сигнала
        frame: Текущий стек вызовов
    """
    signal_name = signal.Signals(signum).name
    logger = logging.getLogger(__name__)
    logger.info(f"🛑 Получен сигнал {signal_name}, завершаю работу...")
    sys.exit(0)