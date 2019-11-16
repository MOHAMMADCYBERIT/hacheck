FROM ubuntu:trusty

# add deadsnakes/ppa repo to get python3.6
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && \
    apt-get -y install \
        dpkg-dev \
        python3.6-dev \
        python-pip \
        python-tox \
        python-setuptools \
        debhelper \
        python-yaml \
        libyaml-dev \
        git \
        wget

# the latest dh-virtualenv available for trusty is 0.6, which doesn't causes
# issues for package building
RUN cd `mktemp -d` && \
    wget http://mirrors.kernel.org/ubuntu/pool/universe/d/dh-virtualenv/dh-virtualenv_0.11-1_all.deb && \
    dpkg -i dh-virtualenv_0.11-1_all.deb && \
    apt-get -f install

RUN pip install virtualenv==15.1.0

ENV HOME /work
ENV PWD /work
WORKDIR /work
