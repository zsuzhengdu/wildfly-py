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

#ADD . /tmp/wildfly-py
#WORKDIR /tmp/wildfly-py
#RUN pip install -e .

ENTRYPOINT ["/usr/bin/wildfly-py"]
