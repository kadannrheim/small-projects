FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV KUBECONFIG=/root/.kube/config

# Настройка времени
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ============================================
# МИНИМАЛЬНЫЙ НАБОР (только необходимое)
# ============================================
RUN apt-get update && apt-get install -y \
    openssh-server \
    curl \
    wget \
    git \
    vim \
    nano \
    bash-completion \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# kubectl
# ============================================
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# ============================================
# k9s (опционально, для удобства)
# ============================================
RUN curl -LO https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_amd64.tar.gz \
    && tar -xvf k9s_Linux_amd64.tar.gz \
    && chmod +x k9s \
    && mv k9s /usr/local/bin/ \
    && rm k9s_Linux_amd64.tar.gz

# ============================================
# HELM (опционально)
# ============================================
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh \
    && rm get_helm.sh

# ============================================
# GITLAB RUNNER (только shell executor!)
# ============================================
# Самый легкий способ - прямой бинарник
RUN curl -L "https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64" -o /usr/local/bin/gitlab-runner \
    && chmod +x /usr/local/bin/gitlab-runner

# Создаем пользователя для runner
RUN useradd -r -s /bin/bash gitlab-runner \
    && mkdir -p /home/gitlab-runner/.gitlab-runner \
    && chown -R gitlab-runner:gitlab-runner /home/gitlab-runner \
    && mkdir -p /etc/gitlab-runner

# ============================================
# НАСТРОЙКА SSH
# ============================================
RUN mkdir /var/run/sshd \
    && echo 'root:root' | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && mkdir -p /root/.ssh \
    && chmod 700 /root/.ssh

# ============================================
# АЛИАСЫ
# ============================================
RUN echo "source <(kubectl completion bash)" >> ~/.bashrc \
    && echo "alias k='kubectl'" >> ~/.bashrc \
    && echo "alias kg='kubectl get'" >> ~/.bashrc \
    && echo "alias kgp='kubectl get pods'" >> ~/.bashrc \
    && echo "alias kgd='kubectl get deployments'" >> ~/.bashrc \
    && echo "alias kgs='kubectl get services'" >> ~/.bashrc \
    && echo "alias kgn='kubectl get nodes'" >> ~/.bashrc \
    && echo "alias kd='kubectl describe'" >> ~/.bashrc \
    && echo "alias kl='kubectl logs'" >> ~/.bashrc \
    && echo "alias ke='kubectl exec -it'" >> ~/.bashrc \
    && echo "alias ka='kubectl apply -f'" >> ~/.bashrc \
    && echo "export KUBE_EDITOR=vim" >> ~/.bashrc

RUN mkdir -p /root/.kube

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]