#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль форматирования коучинговых инструментов
==============================================

Генерирует кликабельные ссылки на основе названия и автора.
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
    
    # Очищаем заголовок от эмодзи для поискового запроса
    clean_title = title
    emojis = ['⚖️', '🔍', '📊', '🎯', '📈', '🧠', '🍅', '🤝', '🌱', '🪑', '📋', '🧩', '👁️', '🔗', '🔄', '🧘', '💭', '📝', '🎭', '⚡', '🪞', '🔨', '✨', '❓', '💡', '❤️', '💪', '🎁', '⏳', '🛡️', '🐸', '🔪', '📚', '🔔', '📥', '🧭', '🦋', '🔋']
    for emoji in emojis:
        clean_title = clean_title.replace(emoji, '').strip()
    
    # Формируем поисковые запросы
    search_query = urllib.parse.quote(f"{clean_title} {author}")
    video_query = urllib.parse.quote(f"{clean_title} {author} коучинг")
    
    # Генерируем кликабельные ссылки
    yandex = f"<a href='https://yandex.ru/search/?text={search_query}'>Яндекс</a>"
    google = f"<a href='https://www.google.com/search?q={search_query}'>Google</a>"
    youtube = f"<a href='https://www.youtube.com/results?search_query={video_query}'>YouTube</a>"
    rutube = f"<a href='https://rutube.ru/search/?query={video_query}'>RuTube</a>"
    
    # Собираем строку ссылок
    links = f"🔗 {yandex} • {google} • {youtube} • {rutube}"
    
    # Собираем пост
    formatted = f"{title}\n\n{content}\n\n{links}\n\n{hashtags}"
    
    return formatted