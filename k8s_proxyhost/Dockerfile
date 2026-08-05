# Образ jump/proxy host: SSH + kubectl/helm/k9s + GitLab Runner (только shell executor)
FROM ubuntu:22.04

# Версии инструментов (пины — стабильная сборка, без «latest»)
ARG KUBECTL_VERSION=v1.30.4
ARG HELM_VERSION=v3.15.4
ARG K9S_VERSION=v0.32.5
ARG GITLAB_RUNNER_VERSION=v17.3.1
# Тяжёлые опциональные бинарники можно отключить через .env / build.args
ARG INSTALL_K9S=true
ARG INSTALL_HELM=true

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    KUBECONFIG=/root/.kube/config \
    GITLAB_RUNNER_CONFIG=/etc/gitlab-runner/config.toml

# Минимальный набор пакетов. Пароли в образ НЕ кладём — только SSH по ключу.
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server \
        curl \
        ca-certificates \
        git \
        bash-completion \
        jq \
        procps \
        tini \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/run/sshd /root/.ssh /root/.kube /etc/gitlab-runner \
    && chmod 700 /root/.ssh \
    && ssh-keygen -A

# kubectl — CLI для Kubernetes (зафиксированная версия)
RUN curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl

# helm — менеджер пакетов K8s (опционально)
RUN if [ "$INSTALL_HELM" = "true" ]; then \
      curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" -o /tmp/helm.tgz \
      && tar -xzf /tmp/helm.tgz -C /tmp \
      && mv /tmp/linux-amd64/helm /usr/local/bin/helm \
      && rm -rf /tmp/helm.tgz /tmp/linux-amd64; \
    fi

# k9s — TUI для кластера (опционально, самый тяжёлый бинарник)
RUN if [ "$INSTALL_K9S" = "true" ]; then \
      curl -fsSL "https://github.com/derailed/k9s/releases/download/${K9S_VERSION}/k9s_Linux_amd64.tar.gz" -o /tmp/k9s.tgz \
      && tar -xzf /tmp/k9s.tgz -C /tmp k9s \
      && mv /tmp/k9s /usr/local/bin/k9s \
      && rm -f /tmp/k9s.tgz; \
    fi

# GitLab Runner — только shell executor (Docker в образе нет)
RUN curl -fsSL "https://gitlab-runner-downloads.s3.amazonaws.com/${GITLAB_RUNNER_VERSION}/binaries/gitlab-runner-linux-amd64" \
      -o /usr/local/bin/gitlab-runner \
    && chmod +x /usr/local/bin/gitlab-runner \
    && useradd --system --create-home --shell /bin/bash gitlab-runner \
    && mkdir -p /home/gitlab-runner \
    && chown -R gitlab-runner:gitlab-runner /home/gitlab-runner

# Удобные алиасы kubectl (без сетевых вызовов на этапе сборки)
RUN printf '%s\n' \
      'source <(kubectl completion bash 2>/dev/null || true)' \
      "alias k='kubectl'" \
      "alias kg='kubectl get'" \
      "alias kgp='kubectl get pods'" \
      "alias kgd='kubectl get deployments'" \
      "alias kgs='kubectl get services'" \
      "alias kgn='kubectl get nodes'" \
      "alias kd='kubectl describe'" \
      "alias kl='kubectl logs'" \
      "alias ke='kubectl exec -it'" \
      "alias ka='kubectl apply -f'" \
      'export KUBE_EDITOR=vi' \
      >> /root/.bashrc

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

# tini = PID 1: убирает зомби-процессы и «зависшие» фоновые циклы runner
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
