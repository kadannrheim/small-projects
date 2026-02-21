#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль утилит Telegram Quotes Bot
=================================

Этот модуль содержит вспомогательные функции и классы, используемые в проекте:
    - Настройка логирования (консоль + файл)
    - Graceful shutdown обработчики
    - Декораторы для повторных попыток (retry logic)
    - Работа с сигналами
    - Вспомогательные функции для работы с файлами

Все функции спроектированы для максимальной надежности и повторного использования.

Автор: kadannr
Версия: 1.0.0
"""

import logging
import sys
import signal
import os
import time
import functools
from typing import Optional, Callable, Any, Type, Union, Tuple
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


# =============================================================================
# НАСТРОЙКА ЛОГГЕРА
# =============================================================================

def setup_logger(
    name: str, 
    level: str = "INFO", 
    log_file: Optional[str] = None,
    max_bytes: int = 10_485_760,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Настраивает и возвращает логгер с обработчиками для консоли и файла.
    
    Эта функция создает логгер с двумя обработчиками:
        1. Консольный (stdout) - для Docker и интерактивной отладки
        2. Файловый (с ротацией) - для постоянного хранения логов
    
    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_file: Путь к файлу логов (если None, только консоль)
        max_bytes: Максимальный размер файла лога до ротации
        backup_count: Количество хранимых backup файлов
    
    Returns:
        logging.Logger: Настроенный логгер
        
    Examples:
        >>> logger = setup_logger(__name__, "DEBUG", "logs/app.log")
        >>> logger.info("Бот запущен")
        >>> logger.error("Ошибка соединения")
    
    Note:
        Файловый обработчик использует RotatingFileHandler для автоматической
        ротации логов при достижении максимального размера.
    """
    # -------------------------------------------------------------------------
    # Шаг 1: Создание логгера
    # -------------------------------------------------------------------------
    logger = logging.getLogger(name)
    
    # Преобразуем строковый уровень в константу logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Предотвращаем дублирование записей (если логгер уже настроен)
    if logger.handlers:
        logger.handlers.clear()
    
    # -------------------------------------------------------------------------
    # Шаг 2: Создание форматтера
    # -------------------------------------------------------------------------
    # Формат: время - имя - уровень - сообщение
    # Пример: 2026-02-20 10:30:15 - bot - INFO - Бот запущен
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # -------------------------------------------------------------------------
    # Шаг 3: Консольный обработчик
    # -------------------------------------------------------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)  # Используем тот же уровень
    logger.addHandler(console_handler)
    
    # -------------------------------------------------------------------------
    # Шаг 4: Файловый обработчик (если указан путь)
    # -------------------------------------------------------------------------
    if log_file:
        try:
            # Создаем директорию для логов, если нужно
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Используем RotatingFileHandler для автоматической ротации
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(numeric_level)
            logger.addHandler(file_handler)
            
            logger.info(f"📝 Логирование в файл: {log_file} (ротация при {max_bytes/1024/1024:.0f} MB)")
            
        except PermissionError:
            logger.warning(f"⚠️ Нет прав на запись в {log_file}, логируем только в консоль")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось создать файл лога: {e}")
    
    return logger


# =============================================================================
# GLOBAL SHUTDOWN MANAGER
# =============================================================================

class ShutdownManager:
    """
    Менеджер корректного завершения работы (Graceful Shutdown).
    
    Этот класс позволяет зарегистрировать несколько обработчиков,
    которые будут вызваны при получении сигналов завершения (SIGINT, SIGTERM).
    
    Особенности:
        - Поддержка множественных обработчиков
        - Защита от повторных сигналов
        - Таймаут на выполнение обработчиков
        - Детальное логирование
    
    Attributes:
        shutdown_handlers (List[Callable]): Список зарегистрированных обработчиков
        shutdown_requested (bool): Флаг, был ли запрошен graceful shutdown
        timeout (int): Максимальное время на выполнение всех обработчиков (секунды)
    
    Example:
        >>> manager = ShutdownManager()
        >>> manager.register_handler(lambda: logger.info("Сохраняю данные..."))
        >>> manager.register_handler(lambda: logger.info("Закрываю соединения..."))
    """
    
    def __init__(self, timeout: int = 30):
        """
        Инициализация менеджера завершения.
        
        Args:
            timeout: Максимальное время на выполнение всех обработчиков (секунды)
        """
        self.shutdown_handlers: list[Callable[[], Any]] = []
        self.shutdown_requested = False
        self.timeout = timeout
        self._start_time: Optional[float] = None
        self.logger = logging.getLogger(__name__)
        
        # Регистрируем обработчики сигналов
        signal.signal(signal.SIGINT, self._handle_signal)   # Ctrl+C
        signal.signal(signal.SIGTERM, self._handle_signal)  # docker stop
        
        self.logger.debug("ShutdownManager инициализирован")
    
    def register_handler(self, handler: Callable[[], Any]) -> None:
        """
        Регистрирует функцию, которая будет вызвана при завершении.
        
        Args:
            handler: Функция без аргументов
            
        Example:
            >>> def save_data():
            ...     print("Сохранение...")
            >>> manager.register_handler(save_data)
        """
        self.shutdown_handlers.append(handler)
        self.logger.debug(f"Зарегистрирован обработчик: {handler.__name__}")
    
    def _handle_signal(self, signum: int, frame: Any) -> None:
        """
        Обрабатывает сигналы завершения.
        
        Args:
            signum: Номер сигнала
            frame: Текущий стек вызовов (не используется)
        """
        # Защита от повторных сигналов
        if self.shutdown_requested:
            signal_name = signal.Signals(signum).name
            self.logger.warning(f"⚠️ Повторный сигнал {signal_name}, принудительный выход...")
            sys.exit(1)
        
        self.shutdown_requested = True
        self._start_time = time.time()
        
        signal_name = signal.Signals(signum).name
        self.logger.info(f"🛑 Получен сигнал {signal_name}, начинаем корректное завершение...")
        
        self._graceful_shutdown()
    
    def _graceful_shutdown(self) -> None:
        """
        Выполняет все зарегистрированные обработчики и завершает работу.
        
        Каждый обработчик выполняется с проверкой общего таймаута.
        Если обработчики не укладываются в таймаут - принудительный выход.
        """
        self.logger.info(f"🛑 Выполняется graceful shutdown (таймаут: {self.timeout}с)")
        
        for i, handler in enumerate(self.shutdown_handlers, 1):
            # Проверяем общий таймаут
            elapsed = time.time() - self._start_time
            if elapsed > self.timeout:
                self.logger.error(f"⏱️ Таймаут завершения ({self.timeout}с), принудительный выход")
                sys.exit(1)
            
            try:
                self.logger.info(f"🔄 Выполняю обработчик {i}/{len(self.shutdown_handlers)}: {handler.__name__}")
                handler()
                self.logger.info(f"✅ Обработчик {handler.__name__} выполнен")
            except Exception as e:
                self.logger.error(f"❌ Ошибка в обработчике {handler.__name__}: {e}")
                self.logger.exception("Детали ошибки:")
        
        self.logger.info("👋 Все обработчики выполнены, завершение работы")
        sys.exit(0)
    
    def is_shutdown_requested(self) -> bool:
        """
        Проверяет, был ли запрошен graceful shutdown.
        
        Returns:
            True если был получен сигнал завершения
        """
        return self.shutdown_requested


# =============================================================================
# RETRY DECORATOR
# =============================================================================

def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Декоратор для повторных попыток выполнения функции при ошибках.
    
    Особенности:
        - Экспоненциальная задержка между попытками (backoff)
        - Возможность указать конкретные исключения для retry
        - Детальное логирование каждой попытки
        - Максимальное количество попыток
    
    Args:
        max_retries: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Множитель увеличения задержки (exponential backoff)
        exceptions: Исключения, при которых нужно повторять
        logger: Логгер для записи событий (если None, используется стандартный)
    
    Returns:
        Callable: Декорированная функция
    
    Examples:
        >>> @retry(max_retries=3, delay=1, backoff=2)
        ... def unstable_function():
        ...     return requests.get("https://api.example.com")
        
        >>> @retry(exceptions=(ConnectionError, TimeoutError))
        ... def send_message():
        ...     return telegram_api.send("Hello")
    
    Note:
        При исчерпании всех попыток исключение пробрасывается наружу.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Используем переданный логгер или получаем из функции
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)
            
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    if attempt > 1:
                        logger.info(f"🔄 Попытка {attempt}/{max_retries} для {func.__name__}")
                    
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Последняя попытка - выходим из цикла
                        logger.error(f"❌ Все {max_retries} попыток для {func.__name__} исчерпаны")
                        break
                    
                    # Логируем ошибку и ждем
                    logger.warning(
                        f"⚠️ Ошибка {attempt}/{max_retries} в {func.__name__}: {e}. "
                        f"Ждем {current_delay:.1f}с перед следующей попыткой..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff  # Exponential backoff
            
            # Если все попытки исчерпаны - пробрасываем последнее исключение
            raise last_exception
            
        return wrapper
    return decorator


# =============================================================================
# GRACEFUL SHUTDOWN FUNCTION (FOR BACKWARD COMPATIBILITY)
# =============================================================================

# Создаем глобальный экземпляр менеджера
_shutdown_manager = ShutdownManager()

def graceful_shutdown(signum: int, frame: Any) -> None:
    """
    Функция для обратной совместимости с существующим кодом.
    
    Args:
        signum: Номер сигнала
        frame: Текущий стек вызовов
    """
    _shutdown_manager._handle_signal(signum, frame)

def register_shutdown_handler(handler: Callable[[], Any]) -> None:
    """
    Регистрирует обработчик для graceful shutdown.
    
    Args:
        handler: Функция без аргументов
    """
    _shutdown_manager.register_handler(handler)

def is_shutdown_requested() -> bool:
    """
    Проверяет, был ли запрошен graceful shutdown.
    
    Returns:
        True если получен сигнал завершения
    """
    return _shutdown_manager.is_shutdown_requested()


# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def ensure_directory(path: Union[str, Path]) -> bool:
    """
    Гарантирует существование директории.
    
    Args:
        path: Путь к директории
        
    Returns:
        bool: True если директория существует или создана
        
    Example:
        >>> if ensure_directory("logs"):
        ...     print("Директория готова")
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Не удалось создать директорию {path}: {e}")
        return False


def get_timestamp() -> str:
    """
    Возвращает текущий timestamp в формате для имен файлов.
    
    Returns:
        str: Timestamp в формате YYYYMMDD_HHMMSS
        
    Example:
        >>> filename = f"backup_{get_timestamp()}.json"
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def safe_file_write(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """
    Безопасно записывает содержимое в файл (атомарная операция).
    
    Args:
        file_path: Путь к файлу
        content: Содержимое для записи
        encoding: Кодировка
        
    Returns:
        bool: True если запись успешна
        
    Example:
        >>> safe_file_write("data.json", json.dumps(data))
    """
    file_path = Path(file_path)
    
    try:
        # Создаем директорию
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Запись во временный файл
        temp_file = file_path.with_suffix('.tmp')
        temp_file.write_text(content, encoding=encoding)
        
        # Атомарная замена
        temp_file.replace(file_path)
        
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Ошибка записи в файл {file_path}: {e}")
        return False


# =============================================================================
# КОНТЕКСТНЫЙ МЕНЕДЖЕР ДЛЯ TIMEOUT
# =============================================================================

import signal as sig

class Timeout:
    """
    Контекстный менеджер для ограничения времени выполнения блока кода.
    
    Args:
        seconds: Максимальное время выполнения в секундах
        error_message: Сообщение об ошибке при таймауте
        
    Example:
        >>> with Timeout(5):
        ...     requests.get("https://api.example.com")
    
    Note:
        Работает только в Unix-подобных системах (Linux, macOS).
        В Windows используется fallback без таймаута.
    """
    
    def __init__(self, seconds: int, error_message: str = "Таймаут операции"):
        self.seconds = seconds
        self.error_message = error_message
    
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    
    def __enter__(self):
        if hasattr(sig, 'SIGALRM'):  # Только Unix
            sig.signal(sig.SIGALRM, self.handle_timeout)
            sig.alarm(self.seconds)
    
    def __exit__(self, type, value, traceback):
        if hasattr(sig, 'SIGALRM'):  # Только Unix
            sig.alarm(0)
# =============================================================================
# КОНЕЦ ФАЙЛА
# =============================================================================