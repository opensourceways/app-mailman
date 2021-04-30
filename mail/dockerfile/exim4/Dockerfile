FROM ubuntu:16.04

LABEL version="1.0.0"
LABEL maintainer="developer@osinfra.cn"

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/local/bin/tini
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini.asc /tini.asc
RUN gpg --batch --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 \
 && gpg --batch --verify /tini.asc /usr/local/bin/tini && chmod +x /usr/local/bin/tini

RUN apt-get update && apt-get install -y exim4 && apt-get install -y spf-tools-perl && rm -rf /var/lib/apt/lists/*

# overwrite derault alias file
COPY alias /etc/aliases

EXPOSE 25
CMD ["tini", "--", "exim", "-bd", "-v"]
