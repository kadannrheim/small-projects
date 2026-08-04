```markdown
# Amnezia WG Easy

Docker-контейнер для AmneziaWG с веб-интерфейсом.

## Быстрый старт

### 1. Настройка окружения

Скопируйте файл примера и настройте переменные:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл, указав свои значения.

### 2. Генерация хеша пароля

```bash
echo "ваш_пароль" | shasum -a 256 | cut -d ' ' -f1
```

Скопируйте полученный хеш и вставьте его в `.env` как значение `PASSWORD_HASH`.

### 3. Запуск

```bash
docker-compose up -d
```

### 4. Доступ к веб-интерфейсу

Откройте браузер и перейдите по адресу:

```
http://ваш-сервер:ПОРТ
```

## Переменные окружения

### Обязательные

| Переменная | Описание |
|------------|----------|
| `PASSWORD_HASH` | Хеш пароля для входа в веб-интерфейс |
| `WG_PORT` | Порт WireGuard (UDP) |
| `PORT` | Порт веб-интерфейса (TCP) |

### Опциональные

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `WG_HOST` | Внешний IP или домен | - |
| `WG_SUBNET` | Подсеть WireGuard | `10.8.0.0/24` |
| `WG_ALLOWED_IPS` | Разрешенные IP | `0.0.0.0/0` |
| `WG_DNS` | DNS-сервер | `1.1.1.1` |
| `WG_PERSISTENT_KEEPALIVE` | Keepalive (сек) | `25` |
| `WG_MTU` | Размер MTU | `1420` |
| `TZ` | Часовой пояс | `UTC` |

## Команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Логи
docker-compose logs -f

# Статус
docker-compose ps
```

## Безопасность

1. Измените пароль по умолчанию
2. Используйте HTTPS (настройте reverse proxy)
3. Настройте брандмауэр для ограничения доступа
4. Храните `.env` в безопасности (не добавляйте в Git)

## Устранение неполадок

```bash
# Проверить логи
docker-compose logs

# Проверить наличие .env
ls -la .env

# Проверить переменные
docker-compose exec amnezia-wg-easy env | grep -E "PASSWORD_HASH|WG_PORT|PORT"
```
```

## `.env.example`:

```env
# Обязательные переменные
PASSWORD_HASH=your_password_hash_here
WG_PORT=ПОРТ
PORT=ПОРТ

# Опциональные переменные
# WG_HOST=your-domain.com
# WG_SUBNET=10.8.0.0/24
# WG_ALLOWED_IPS=0.0.0.0/0
# WG_DNS=1.1.1.1
# WG_PERSISTENT_KEEPALIVE=25
# WG_MTU=1420
# TZ=UTC
```