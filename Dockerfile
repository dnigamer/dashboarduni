FROM --platform=amd64 python:3.9.18-slim-bullseye AS base-image

FROM base-image as linux-packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

FROM linux-packages as copy-files
WORKDIR /app
COPY . /app

FROM copy-files as install-dependencies
RUN pip3 install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]