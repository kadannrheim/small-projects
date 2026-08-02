#!/bin/bash

echo "=== Starting K8s Proxyhost ==="

# ============================================
# НАСТРОЙКА SSH
# ============================================
echo "🔧 Configuring SSH..."

# Создание .ssh директории
mkdir -p /root/.ssh
chmod 700 /root/.ssh

# Копирование публичных ключей
if [ -f /config/authorized_keys ]; then
    cp /config/authorized_keys /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
    echo "✅ Public keys loaded from /config/authorized_keys"
else
    echo "⚠️  No authorized_keys found in /config/"
fi

# Генерация ключей хоста (если нет)
ssh-keygen -A 2>/dev/null || true

# Правильный SSH конфиг
cat > /etc/ssh/sshd_config << 'SSHCONF'
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
PermitRootLogin yes
PubkeyAuthentication yes
PasswordAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server
Banner none
SSHCONF

# Убить старый SSH если есть
pkill sshd 2>/dev/null || true
sleep 1

# ============================================
# ПРОВЕРКА KUBERNETES
# ============================================
if [ -f /root/.kube/config ]; then
    echo "✅ Kubernetes config found"
    kubectl cluster-info 2>/dev/null || echo "⚠️  Unable to connect to cluster"
else
    echo "⚠️  Kubernetes config not found"
fi

# ============================================
# АВТОМАТИЧЕСКАЯ РЕГИСТРАЦИЯ GITLAB RUNNER
# ============================================
if [ ! -f /etc/gitlab-runner/config.toml ]; then
    echo ""
    echo "🔄 Configuring GitLab Runners..."
    
    # SHELL runner
    if [ ! -z "$GITLAB_RUNNER_TOKEN_SHELL" ]; then
        echo "Registering SHELL runner..."
        gitlab-runner register \
          --non-interactive \
          --url ${GITLAB_URL:-https://gitlab.com} \
          --token $GITLAB_RUNNER_TOKEN_SHELL \
          --executor shell \
          --description "Shell Runner" \
          --tag-list "shell,k8s" \
          --run-untagged="true" \
          --locked="false"
        echo "✅ SHELL runner registered!"
    fi
    
    # DOCKER runner (опционально, только если есть Docker)
    if [ ! -z "$GITLAB_RUNNER_TOKEN_DOCKER" ] && [ -x "$(command -v docker)" ]; then
        echo "Registering DOCKER runner..."
        gitlab-runner register \
          --non-interactive \
          --url ${GITLAB_URL:-https://gitlab.com} \
          --token $GITLAB_RUNNER_TOKEN_DOCKER \
          --executor docker \
          --description "Docker Runner" \
          --tag-list "docker,k8s" \
          --run-untagged="true" \
          --locked="false" \
          --docker-image alpine:latest \
          --docker-privileged \
          --docker-volumes /var/run/docker.sock:/var/run/docker.sock
        echo "✅ DOCKER runner registered!"
    fi
fi

# Запуск GitLab Runner
if [ -f /etc/gitlab-runner/config.toml ]; then
    echo ""
    echo "🔄 Starting GitLab Runner..."
    gitlab-runner run &
fi

# ============================================
# ВЫВОД ИНФОРМАЦИИ
# ============================================
echo ""
echo "🛠️  Available tools:"
echo "   - kubectl: $(kubectl version --client --short 2>/dev/null || echo 'not found')"
echo "   - helm: $(helm version --short 2>/dev/null || echo 'not found')"
echo "   - k9s: $(k9s version 2>/dev/null | head -1 || echo 'not found')"
echo "   - yq: $(yq --version 2>/dev/null || echo 'not found')"
echo "   - gitlab-runner: $(gitlab-runner --version 2>/dev/null | head -1 || echo 'not found')"
echo ""
echo "📦 kubectl aliases:"
echo "   k, kg, kgp, kgd, kgs, kgn, kd, kl, klf, ke, ka, kdel"
echo "   kctx - show current context"
echo "   kns <namespace> - switch namespace"
echo ""

# ============================================
# ЗАПУСК SSH
# ============================================
echo "🚀 Starting SSH server on port 22..."
echo "   Connect with: ssh root@localhost -p ${SSH_PORT:-2222}"
echo "   Password: root (if key doesn't work)"
echo ""

/usr/sbin/sshd -D -e