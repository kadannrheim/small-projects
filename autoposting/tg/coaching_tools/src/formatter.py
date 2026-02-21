#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль форматирования коучинговых инструментов
==============================================

Отвечает за красивое оформление постов с ссылками на все поисковики.
"""

import urllib.parse
from typing import Dict, Any


def format_tool(tool_data: Dict[str, Any]) -> str:
    """
    Форматирует коучинговый инструмент для отправки в Telegram.
    
    Args:
        tool_data: Данные инструмента из JSON
        
    Returns:
        str: Отформатированный пост для публикации
    """
    # Извлекаем данные
    title = tool_data.get('title', 'Коучинговый инструмент')
    content = tool_data.get('content', '')
    hashtags = tool_data.get('hashtags', '#коучинговые_инструменты')
    
    # Собираем пост
    formatted = f"{title}\n\n{content}\n\n{hashtags}"
    
    return formatted