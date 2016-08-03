###############################################################################################
# Docker container image with wildfly-py and dependencies.
#
# See: README.md
###############################################################################################

FROM alpine:3.2

MAINTAINER CENX "cenx.com"

RUN apk update && apk add py-pip gcc python-dev

ADD . /home/wildfly-py
WORKDIR /home/wildfly-py

RUN pip install -r dev-requirements.txt
RUN pip install .
