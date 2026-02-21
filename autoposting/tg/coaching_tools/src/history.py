#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль истории публикаций
=========================

Универсальный модуль для отслеживания публикаций любых типов контента.
Поддерживает:
    - Цитаты (ключ = текст цитаты)
    - Коучинговые инструменты (ключ = название инструмента)
"""

import json
import os
import datetime
import logging
from typing import Dict, List, Optional, Any, Set, Union
from pathlib import Path
from collections import defaultdict

from config import config

logger = logging.getLogger(__name__)


class PublicationHistory:
    """
    Класс для отслеживания истории публикаций.
    
    Универсальное хранилище: может работать с любым типом контента.
    Ключом может быть текст (для цитат) или название (для инструментов).
    """
    
    def __init__(self, history_file: Optional[str] = None):
        """Инициализация истории публикаций."""
        self.history_file = history_file or config.history_file
        logger.debug(f"Инициализация истории публикаций, файл: {self.history_file}")
        
        self.history: Dict[str, str] = {}
        self._load_history()
        
        logger.info(f"✅ История публикаций загружена: {len(self.history)} записей")
    
    # =========================================================================
    # ПРИВАТНЫЕ МЕТОДЫ РАБОТЫ С ФАЙЛАМИ
    # =========================================================================
    
    def _load_history(self) -> None:
        """Загружает историю публикаций из JSON файла."""
        history_path = Path(self.history_file)
        
        if not history_path.exists():
            logger.info(f"📁 Файл истории не найден, будет создан новый: {self.history_file}")
            self.history = {}
            return
        
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                # Валидация формата дат
                valid_history = {}
                invalid_dates = 0
                
                for key, date_str in data.items():
                    try:
                        datetime.datetime.strptime(date_str, '%Y-%m-%d')
                        valid_history[key] = date_str
                    except (ValueError, TypeError):
                        invalid_dates += 1
                        logger.warning(f"⚠️ Неверный формат даты для ключа: {key[:50]}... = {date_str}")
                
                self.history = valid_history
                
                if invalid_dates > 0:
                    logger.warning(f"⚠️ Пропущено {invalid_dates} записей с неверными датами")
                
                logger.info(f"✅ Загружена история публикаций: {len(self.history)} записей")
            else:
                logger.error(f"❌ Неверный формат истории: ожидался dict, получен {type(data)}")
                self._backup_corrupted_file()
                self.history = {}
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга файла истории: {e}")
            self._backup_corrupted_file()
            self.history = {}
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при загрузке истории: {e}")
            self.history = {}
    
    def _backup_corrupted_file(self) -> None:
        """Создает резервную копию поврежденного файла истории."""
        try:
            history_path = Path(self.history_file)
            if history_path.exists():
                backup_name = f"{history_path}.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                history_path.rename(backup_name)
                logger.info(f"💾 Создана резервная копия: {backup_name}")
        except Exception as e:
            logger.error(f"❌ Не удалось создать резервную копию: {e}")
    
    def _save_history(self) -> bool:
        """Сохраняет историю публикаций в JSON файл."""
        history_path = Path(self.history_file)
        
        try:
            history_path.parent.mkdir(parents=True, exist_ok=True)
            
            temp_file = history_path.with_suffix('.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.history, 
                    f, 
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True
                )
            
            os.replace(temp_file, history_path)
            
            logger.debug(f"💾 История сохранена: {len(self.history)} записей")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения истории: {e}")
            return False
    
    # =========================================================================
    # ПУБЛИЧНЫЕ МЕТОДЫ
    # =========================================================================
    
    def is_published_recently(self, key: str, days: int = 365) -> bool:
        """
        Проверяет, публиковался ли элемент за последние N дней.
        
        Args:
            key: Уникальный ключ элемента (текст цитаты или название инструмента)
            days: Количество дней для проверки
            
        Returns:
            True если публиковался в указанном периоде
        """
        if key not in self.history:
            logger.debug(f"Элемент никогда не публиковался: {key[:50]}...")
            return False
        
        last_date_str = self.history[key]
        
        try:
            last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d').date()
            today = datetime.datetime.now().date()
            days_diff = (today - last_date).days
            
            logger.debug(f"Элемент публиковался {days_diff} дней назад")
            return days_diff < days
            
        except ValueError as e:
            logger.error(f"❌ Ошибка парсинга даты '{last_date_str}': {e}")
            return False
    
    def mark_published(self, key: str) -> bool:
        """
        Отмечает элемент как опубликованный сегодня.
        
        Args:
            key: Уникальный ключ элемента (текст цитаты или название инструмента)
            
        Returns:
            bool: True если успешно сохранено
        """
        today = datetime.datetime.now().date().isoformat()
        
        self.history[key] = today
        logger.info(f"📝 Отмечена публикация: {key[:50]}... -> {today}")
        
        if self._save_history():
            logger.debug("История успешно сохранена")
            return True
        else:
            logger.error("❌ Не удалось сохранить историю")
            return False
    
    def get_available_quotes(self, items: List[Dict[str, Any]], days: int = 365, key_field: str = 'text') -> List[Dict[str, Any]]:
        """
        Возвращает список элементов, которые можно опубликовать.
        
        Args:
            items: Список всех элементов (цитат или инструментов)
            days: Период проверки в днях
            key_field: Поле, используемое как уникальный ключ ('text' для цитат, 'title' для инструментов)
        
        Returns:
            Список доступных для публикации элементов
        """
        available = []
        skipped = 0
        
        for item in items:
            # Получаем ключ (текст или название)
            key = item.get(key_field, '')
            
            if not key:
                skipped += 1
                continue
            
            if not self.is_published_recently(key, days):
                available.append(item)
        
        if skipped > 0:
            logger.debug(f"Пропущено {skipped} элементов без поля '{key_field}'")
        
        logger.debug(f"Найдено {len(available)} доступных элементов из {len(items)}")
        return available
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику публикаций."""
        total = len(self.history)
        
        if total == 0:
            return {
                "total": 0,
                "last_30_days": 0,
                "oldest": None,
                "newest": None,
                "by_year": {},
                "by_month": {}
            }
        
        today = datetime.datetime.now().date()
        last_30_days = 0
        dates = []
        years = defaultdict(int)
        months = defaultdict(int)
        
        for date_str in self.history.values():
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                dates.append(date)
                years[date.year] += 1
                month_key = date.strftime('%Y-%m')
                months[month_key] += 1
                
                if (today - date).days <= 30:
                    last_30_days += 1
            except ValueError:
                continue
        
        sorted_months = dict(sorted(months.items(), reverse=True)[:12])
        
        return {
            "total": total,
            "last_30_days": last_30_days,
            "oldest": min(dates).isoformat() if dates else None,
            "newest": max(dates).isoformat() if dates else None,
            "by_year": dict(years),
            "by_month": sorted_months
        }
    
    def reset_history(self) -> bool:
        """Полностью сбрасывает историю для нового цикла."""
        logger.warning("⚠️ СБРОС ИСТОРИИ ПУБЛИКАЦИЙ!")
        
        self.history.clear()
        
        if self._save_history():
            logger.info("📆 История публикаций сброшена")
            return True
        else:
            logger.error("❌ Не удалось сохранить историю после сброса")
            return False


# =============================================================================
# ГЛОБАЛЬНЫЙ ОБЪЕКТ ИСТОРИИ
# =============================================================================

history = PublicationHistory()