# Telegram Quotes Bot

Бот для автоматической публикации цитат в Telegram канал.

# Файловая структура
```
.
├── autoposting
│   ├── README.md
│   └── tg
│       ├── docker-compose.yml
│       ├── logs
│       │   └── bot.log
│       └── quotes
│           ├── data
│           │   ├── published_history.json
│           │   ├── quotes365.json
│           │   └── quotes-example.json
│           ├── Dockerfile
│           ├── .env
│           ├── .env.example
│           ├── requirements
│           └── src
│               ├── bot.py
│               ├── config.py
│               ├── history.py
│               └── utils.py
└── README.md
└── notes.md
└── .gitignore
```
# Хранение секретов
Секреты в менеджере паролей
Конфиги синхронизируйте через облако или локально через симлинк (что бы не попали в гит или добавьте файл .env в gitignore), чувствительные данные (включая цитаты) находятся в файлах (в проекте они добавлены в gitignore): 
```
tg
├── bot.log
  quotes
  └── .env
    data
    ├── quotes356.json
    └── published_history.json
```

## Установка

1. Склонируйте репозиторий
2. Создайте файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env

3. Заполните .env своими значениями:
Получите токен бота у @BotFather
Укажите ID вашего канала (например, @mychannel)
4. Установите зависимости:
`pip install -r requirements.txt`
----
# Запуск (в проекте использовал основной через docker-compose с .env = "docker-compose up -d", дополнительные указаны для отладки)
## Локально
`python src/bot.py`
## Docker
`docker-compose up -d`
## Docker без docker-compose
```bash
docker build -t quotes-bot .
docker run -d --name quotes-bot \
  -e BOT_TOKEN="your_token" \
  -e CHANNEL_ID="@your_channel" \
  quotes-bot
```
----
# Основные настройки в .env файле:
```
BOT_TOKEN - токен бота от @BotFather
CHANNEL_ID - ID канала (начинается с @)
BASE_HOUR - час публикации (по умолчанию 9)
BASE_MINUTE - минута публикации (по умолчанию 0)
RANDOM_RANGE_MINUTES - случайное смещение в минутах (по умолчанию ±30)
```
----
# Добавление цитат
## Добавляйте цитаты в файл data/quotes.json в формате:
```json
[
  {
    "text": "Текст цитаты",
    "author": "Автор",
    "hashtag": "#тег"
  }
]
```
----
# Развёртывание
## 1. Инициализируйте git (ветка main):
```bash
git init
git clone https://github.com/kadannrheim/small-projects.git
```

## 5. Хранение персоналифицированной информации (для тех кто разворачивает на своём пк). 
Хранится отдельно локально\облачная папка, создаётся симлинк для добавления цитат в проект через cmd:

### Хранение цитат (windows симлинк)
```md   
# Запустите cmd от имени Администратора
# (Win + R → cmd → Ctrl+Shift+Enter)

# Перейдите в папку c git (где файлы проекта основные). [локальный путь]- подставить свой
cd [локальный путь]git\small-projects\autoposting\tg\quotes\data

# Создайте символическую ссылку. [локальный путь]- подставить свой
mklink quotes365.json "[локальный путь]quotes\quotes365.json"
```

### Хранение конфига .env (windows симлинк)
```md   
# Запустите cmd от имени Администратора
# (Win + R → cmd → Ctrl+Shift+Enter)

# Перейдите в папку c git (где файлы проекта основные). [локальный путь]- подставить свой
cd [локальный путь]git\small-projects\autoposting\tg\quotes

# Создайте символическую ссылку. [локальный путь]- подставить свой
mklink .env "[локальный путь]quotes\config\telegram-quotes.env"
```

Имена симлинков на месте будет quotes365.json и .env

---
# Версионность
1. Создаётся ветка fix для фикса, feature для для новой функциональности
```
main (стабильная)
└── dev (разработка) после тестов идёт в main
    ├── feature/*
    └── fix/*
```
## Описание наименовая коммитов 

### Основные типы:

| Тип | Когда использовать |
|-----|-------------------|
| **feat** | Новая функциональность |
| **fix** | Исправление бага |
| **docs** | Изменения в документации |
| **style** | Форматирование, отступы, точки с запятой (не влияет на код) |
| **refactor** | Рефакторинг кода (не фикс и не новая фича) |
| **perf** | Изменения для улучшения производительности |
| **test** | Добавление или исправление тестов |
| **chore** | Обновление задач, настройка (не влияет на код) |
| **build** | Сборка, зависимости |
| **ci** | Настройка CI/CD |

---
### Если нужно подробнее — добавляется тело коммита

```
feat: add password reset functionality

- Add reset password endpoint
- Send email with reset link
- Add validation for token expiration
```

# Указание тэгов

`git tag -a v1.0.0 -m "Release version 1.0.0"`