# Telegram Quotes Bot

Бот для автоматической публикации цитат в Telegram канал.
Секреты в менеджере паролей
Конфиги синхронизируйте через облако или локально через симлинк
data
├── quotes356.json
└── published_history.json
quotes
└── .env

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
# Запуск
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
BOT_TOKEN - токен бота от @BotFather
CHANNEL_ID - ID канала (начинается с @)
BASE_HOUR - час публикации (по умолчанию 9)
BASE_MINUTE - минута публикации (по умолчанию 0)
RANDOM_RANGE_MINUTES - случайное смещение в минутах (по умолчанию ±30)
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
## 1. Инициализируйте git:
```bash
cd autoposting
git init
echo "# Autoposting Project" > README.md
cp telegram/quotes/.env.example .env.example  # Копируем шаблон
```
## 3. Создайте реальный .env файл:
```bash
cd telegram/quotes
cp .env.example .env
# Отредактируйте .env своими секретами
```
## 4. Добавьте в git
```bash
git add .
git commit -m "Initial commit: Telegram quotes bot with proper structure"
```

## 5. Хранение персоналифицированной информации. 
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
main (стабильная)
└── dev (разработка) после тестов идёт в main
    ├── feature/*
    └── fix/*