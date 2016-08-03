FROM anapsix/alpine-java:jdk8

COPY . /java
WORKDIR /java

RUN apk add --update curl && rm -rf /var/cache/apk/*

RUN chmod +x setup.sh
ENTRYPOINT ["sh"]
