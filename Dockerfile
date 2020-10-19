# This Dockerfile allows to run tests
# on different Python versions locally
#
# Build: docker build . -t py3.8.0:v1
#        docker build . -t py3.8.0:v2
#
# Test:  docker run -t py3.8.0:v1
#        docker run -t py3.8.0:v2

FROM ubuntu:xenial
ARG BUILDDIR="/tmp/build"
ARG PYTHON="3.8.0"
ARG VARANA="/home/varana"
WORKDIR ${BUILDDIR}

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
        wget \
        gcc \
        make \
        libdb4o-cil-dev \
        libffi-dev \
        libgdbm-dev \
        libgdm-dev \
        liblzma-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libpcap-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libtk8.5 \
        openssl \
        uuid-dev \
        zlib1g-dev

RUN wget https://www.python.org/ftp/python/${PYTHON}/Python-${PYTHON}.tgz
RUN tar zxvf Python-${PYTHON}.tgz
RUN cd Python-${PYTHON} && \
    ./configure && \
    make && \
    make install && \
    rm -rf ${BUILDDIR}

RUN mkdir ${VARANA}
COPY varana ${VARANA}

RUN cd ${VARANA} && \
    pip3 install -U pip && \
    pip install pytest && \
    pip install -r requirements.txt && \
    pip install .

CMD pytest -vv /home/varana
