# Kubernetes proxyhost + GitLab Runner (shell)

Docker-контейнер: SSH-доступ к kubectl/helm/k9s и **shell** GitLab Runner.

> Docker / DinD executor **не поддерживается**. В GitLab создавайте runner с executor **Shell**.

## Быстрый старт

```bash
cp .env.example .env
# Заполните GITLAB_URL и GITLAB_RUNNER_TOKEN_SHELL (токен glrt-... от Shell runner)

mkdir -p folder_with_sshkey kubeconfig scripts manifests
# Публичный SSH-ключ:
#   echo "ssh-ed25519 AAAA..." > folder_with_sshkey/authorized_keys
# Kubeconfig:
#   cp ~/.kube/config kubeconfig/config

docker compose down
docker compose build --no-cache
docker compose up -d
docker compose logs -f
```

Подключение: `ssh root@localhost -p 2222` (только по ключу, пароля нет).

## GitLab Runner

1. В GitLab: **Settings → CI/CD → Runners → New project/instance runner**
2. Executor: **Shell**, теги например `shell,linux`
3. Скопируйте authentication token (`glrt-...`) в `.env` → `GITLAB_RUNNER_TOKEN_SHELL`
4. Старые runners со статусом **Never contacted** удалите в UI — их токены уже бесполезны
5. Если контейнер уже поднимался со старым томом:

```bash
# Один раз перерегистрировать:
# в .env: FORCE_REREGISTER=true
docker compose up -d
# затем FORCE_REREGISTER=false

# Или снести volume целиком:
docker compose down
docker volume rm k8s_proxyhost_gitlab-runner-config 2>/dev/null || docker volume ls | grep gitlab
docker compose up -d
```

Проверка:

```bash
docker compose logs | grep -i runner
docker exec k8s-proxyhost gitlab-runner verify
docker exec k8s-proxyhost gitlab-runner list
```

## Переменные (.env)

См. `.env.example`. Обязательные для runner:

| Переменная | Назначение |
|---|---|
| `GITLAB_URL` | URL GitLab (`https://gitlab.com` или self-hosted) |
| `GITLAB_RUNNER_TOKEN_SHELL` | Токен shell-runner (`glrt-...`) |
| `SSH_KEYS_PATH` | Папка с `authorized_keys` |
| `KUBECONFIG_PATH` | Файл kubeconfig |
| `FORCE_REREGISTER` | `true` один раз, чтобы перезаписать `config.toml` |
| `INSTALL_K9S` / `INSTALL_HELM` | `false` — ещё легче образ |

## Ресурсы / CPU

Лимиты по умолчанию: `CPU_LIMIT=0.5`, `MEMORY_LIMIT=512m`. Runner: `concurrent = 1`.

Если CPU снова высокий: `docker stats k8s-proxyhost` и `docker compose logs` — не должно быть бесконечных retry register.

## Устранение проблем

**Runner Never contacted / `verify` без runners** — чаще всего:
1. Регистрация с `glrt-` падала из‑за флагов `--tag-list` / `--locked` (исправлено в `entrypoint.sh`)
2. Пустой/старый токен, неверный `GITLAB_URL`, или битый volume
3. В `.env` всё ещё задан `GITLAB_RUNNER_TOKEN_DOCKER` — удалите docker-runner в UI и очистите переменную

Удалите runners **Never contacted** в GitLab → создайте новый **Shell** runner → свежий `glrt-...` в `.env` → `FORCE_REREGISTER=true` → `docker compose up -d --build` → снова `FORCE_REREGISTER=false`.

Успех в логах: `[ok] Runner registered` и `[ok] sshd started; starting gitlab-runner...`.

**SSH denied** — проверьте `folder_with_sshkey/authorized_keys` и порт `SSH_PORT`.

**Нет kubectl к кластеру** — проверьте `kubeconfig/config` на хосте.
