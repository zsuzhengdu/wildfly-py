###############################################################################################
# Docker container image with wildfly-py and dependencies.
#
# See: README.md
###############################################################################################

FROM fedora:22

MAINTAINER CENX "cenx.com"

# install required packages
RUN /usr/bin/dnf install -y git python-pip python-crypto gcc python-devel && \
    pip install --upgrade pip

ADD . /home/wildfly-py
WORKDIR /home/wildfly-py

# install required packages
RUN pip install -r dev-requirements.txt

# Deploy the project source in “Development Mode”
#RUN pip install --editable .
RUN pip install .
