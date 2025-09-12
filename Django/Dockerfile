FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /workspace

# システム依存のインストール
RUN apt-get update && apt-get install -y \
    build-essential git \
    libxrender1 libxext6 libsm6 \
 && rm -rf /var/lib/apt/lists/*
 
RUN mkdir /code
ENV PYTHONUNBUFFERED 1
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -U pip && \
    pip install -r requirements.txt && \
    pip install git+https://github.com/rdkit/django-rdkit.git
