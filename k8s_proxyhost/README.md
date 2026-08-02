# 🚀 Kubernetes proxyhost with GitLab CI/CD

Докер-контейнер для управления Kubernetes кластером и выполнения CI/CD задач с GitLab Runner.

## 📋 Содержание

- [Возможности](#-возможности)
- [Требования](#-требования)
- [Быстрый старт](#-быстрый-старт)
- [Настройка](#-настройка)
- [Использование](#-использование)
- [Установленные инструменты](#-установленные-инструменты)
- [GitLab Runner](#-gitlab-runner)
- [Безопасность](#-безопасность)
- [Устранение проблем](#-устранение-проблем)
- [Команды](#-команды)

## ✨ Возможности

- ✅ **Kubernetes управление** через kubectl, helm, k9s
- ✅ **GitLab Runner** с поддержкой shell и docker executors
- ✅ **SSH доступ** к контейнеру для удаленной работы
- ✅ **Docker-in-Docker** поддержка
- ✅ **Готовые алиасы** для kubectl
- ✅ **Легкая настройка** через .env файл
- ✅ **Безопасное хранение** секретов

## 📦 Требования

- Docker (20.10+)
- Docker Compose (2.0+)
- Git
- Доступ к Kubernetes кластеру (для работы)
- GitLab токен (для CI/CD)

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/k8s-jumphost.git
cd k8s-jumphost
```

### 2. Настройка окружения

```bash
# Создать .env из шаблона
cp .env.example .env

# Отредактировать .env (заполнить токены и пути)
nano .env
```

### 3. Добавление SSH ключа

```bash
# Создать папку для ключей
mkdir -p folder_with_sshkey

# Добавить свой публичный ключ
echo "ssh-ed25519 AAAAC3... ваш_публичный_ключ" > folder_with_sshkey/authorized_keys
```

### 4. Добавление Kubernetes конфига

```bash
# Создать папку для конфига
mkdir -p kubeconfig

# Скопировать конфиг кластера
cp ~/.kube/config kubeconfig/config
# Или из другого места
scp user@remote-server:~/.kube/config kubeconfig/config
```

### 5. Запуск контейнера

```bash
# Собрать и запустить
docker compose up -d

# Проверить статус
docker compose ps

# Посмотреть логи
docker compose logs -f
```

### 6. Подключение к контейнеру

```bash
# Через SSH
ssh root@localhost -p 2222

# Или через docker exec
docker exec -it k8s-proxyhost bash
```

## ⚙️ Настройка

### Конфигурация через .env

Создайте файл `.env` на основе `.env.example`:

```bash
# .env
# Общая конфигурация
CONTAINER_NAME=k8s-proxyhost
SSH_PORT=2222
TIMEZONE=Europe/Moscow

# Пути на хосте
SSH_KEYS_PATH=./folder_with_sshkey
KUBECONFIG_PATH=./kubeconfig/config

# GitLab Runner токены
GITLAB_RUNNER_TOKEN_SHELL=glrt-xxxxxxxxxxxx
GITLAB_RUNNER_TOKEN_DOCKER=glrt-yyyyyyyyyyyy
GITLAB_URL=https://gitlab.com

# Ресурсы
CPU_LIMIT=0.8
MEMORY_LIMIT=1G
CPU_RESERVATION=0.2
MEMORY_RESERVATION=256M
```

### Настройка GitLab Runner

**Автоматическая регистрация** (через .env):

```bash
# Просто запустите контейнер с заполненными токенами
docker compose up -d
```

**Ручная регистрация**:

```bash
# Войти в контейнер
docker exec -it k8s-proxyhost bash

# Shell executor
gitlab-runner register \
  --url https://gitlab.com \
  --token glrt-xxxxxxxxxxxx \
  --executor shell

# Docker executor
gitlab-runner register \
  --url https://gitlab.com \
  --token glrt-yyyyyyyyyyyy \
  --executor docker \
  --docker-image alpine:latest
```

## 🛠️ Использование

### Основные команды

```bash
# Kubernetes команды (с алиасами)
k get pods -A
k get nodes
k describe pod my-pod
k logs -f my-pod
k exec -it my-pod -- bash

# Helm
h list
h install nginx stable/nginx
h upgrade nginx ./nginx-chart

# K9s - интерактивный UI
k9s

# GitLab Runner
gitlab-runner list
gitlab-runner status
gitlab-runner run
```

### Алиасы kubectl

| Алиас | Команда |
|-------|---------|
| `k` | `kubectl` |
| `kg` | `kubectl get` |
| `kgp` | `kubectl get pods` |
| `kgd` | `kubectl get deployments` |
| `kgs` | `kubectl get services` |
| `kgn` | `kubectl get nodes` |
| `kd` | `kubectl describe` |
| `kl` | `kubectl logs` |
| `klf` | `kubectl logs -f` |
| `ke` | `kubectl exec -it` |
| `ka` | `kubectl apply -f` |

## 📦 Установленные инструменты

### 🖥️ Базовые утилиты
- `openssh-server` - SSH сервер
- `sudo` - выполнение команд от root
- `curl, wget` - загрузка данных
- `vim, nano` - текстовые редакторы
- `git` - система контроля версий
- `htop` - мониторинг процессов
- `jq, yq` - обработка JSON/YAML
- `bash-completion` - автодополнение

### ☸️ Инструменты Kubernetes
- `kubectl` - основной CLI
- `helm` - менеджер пакетов
- `k9s` - терминальный UI

### 🐳 Docker
- `docker` - для выполнения контейнеров
- `docker-compose` - оркестрация

### 🚀 GitLab Runner
- `gitlab-runner` - для CI/CD
- Поддержка shell и docker executors

## 🔒 Безопасность

### Защита секретов

1. **Никогда не коммитьте .env в Git**
2. Используйте `.env.example` как шаблон
3. SSH ключи храните отдельно
4. Kubeconfig с токенами не коммитьте

### .gitignore

```gitignore
# Секреты
.env
.env.local
.env.*.local

# Конфиги
kubeconfig/
folder_with_sshkey/

# Docker volumes
volumes/
config.toml
*.token
```

### Рекомендации

- Используйте переменные окружения вместо хардкода
- Регулярно обновляйте токены
- Ограничьте доступ к SSH порту фаерволом
- Используйте `:ro` для монтирования конфигов

## 🔧 Устранение проблем

### Контейнер не запускается

```bash
# Проверить логи
docker compose logs

# Проверить наличие файлов
ls -la folder_with_sshkey/
ls -la kubeconfig/

# Пересобрать без кеша
docker compose build --no-cache
```

### Нет доступа к Kubernetes

```bash
# Проверить конфиг
kubectl config view

# Проверить подключение
kubectl cluster-info

# Перезагрузить конфиг
docker compose restart
```

### GitLab Runner не регистрируется

```bash
# Проверить токены в .env
cat .env | grep GITLAB_RUNNER_TOKEN

# Ручная регистрация
docker exec -it k8s-proxyhost bash
gitlab-runner register --url https://gitlab.com --token YOUR_TOKEN
```

### Нет доступа к Docker

```bash
# Проверить права
docker ps

# Если permission denied
sudo chmod 666 /var/run/docker.sock

# Или перезапустить контейнер с privileged
docker compose down
docker compose up -d
```

### SSH не работает

```bash
# Проверить ключи
docker exec k8s-proxyhost cat /root/.ssh/authorized_keys

# Проверить SSH сервер
docker exec k8s-proxyhost ps aux | grep sshd

# Перезапустить SSH
docker exec k8s-proxyhost service ssh restart
```

## 📚 Команды

### Запуск и управление

```bash
# Собрать образ
docker compose build

# Запустить в фоне
docker compose up -d

# Запустить с логами
docker compose up

# Остановить
docker compose stop

# Остановить и удалить
docker compose down

# Остановить и удалить с volumes
docker compose down -v

# Перезапустить
docker compose restart
```

### Вход в контейнер

```bash
# Через SSH
ssh root@localhost -p 2222

# Через docker exec
docker exec -it k8s-proxyhost bash

# С выполнением команды
docker exec k8s-proxyhost kubectl get pods
```

### Очистка

```bash
# Удалить все неиспользуемое
docker system prune -a -f

# Очистить логи
find /var/lib/docker/containers/ -name "*.log" -type f -exec truncate -s 0 {} \;

# Полная очистка
docker compose down -v
docker rmi k8s-jumphost-k8s-bastion
```

### Проверка

```bash
# Статус контейнера
docker compose ps

# Использование ресурсов
docker stats k8s-proxyhost

# Логи
docker compose logs -f

# Проверка сетей
docker network ls

# Проверка volumes
docker volume ls
```

## 📝 Пример .gitlab-ci.yml

```yaml
stages:
  - test
  - deploy

test-k8s:
  stage: test
  tags:
    - shell
    - k8s
  script:
    - kubectl get pods -A
    - helm list
    - docker ps

deploy-app:
  stage: deploy
  tags:
    - shell
    - k8s
  script:
    - kubectl apply -f manifests/
    - kubectl rollout status deployment/my-app
  only:
    - main
```