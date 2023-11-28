FROM --platform=amd64 python:3.12-slim AS base-image

LABEL VERSION="1.8.0"
LABEL MAINTAINER="DniGamer <dnigamerofficial@gmail.com>"
LABEL DESCRIPTION="Dockerfile for the dashboarduni repository."
LABEL REPOSITORY="https://github.com/dnigamer/dashboarduni"

FROM base-image as linux-packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel

FROM linux-packages as copy-files
WORKDIR /app
COPY . /app

FROM copy-files as install-dependencies
RUN pip3 install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]