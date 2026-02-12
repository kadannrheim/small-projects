import logging
import sys
import signal
import os

def setup_logger(name: str, level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Настройка логирования"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый handler
    if log_file:
        try:
            # Создаем директорию если нужно
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, mode=0o755, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(f"📝 Логирование в файл: {log_file}")
        except PermissionError:
            logger.warning(f"⚠️ Нет прав на запись в {log_file}, логируем только в консоль")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось создать файл лога: {e}")
    
    return logger

def graceful_shutdown(signum, frame):
    """Обработчик graceful shutdown"""
    logger = logging.getLogger(__name__)
    logger.info(f"\nПолучен сигнал {signum}. Останавливаю бота...")
    sys.exit(0)