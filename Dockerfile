FROM python:3.13.10-slim-trixie
LABEL authors="slava.nykon@gmail.com"

ENV PYTHONUNBUFFERED=1
WORKDIR /statusphere

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -s /bin/false my_user && \
    mkdir -p /statusphere/media && \
    chown -R my_user:my_user /statusphere && \
    chmod -R 755 /statusphere/media

USER my_user
