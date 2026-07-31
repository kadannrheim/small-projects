#!/bin/bash

# Создание директории для SSH ключей
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

# Проверка конфига Kubernetes
if [ -f /root/.kube/config ]; then
    echo "✅ Kubernetes config found at /root/.kube/config"
    echo ""
    echo "📋 Cluster info:"
    kubectl cluster-info 2>/dev/null || echo "⚠️  Unable to connect to cluster"
else
    echo "⚠️  Kubernetes config not found at /root/.kube/config"
fi

# Вывод установленных инструментов
echo ""
echo "🛠️  Available tools:"
echo "   - kubectl: $(kubectl version --client --short 2>/dev/null || echo 'not found')"
echo "   - helm: $(helm version --short 2>/dev/null || echo 'not found')"
echo "   - k9s: $(k9s version 2>/dev/null | head -1 || echo 'not found')"
echo "   - yq: $(yq --version 2>/dev/null || echo 'not found')"
echo "   - jq: $(jq --version 2>/dev/null || echo 'not found')"

# Запуск SSH
echo ""
echo "🚀 Starting SSH server on port 22..."
echo "   Connect with: ssh root@localhost -p ${SSH_PORT:-2222}"
echo "   После подключения используйте:"
echo "   - k9s  - для интерактивного управления кластером"
echo "   - kubectl (или k) - для управления кластером"
echo ""

/usr/sbin/sshd -D
