#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль истории публикаций "День в истории"
==========================================

Отслеживает, какие посты уже публиковались в текущем году.
Ключом является ID поста (str).
"""

import json
import os
import datetime
import logging
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from collections import defaultdict

from config import config

logger = logging.getLogger(__name__)


class PublicationHistory:
    """
    Класс для отслеживания истории публикаций.
    
    Хранит даты последней публикации для каждого ID поста.
    """
    
    def __init__(self, history_file: Optional[str] = None):
        """Инициализация истории публикаций."""
        self.history_file = history_file or config.history_file
        logger.debug(f"Инициализация истории публикаций, файл: {self.history_file}")
        
        self.history: Dict[str, str] = {}  # id -> дата публикации (YYYY-MM-DD)
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
                        logger.warning(f"⚠️ Неверный формат даты для ID {key}: {date_str}")
                
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
    
    def is_published_recently(self, post_id: str, days: int = 365) -> bool:
        """
        Проверяет, публиковался ли пост за последние N дней.
        
        Args:
            post_id: ID поста
            days: Количество дней для проверки
            
        Returns:
            True если публиковался в указанном периоде
        """
        if post_id not in self.history:
            logger.debug(f"Пост ID={post_id} никогда не публиковался")
            return False
        
        last_date_str = self.history[post_id]
        
        try:
            last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d').date()
            today = datetime.datetime.now().date()
            days_diff = (today - last_date).days
            
            logger.debug(f"Пост ID={post_id} публиковался {days_diff} дней назад")
            return days_diff < days
            
        except ValueError as e:
            logger.error(f"❌ Ошибка парсинга даты '{last_date_str}': {e}")
            return False
    
    def is_published_this_year(self, post_id: str) -> bool:
        """
        Проверяет, публиковался ли пост в текущем году.
        
        Args:
            post_id: ID поста
            
        Returns:
            True если публиковался в этом году
        """
        if post_id not in self.history:
            return False
        
        last_date_str = self.history[post_id]
        
        try:
            last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d').date()
            today = datetime.datetime.now().date()
            
            return last_date.year == today.year
            
        except ValueError:
            return False
    
    def mark_published(self, post_id: str) -> bool:
        """
        Отмечает пост как опубликованный сегодня.
        
        Args:
            post_id: ID поста
            
        Returns:
            bool: True если успешно сохранено
        """
        today = datetime.datetime.now().date().isoformat()
        
        self.history[post_id] = today
        logger.info(f"📝 Отмечена публикация поста ID={post_id} -> {today}")
        
        if self._save_history():
            logger.debug("История успешно сохранена")
            return True
        else:
            logger.error("❌ Не удалось сохранить историю")
            return False
    
    def get_available_for_today(self, posts: List[Dict[str, Any]], today_md: str) -> List[Dict[str, Any]]:
        """
        Возвращает список постов на сегодня, которые ещё не публиковались в этом году.
        
        Args:
            posts: Список всех постов
            today_md: Сегодняшняя дата в формате MM-DD
            
        Returns:
            Список доступных для публикации постов на сегодня
        """
        # Находим все посты на сегодняшнюю дату
        today_posts = [p for p in posts if p.get('month_day') == today_md]
        
        if not today_posts:
            return []
        
        # Фильтруем те, что ещё не публиковались в этом году
        available = []
        for post in today_posts:
            post_id = str(post.get('id', ''))
            if not post_id:
                logger.warning(f"⚠️ Пост без ID пропущен: {post.get('title', '')}")
                continue
                
            if not self.is_published_this_year(post_id):
                available.append(post)
        
        logger.debug(f"Из {len(today_posts)} постов на {today_md} доступно {len(available)}")
        return available
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику публикаций."""
        total = len(self.history)
        
        if total == 0:
            return {
                "total": 0,
                "this_year": 0,
                "last_30_days": 0,
                "oldest": None,
                "newest": None,
                "by_year": {},
                "by_month": {}
            }
        
        today = datetime.datetime.now().date()
        this_year = 0
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
                
                if date.year == today.year:
                    this_year += 1
                
                if (today - date).days <= 30:
                    last_30_days += 1
            except ValueError:
                continue
        
        sorted_months = dict(sorted(months.items(), reverse=True)[:12])
        
        return {
            "total": total,
            "this_year": this_year,
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
    
    def get_posts_for_date(self, month_day: str) -> List[str]:
        """
        Возвращает список ID постов, публиковавшихся в указанную дату (MM-DD).
        Полезно для отладки.
        
        Args:
            month_day: Дата в формате MM-DD
            
        Returns:
            Список ID постов
        """
        result = []
        for post_id, date_str in self.history.items():
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                if date.strftime("%m-%d") == month_day:
                    result.append(post_id)
            except ValueError:
                continue
        return result


# =============================================================================
# ГЛОБАЛЬНЫЙ ОБЪЕКТ ИСТОРИИ
# =============================================================================

history = PublicationHistory()