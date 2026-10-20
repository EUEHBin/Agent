FROM python:3.14-slim

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv -i https://mirrors.aliyun.com/pypi/simple/
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

