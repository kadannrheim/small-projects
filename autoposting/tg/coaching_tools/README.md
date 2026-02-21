# 🤖 Coaching Tools Telegram Bot

Автоматическая публикация коучинговых инструментов в Telegram канал.

## 📋 Описание

Бот ежедневно публикует один коучинговый инструмент с ссылками на:
- Яндекс
- Google
- Википедию
- YouTube
- RuTube

## 🚀 Быстрый старт

1. Клонируйте репозиторий
2. Скопируйте `.env.example` в `.env` и заполните токен и ID канала
3. Заполните `data/coaching_tools.json` своими инструментами
4. Запустите:
   ```bash
   docker-compose up -d

# Файловая структура 
```bash
coaching_tools/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt.txt
├── README.md
├── data/
│   ├── coaching_tools.json
│   └── history.json
├── logs/
│   └── bot.log
└── src/
    ├── bot.py
    ├── config.py
    ├── formatter.py
    ├── history.py
    └── utils.py
```

# Структура данных
```json
[
  {
    "id": 1,
    "title": "Название",
    "content": "Описание",
    "author": "Автор",
    "hashtags": "#теги",
    "type": "exercise|technique|tool",
    "duration_minutes": 15,
    "difficulty": "easy|medium|hard"
  }
]
```

# Мониторинг
Логи: docker-compose logs -f
История публикаций: data/history.json