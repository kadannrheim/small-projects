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
    author = tool_data.get('author', 'Неизвестный автор')
    hashtags = tool_data.get('hashtags', '#коучинговые_инструменты')
    duration = tool_data.get('duration_minutes', '')
    
    # Формируем поисковые запросы
    search_query = f"{title} {author}"
    encoded_query = urllib.parse.quote(search_query)
    video_query = urllib.parse.quote(f"{title} коучинг")
    
    # Ссылки на все источники
    links = [
        f"<a href='https://yandex.ru/search/?text={encoded_query}'>Яндекс</a>",
        f"<a href='https://www.google.com/search?q={encoded_query}'>Google</a>",
        f"<a href='https://ru.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}'>Википедия</a>",
        f"<a href='https://www.youtube.com/results?search_query={video_query}'>YouTube</a>",
        f"<a href='https://rutube.ru/search/?query={video_query}'>RuTube</a>"
    ]
    
    # Собираем пост
    formatted = f"{title}\n\n{content}\n\n"
    
    if duration:
        formatted += f"⏱️ {duration} минут | Автор: {author}\n\n"
    else:
        formatted += f"Автор: {author}\n\n"
    
    formatted += "🔗 " + " • ".join(links) + "\n\n"
    formatted += hashtags
    
    return formatted