#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль форматирования постов "День в истории"
=============================================

Генерирует посты для Telegram с автоматической шапкой.
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
    hashtags = post_data.get('hashtags', '#деньвистории')
    
    # Формируем шапку
    header = "------------------------\n<b>ЭТОТ ДЕНЬ В ИСТОРИИ</b>\n------------------------\n"
    
    # Собираем пост
    formatted = f"{header}\n<b>{title}</b>\n\n{content}\n\n{hashtags}"
    
    return formatted