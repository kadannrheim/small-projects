#!/bin/bash
set -euo pipefail

echo "=== Starting K8s Proxyhost ==="

GITLAB_URL="${GITLAB_URL:-https://gitlab.com}"
CONFIG_FILE="${GITLAB_RUNNER_CONFIG:-/etc/gitlab-runner/config.toml}"
RUNNER_NAME="${GITLAB_RUNNER_NAME:-shell-on-k8s-proxyhost}"
SSH_PORT_HINT="${SSH_PORT:-2222}"

# --------------------------------------------
# SSH (key-only — no hardcoded passwords)
# --------------------------------------------
mkdir -p /root/.ssh
chmod 700 /root/.ssh

if [ -f /config/authorized_keys ]; then
  cp /config/authorized_keys /root/.ssh/authorized_keys
  chmod 600 /root/.ssh/authorized_keys
  echo "[ok] SSH authorized_keys loaded"
else
  echo "[warn] /config/authorized_keys not found — SSH key login will fail until you mount it"
fi

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
# Helpers
# --------------------------------------------
config_has_runners() {
  [ -f "$CONFIG_FILE" ] && grep -q '\[\[runners\]\]' "$CONFIG_FILE" 2>/dev/null
}

register_shell_runner() {
  local token="$1"
  echo "Registering GitLab Runner (shell executor)..."
  echo "  URL:   $GITLAB_URL"
  echo "  Name:  $RUNNER_NAME"

  # Authentication token (glrt-*) — tags/description are primarily set in GitLab UI.
  if ! gitlab-runner register \
      --non-interactive \
      --url "$GITLAB_URL" \
      --token "$token" \
      --executor "shell" \
      --description "$RUNNER_NAME" \
      --name "$RUNNER_NAME" \
      --tag-list "${GITLAB_RUNNER_TAGS:-shell,linux}" \
      --run-untagged="${GITLAB_RUNNER_RUN_UNTAGGED:-true}" \
      --locked="${GITLAB_RUNNER_LOCKED:-false}"; then
    echo "[error] gitlab-runner register failed — check GITLAB_URL and GITLAB_RUNNER_TOKEN_SHELL"
    echo "        Delete stale 'Never contacted' runners in GitLab UI and create a fresh shell runner token."
    return 1
  fi

  if ! config_has_runners; then
    echo "[error] Registration finished but $CONFIG_FILE has no [[runners]] section"
    return 1
  fi

  # Keep runner light: one job at a time, sane poll interval
  sed -i 's/^concurrent = .*/concurrent = 1/' "$CONFIG_FILE" 2>/dev/null || true
  if ! grep -q '^check_interval' "$CONFIG_FILE"; then
    sed -i '1a check_interval = 3' "$CONFIG_FILE" 2>/dev/null || true
  fi

  echo "[ok] Runner registered → $CONFIG_FILE"
}

# --------------------------------------------
# GitLab Runner
# --------------------------------------------
if [ "${FORCE_REREGISTER:-false}" = "true" ] && [ -f "$CONFIG_FILE" ]; then
  echo "[warn] FORCE_REREGISTER=true — removing old $CONFIG_FILE"
  rm -f "$CONFIG_FILE"
fi

TOKEN_SHELL="${GITLAB_RUNNER_TOKEN_SHELL:-}"

if config_has_runners; then
  echo "[ok] Existing runner config found — skipping register"
elif [ -n "$TOKEN_SHELL" ]; then
  register_shell_runner "$TOKEN_SHELL" || true
else
  echo "[warn] GITLAB_RUNNER_TOKEN_SHELL is empty — runner will NOT register or contact GitLab"
  echo "       Set it in .env to a fresh shell-executor runner token (glrt-...)."
fi

if [ -n "${GITLAB_RUNNER_TOKEN_DOCKER:-}" ]; then
  echo "[warn] GITLAB_RUNNER_TOKEN_DOCKER is set but docker executor is not enabled in this image."
  echo "       Use a shell runner token only, or delete the unused docker runner in GitLab UI."
fi

# --------------------------------------------
# Start processes (no busy-restart loops)
# --------------------------------------------
echo ""
echo "Tools (client-only, no API calls):"
echo "  kubectl: $(kubectl version --client -o yaml 2>/dev/null | awk '/gitVersion:/{print $2; exit}')"
command -v helm >/dev/null 2>&1 && echo "  helm:    $(helm version --short 2>/dev/null || echo present)"
command -v k9s >/dev/null 2>&1 && echo "  k9s:     present"
echo "  runner:  $(gitlab-runner --version 2>/dev/null | head -1)"

echo ""
echo "SSH: root@localhost -p ${SSH_PORT_HINT} (key auth only)"

if config_has_runners; then
  # Daemonize sshd, keep gitlab-runner in foreground (tini = PID 1)
  /usr/sbin/sshd
  echo "[ok] sshd started; starting gitlab-runner..."
  exec gitlab-runner run --config "$CONFIG_FILE" --working-directory /home/gitlab-runner
fi

echo "[warn] No runner config — container stays up with sshd only"
exec /usr/sbin/sshd -D
