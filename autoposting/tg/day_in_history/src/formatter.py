#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль форматирования постов "День в истории"
=============================================

Генерирует посты для Telegram.
"""

from typing import Dict, Any


def format_post(post_data: Dict[str, Any]) -> str:
    """
    Форматирует пост для отправки в Telegram.
    
    Args:
        post_data: Данные поста из JSON
        
    Returns:
        str: Отформатированный пост для публикации
    """
    # Извлекаем данные
    title = post_data.get('title', 'День в истории')
    content = post_data.get('content', '')
    lesson = post_data.get('lesson', '')
    hashtags = post_data.get('hashtags', '#деньвистории')
    
    # Формируем урок, если есть
    lesson_text = f"\n\n💡 {lesson}" if lesson else ""
    
    # Собираем пост
    formatted = f"{title}\n\n{content}{lesson_text}\n\n{hashtags}"
    
    return formatted