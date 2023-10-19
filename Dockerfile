FROM --platform=amd64 python:3.9.18-slim-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt
RUN chmod +x /app/./run.sh

EXPOSE 8000

CMD ["/app/./run.sh"]