FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV KUBECONFIG=/root/.kube/config

# Настройка времени
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ============================================
# БАЗОВЫЕ УТИЛИТЫ (минимальный набор)
# ============================================
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    jq \
    bash-completion \
    ca-certificates \
    gnupg \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# УСТАНОВКА kubectl
# ============================================
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# ============================================
# УСТАНОВКА helm
# ============================================
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh \
    && rm get_helm.sh

# ============================================
# УСТАНОВКА k9s (оставляем!)
# ============================================
RUN curl -LO https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_amd64.tar.gz \
    && tar -xvf k9s_Linux_amd64.tar.gz \
    && chmod +x k9s \
    && mv k9s /usr/local/bin/ \
    && rm k9s_Linux_amd64.tar.gz

# ============================================
# УСТАНОВКА yq (для работы с YAML)
# ============================================
RUN wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \
    && chmod +x /usr/local/bin/yq

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
# АЛИАСЫ И АВТОДОПОЛНЕНИЕ
# ============================================
RUN echo "source <(kubectl completion bash)" >> ~/.bashrc \
    && echo "source /usr/share/bash-completion/bash_completion" >> ~/.bashrc \
    && echo "alias k='kubectl'" >> ~/.bashrc \
    && echo "alias kg='kubectl get'" >> ~/.bashrc \
    && echo "alias kgp='kubectl get pods'" >> ~/.bashrc \
    && echo "alias kgd='kubectl get deployments'" >> ~/.bashrc \
    && echo "alias kgs='kubectl get services'" >> ~/.bashrc \
    && echo "alias kgn='kubectl get nodes'" >> ~/.bashrc \
    && echo "alias kd='kubectl describe'" >> ~/.bashrc \
    && echo "alias kl='kubectl logs'" >> ~/.bashrc \
    && echo "alias klf='kubectl logs -f'" >> ~/.bashrc \
    && echo "alias ke='kubectl exec -it'" >> ~/.bashrc \
    && echo "alias ka='kubectl apply -f'" >> ~/.bashrc \
    && echo "alias kdel='kubectl delete'" >> ~/.bashrc \
    && echo "alias kctx='kubectl config current-context'" >> ~/.bashrc \
    && echo "alias kns='kubectl config set-context --current --namespace'" >> ~/.bashrc \
    && echo "alias h='helm'" >> ~/.bashrc \
    && echo "export KUBE_EDITOR=vim" >> ~/.bashrc

# Создание директории для конфигов
RUN mkdir -p /root/.kube

# Копирование entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]
