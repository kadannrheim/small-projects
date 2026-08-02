#!/bin/bash

echo "=== Starting K8s Proxyhost ==="

# ============================================
# SSH
# ============================================
mkdir -p /root/.ssh
chmod 700 /root/.ssh

if [ -f /config/authorized_keys ]; then
    cp /config/authorized_keys /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
    echo "✅ Public keys loaded"
fi

# Генерация ключей хоста
ssh-keygen -A 2>/dev/null || true

# SSH конфиг
cat > /etc/ssh/sshd_config << 'SSHCONF'
Port 22
PermitRootLogin yes
PubkeyAuthentication yes
PasswordAuthentication yes
UsePAM yes
Subsystem sftp /usr/lib/openssh/sftp-server
SSHCONF

pkill sshd 2>/dev/null || true

# ============================================
# GITLAB RUNNER (только shell executor)
# ============================================
if [ ! -f /etc/gitlab-runner/config.toml ] && [ ! -z "$GITLAB_RUNNER_TOKEN_SHELL" ]; then
    echo "Registering GitLab Runner (shell executor)..."
    
    gitlab-runner register \
        --non-interactive \
        --url ${GITLAB_URL:-https://gitlab.com} \
        --token $GITLAB_RUNNER_TOKEN_SHELL \
        --executor shell \
        --description "Shell Runner" \
        --tag-list "shell,linux" \
        --run-untagged="true"
    
    echo "✅ Runner registered!"
fi

# Запуск runner
if [ -f /etc/gitlab-runner/config.toml ]; then
    echo "Starting GitLab Runner..."
    gitlab-runner run &
fi

# ============================================
# ИНФОРМАЦИЯ
# ============================================
echo ""
echo "🛠️  Tools:"
echo "   - kubectl: $(kubectl version --client --short 2>/dev/null)"
echo "   - helm: $(helm version --short 2>/dev/null)"
echo "   - k9s: $(k9s version 2>/dev/null | head -1)"
echo "   - gitlab-runner: $(gitlab-runner --version 2>/dev/null)"

# ============================================
# SSH
# ============================================
echo ""
echo "🚀 Starting SSH..."
echo "   ssh root@localhost -p ${SSH_PORT:-2222}"
echo ""

/usr/sbin/sshd -D