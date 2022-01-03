FROM python:slim

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    curl bash make gcc  musl-dev libc-dev g++ gnupg

WORKDIR /app/src

RUN groupadd -g 1000 web
RUN useradd -d /app -s /bin/bash -g web -u 1000 web && \
    chown -R 1000:1000 /app

USER web
COPY requirements.txt /app/requirements.txt
RUN pip3 install --user --no-cache-dir -r /app/requirements.txt\
    && rm -rf /app/requirements.txt

USER root

RUN set -ex; \
# gpg: key 5072E1F5: public key "MySQL Release Engineering <mysql-build@oss.oracle.com>" imported
	key='A4A9406876FCBD3C456770C88C718D3B5072E1F5'; \
	export GNUPGHOME="$(mktemp -d)"; \
	gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key"; \
	gpg --batch --export "$key" > /etc/apt/trusted.gpg.d/mysql.gpg; \
	gpgconf --kill all; \
	rm -rf "$GNUPGHOME"; \
	apt-key list > /dev/null

ENV MYSQL_MAJOR 8.0

RUN echo "deb http://repo.mysql.com/apt/debian/ bullseye mysql-${MYSQL_MAJOR}" > /etc/apt/sources.list.d/mysql.list
RUN echo "deb http://repo.mysql.com/apt/debian/ bullseye mysql-tools" >> /etc/apt/sources.list.d/mysql.list

# RUN curl -L -o /tmp/mysql-apt-config_0.8.20-1_all.deb https://dev.mysql.com/get/mysql-apt-config_0.8.20-1_all.deb && \
#      dpkg -i /tmp/mysql-apt-config_0.8.20-1_all.deb && \
#      rm -rf /tmp/mysql-apt-config_0.8.20-1_all.deb
RUN apt-get update && apt-get install -y --no-install-recommends mysql-shell mysql-community-client && rm -rf /var/lib/apt/lists

RUN apt-get remove -y make gcc  musl-dev libc-dev g++ gnupg && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists

COPY cluster.sh /usr/local/bin/cluster.sh

USER web