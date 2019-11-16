FROM ubuntu:14.04
MAINTAINER John Billings <billings@yelp.com>

# add deadsnakes/ppa repo to get python3.6
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && apt-get -y install python3.6-dev

ADD itest.sh /itest.sh

CMD /itest.sh
