FROM mysql:latest
RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext curl jq && \
    rm -rf /var/lib/apt/lists/*
RUN cp /usr/bin/envsubst /usr/bin/envsubst_ && \
    apt-get remove -y gettext && apt-get -y autoremove
RUN mv /usr/bin/envsubst_ /usr/bin/envsubst
COPY docker-entrypoint.sh /usr/local/bin/
COPY my.cnf.tpl /usr/local/bin
COPY my_min.cnf.tpl /usr/local/bin
RUN rm -f /entrypoint.sh && ln -s usr/local/bin/docker-entrypoint.sh /entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]