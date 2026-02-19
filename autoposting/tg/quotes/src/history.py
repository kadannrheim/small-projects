import json
import os
import datetime
import logging  # <-- ДОБАВЛЕНО!
from typing import Dict, List, Optional, Set
from config import config

# Настраиваем логгер для истории
logger = logging.getLogger(__name__)  # <-- ДОБАВЛЕНО!

class PublicationHistory:
    """Класс для отслеживания истории публикаций цитат"""
    
    def __init__(self, history_file: str = None):
        self.history_file = history_file or config.history_file
        self.history = self._load_history()
    
    def _load_history(self) -> Dict[str, str]:
        """Загружает историю публикаций из файла"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_history(self):
        """Сохраняет историю публикаций в файл"""
        try:
            # Создаем директорию если нужно
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")
    
    def is_published_recently(self, quote_text: str, days: int = 365) -> bool:
        """
        Проверяет, публиковалась ли цитата за последние N дней
        
        Args:
            quote_text: текст цитаты
            days: количество дней для проверки (по умолчанию 365)
        
        Returns:
            True если публиковалась, False если нет
        """
        if quote_text not in self.history:
            return False
        
        last_date_str = self.history[quote_text]
        try:
            last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d').date()
            today = datetime.datetime.now().date()
            days_diff = (today - last_date).days
            return days_diff < days
        except ValueError:
            return False
    
    def mark_published(self, quote_text: str):
        """Отмечает цитату как опубликованную сегодня"""
        today = datetime.datetime.now().date().isoformat()
        self.history[quote_text] = today
        self._save_history()
    
    def get_available_quotes(self, quotes: List[Dict], days: int = 365) -> List[Dict]:
        """
        Возвращает список цитат, которые можно опубликовать
        
        Args:
            quotes: список всех цитат
            days: период проверки в днях
        
        Returns:
            список доступных цитат
        """
        available = []
        for quote in quotes:
            text = quote.get('text', '')
            if not self.is_published_recently(text, days):
                available.append(quote)
        return available
    
    def get_stats(self) -> Dict:
        """Возвращает статистику публикаций"""
        total = len(self.history)
        if total == 0:
            return {"total": 0, "last_30_days": 0, "oldest": None, "newest": None}
        
        # Считаем публикации за последние 30 дней
        today = datetime.datetime.now().date()
        last_30_days = 0
        dates = []
        
        for date_str in self.history.values():
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                dates.append(date)
                if (today - date).days <= 30:
                    last_30_days += 1
            except ValueError:
                continue
        
        return {
            "total": total,
            "last_30_days": last_30_days,
            "oldest": min(dates).isoformat() if dates else None,
            "newest": max(dates).isoformat() if dates else None
        }
    
    def reset_history(self):
        """Полностью сбрасывает историю для нового цикла"""
        self.history.clear()
        self._save_history()
        logger.info("📆 История публикаций сброшена - начинаем новый годовой цикл!")

# Глобальный объект истории
history = PublicationHistory()