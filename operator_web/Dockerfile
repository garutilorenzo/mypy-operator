FROM python:3-alpine

RUN apk add --no-cache libpq-dev curl bash make gcc linux-headers openssl-dev libffi-dev musl-dev libc-dev g++

WORKDIR /app/src

RUN addgroup --gid 1000 web && \
    adduser \
    --disabled-password \
    --gecos "" \
    --home /app \
    --ingroup web \
    --no-create-home \
    --uid 1000 \
    web && \
    chown -R 1000:1000 /app

USER web
COPY operator_web/requirements.txt /app/requirements.txt
RUN pip3 install --user --no-cache-dir -r /app/requirements.txt\
    && rm -rf /app/requirements.txt

USER root
RUN apk del --no-network make gcc linux-headers musl-dev openssl-dev libffi-dev libc-dev g++
COPY ./src /app 
RUN chown -R 1000:1000 /app/src

USER web