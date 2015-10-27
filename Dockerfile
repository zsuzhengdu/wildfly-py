###############################################################################################
# Docker container image with wildfly-py and dependencies.
#
# See: README.md
###############################################################################################

FROM fedora:22

MAINTAINER CENX "cenx.com"

# install required packages
#RUN easy_install pip
#RUN wget  https://bootstrap.pypa.io/get-pip.py
#RUN python get-pip.py
RUN /usr/bin/dnf install -y git python-pip python-crypto gcc python-devel && \
    pip install --upgrade pip

ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
# Deploy the project source in “Development Mode”
#RUN pip install --editable .
#xRUN pip install .
#ENTRYPOINT ["/usr/bin/wildfly-py"]
