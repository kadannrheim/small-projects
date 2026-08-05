#!/bin/bash
# Точка входа контейнера: SSH + регистрация/запуск GitLab Runner (shell)
set -euo pipefail

echo "=== Starting K8s Proxyhost ==="

GITLAB_URL="${GITLAB_URL:-https://gitlab.com}"
CONFIG_FILE="${GITLAB_RUNNER_CONFIG:-/etc/gitlab-runner/config.toml}"
RUNNER_NAME="${GITLAB_RUNNER_NAME:-shell-on-k8s-proxyhost}"
SSH_PORT_HINT="${SSH_PORT:-2222}"

# --------------------------------------------
# SSH: только ключи, без паролей в образе
# --------------------------------------------
mkdir -p /root/.ssh
chmod 700 /root/.ssh

if [ -f /config/authorized_keys ]; then
  cp /config/authorized_keys /root/.ssh/authorized_keys
  chmod 600 /root/.ssh/authorized_keys
  echo "[ok] SSH authorized_keys loaded"
else
  echo "[warn] /config/authorized_keys не найден — вход по SSH не сработает, пока не смонтируете ключи"
fi

# Host keys для sshd (если ещё не сгенерированы)
ssh-keygen -A >/dev/null 2>&1 || true

cat > /etc/ssh/sshd_config << 'SSHCONF'
Port 22
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no
X11Forwarding no
PrintMotd no
Subsystem sftp /usr/lib/openssh/sftp-server
SSHCONF

# --------------------------------------------
# Вспомогательные функции
# --------------------------------------------

# Есть ли уже зарегистрированный runner в config.toml
config_has_runners() {
  [ -f "$CONFIG_FILE" ] && grep -q '\[\[runners\]\]' "$CONFIG_FILE" 2>/dev/null
}

# Регистрация shell-runner по authentication token (glrt-...)
register_shell_runner() {
  local token="$1"
  echo "Registering GitLab Runner (shell executor)..."
  echo "  URL:   $GITLAB_URL"
  echo "  Name:  $RUNNER_NAME"
  echo "  Token: ${token:0:5}… (len=${#token})"

  # Для токенов glrt-* теги / locked / run-untagged задаются ТОЛЬКО в UI GitLab.
  # Флаги --tag-list / --run-untagged / --locked ломают register с ошибкой:
  #   "Runner configuration other than name and executor configuration is reserved"
  if [[ "$token" != glrt-* ]]; then
    echo "[error] Нужен authentication token (glrt-...), получен другой префикс."
    echo "        GitLab UI: Create runner → Shell → скопируйте authentication token."
    return 1
  fi

  # Сбрасываем устаревшие REGISTER_*, чтобы они не подмешали запрещённые опции
  unset REGISTER_LOCKED REGISTER_RUN_UNTAGGED REGISTER_TAG_LIST \
        REGISTER_ACCESS_LEVEL REGISTER_MAXIMUM_TIMEOUT REGISTER_PAUSED \
        REGISTER_MAINTENANCE_NOTE 2>/dev/null || true

  if ! gitlab-runner register \
      --non-interactive \
      --config "$CONFIG_FILE" \
      --url "$GITLAB_URL" \
      --token "$token" \
      --executor "shell" \
      --description "$RUNNER_NAME"; then
    echo "[error] gitlab-runner register не удался — проверьте GITLAB_URL и GITLAB_RUNNER_TOKEN_SHELL"
    echo "        Удалите «Never contacted» runners в UI и создайте свежий shell-токен."
    echo "        Токены одноразовые: если уже использовали — нужен новый runner."
    return 1
  fi

  if ! config_has_runners; then
    echo "[error] Регистрация завершилась, но в $CONFIG_FILE нет секции [[runners]]"
    return 1
  fi

  # Облегчаем runner: один job за раз, разумный интервал опроса
  sed -i 's/^concurrent = .*/concurrent = 1/' "$CONFIG_FILE" 2>/dev/null || true
  if ! grep -q '^check_interval' "$CONFIG_FILE"; then
    sed -i '1a check_interval = 3' "$CONFIG_FILE" 2>/dev/null || true
  fi

  echo "[ok] Runner registered → $CONFIG_FILE"
}

# --------------------------------------------
# GitLab Runner: регистрация или использование существующего конфига
# --------------------------------------------
mkdir -p "$(dirname "$CONFIG_FILE")"

# FORCE_REREGISTER=true в .env — один раз сбросить volume-конфиг и зарегистрироваться заново
if [ "${FORCE_REREGISTER:-false}" = "true" ] && [ -f "$CONFIG_FILE" ]; then
  echo "[warn] FORCE_REREGISTER=true — удаляю старый $CONFIG_FILE"
  rm -f "$CONFIG_FILE"
fi

TOKEN_SHELL="${GITLAB_RUNNER_TOKEN_SHELL:-}"

if config_has_runners; then
  echo "[ok] Найден существующий конфиг runner — пропускаю register"
elif [ -n "$TOKEN_SHELL" ]; then
  if ! register_shell_runner "$TOKEN_SHELL"; then
    echo "[error] Регистрация не удалась — поднимаю только SSH (без gitlab-runner)"
  fi
else
  echo "[warn] GITLAB_RUNNER_TOKEN_SHELL пуст — runner НЕ зарегистрируется и не свяжется с GitLab"
  echo "       Укажите в .env свежий shell-токен (glrt-...)."
fi

if [ -n "${GITLAB_RUNNER_TOKEN_DOCKER:-}" ]; then
  echo "[warn] GITLAB_RUNNER_TOKEN_DOCKER задан, но docker executor в этом образе не поддерживается."
  echo "       Удалите docker-runner в UI GitLab; оставьте только Shell-токен."
fi

# --------------------------------------------
# Запуск процессов (без busy-loop в фоне)
# --------------------------------------------
echo ""
echo "Tools (client-only, no API calls):"
echo "  kubectl: $(kubectl version --client -o yaml 2>/dev/null | awk '/gitVersion:/{print $2; exit}')"
command -v helm >/dev/null 2>&1 && echo "  helm:    $(helm version --short 2>/dev/null || echo present)"
command -v k9s >/dev/null 2>&1 && echo "  k9s:     present"
echo "  runner:  $(gitlab-runner --version 2>/dev/null | head -1)"

echo ""
echo "SSH: root@localhost -p ${SSH_PORT_HINT} (только ключ)"

if config_has_runners; then
  # sshd в фоне, gitlab-runner — главный процесс (tini = PID 1)
  /usr/sbin/sshd
  echo "[ok] sshd started; starting gitlab-runner..."
  exec gitlab-runner run --config "$CONFIG_FILE" --working-directory /home/gitlab-runner
fi

echo "[warn] Нет конфига runner — контейнер работает только с sshd"
exec /usr/sbin/sshd -D
