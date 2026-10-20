FROM python:3.14-slim

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    bash \
    git \
    kubectl \
    wget \
    xz-utils \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q https://get.helm.sh/helm-v3.16.3-linux-amd64.tar.gz -O /tmp/helm.tar.gz \
    && tar xzf /tmp/helm.tar.gz -C /tmp \
    && mv /tmp/linux-amd64/helm /usr/local/bin/helm \
    && rm -rf /tmp/*

ENV PATH=$PATH:/usr/local/bin