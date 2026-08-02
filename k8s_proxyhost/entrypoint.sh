#!/bin/bash

# Создание директории для SSH ключей
mkdir -p /root/.ssh
chmod 700 /root/.ssh

# Копирование публичных ключей
if [ -f /config/authorized_keys ]; then
    cp /config/authorized_keys /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
    echo "✅ Public keys loaded"
fi

# Проверка конфига Kubernetes
if [ -f /root/.kube/config ]; then
    echo "✅ Kubernetes config found"
    kubectl cluster-info 2>/dev/null || echo "⚠️  Unable to connect to cluster"
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
          --run-untagged="true"
        echo "✅ SHELL runner registered!"
    fi
    
    # DOCKER runner
    if [ ! -z "$GITLAB_RUNNER_TOKEN_DOCKER" ]; then
        echo "Registering DOCKER runner..."
        gitlab-runner register \
          --non-interactive \
          --url ${GITLAB_URL:-https://gitlab.com} \
          --token $GITLAB_RUNNER_TOKEN_DOCKER \
          --executor docker \
          --description "Docker Runner" \
          --tag-list "docker,k8s" \
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

# Вывод информации
echo ""
echo "🛠️  Available tools:"
echo "   - kubectl: $(kubectl version --client --short 2>/dev/null || echo 'not found')"
echo "   - helm: $(helm version --short 2>/dev/null || echo 'not found')"
echo "   - k9s: $(k9s version 2>/dev/null | head -1 || echo 'not found')"
echo "   - docker: $(docker --version 2>/dev/null || echo 'not found')"
echo "   - gitlab-runner: $(gitlab-runner --version 2>/dev/null || echo 'not found')"

# Запуск SSH
echo ""
echo "🚀 Starting SSH server on port 22..."
echo "   Connect with: ssh root@localhost -p ${SSH_PORT:-2222}"
echo "   После подключения используйте:"
echo "   - k9s  - для интерактивного управления кластером"
echo "   - kubectl (или k) - для управления кластером"
echo ""

/usr/sbin/sshd -D