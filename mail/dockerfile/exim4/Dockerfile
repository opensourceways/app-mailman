FROM ubuntu:16.04

LABEL version="1.0.0"
LABEL maintainer="developer@osinfra.cn"

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini.asc /tini.asc
RUN gpg --batch --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 \
 && gpg --batch --verify /tini.asc /tini && chmod +x /tini

RUN apt-get update && apt-get install -y exim4 && rm -rf /var/lib/apt/lists/*

EXPOSE 25
CMD ["/tini", "--", "exim", "-bd", "-v"]
