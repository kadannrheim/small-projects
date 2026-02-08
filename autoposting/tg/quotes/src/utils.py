import logging
import sys
import signal

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
    
    # Файловый handler (если указан файл)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def graceful_shutdown(signum, frame):
    """Обработчик graceful shutdown"""
    logger = logging.getLogger(__name__)
    logger.info(f"\nПолучен сигнал {signum}. Останавливаю бота...")
    sys.exit(0)