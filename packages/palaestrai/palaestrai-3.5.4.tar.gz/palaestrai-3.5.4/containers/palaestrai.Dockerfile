# palaestrai -- Full-stack palaestrAI dockerfile
#
# The base image contains the extended Python basis along with the packages
# palaestrAI needs in any case. Derived versions either check out palaestrAI
# or install it from PyPI, depending on the "BUILD_TYPE" argument.
#
# BUILD_TYPE:
#   BUILD_TYPE=development  Check out current development from git
#   BUILD_TYPE=master       Install palaestrai & packages from PyPI
#
# PYTORCH_VERSION:
#   Sets the version of the PyTorch base image as
#   `FROM nvcr.io/nvidia/pytorch:$PYTORCH_VERSION`
#
# BUILD_BASE_TESTING:
#   Base image for the "testing" build type. Defaults to "development", but
#   can also be a completely different base image. Useful for referring to a
#   common base image, such as `palaestrai-base:development`.
#
# """
#    Another thing to be careful about is that after every FROM statement,
#    all the ARGs get collected and are no longer available.
# """
# To have an ARG available with the same value as before, they have to be
# "requested" to be present, see: https://stackoverflow.com/a/56748289

ARG BUILD_TYPE=development
ARG PYTORCH_VERSION=2.1.2-cuda11.8-cudnn8-runtime
ARG BUILD_BASE_MASTER=base
ARG BUILD_BASE_TESTING=base

FROM pytorch/pytorch:$PYTORCH_VERSION AS base
ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo "$TZ" > /etc/timezone \
    && apt-get clean \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        wget \
        git \
        sudo \
        curl \
        sqlite3 \
        postgresql-client \
        python3-pip \
        build-essential \
        pandoc \
        graphviz \
        graphviz-dev \
        libgraphviz-dev \
        libxml2-dev \
        libxslt-dev \
    && python3 -m pip install -U pip \
    && conda install -y conda=23.11.0 \
    && conda install -y -c numba numba==0.56.4 \
    && wget https://github.com/jgm/pandoc/releases/download/3.1.11.1/pandoc-3.1.11.1-1-amd64.deb -O pandoc.deb \
    && apt install -y ./pandoc.deb \
    && rm pandoc.deb \
    && useradd -Um -G users palaestrai \
    && mkdir /palaestrai \
    && mkdir -p /workspace \
    && chown palaestrai:palaestrai /workspace \
    && chmod 1770 /workspace



ARG DEV_BRANCH=development

FROM base AS development
WORKDIR /palaestrai

RUN \
    apt-get install -y --no-install-recommends \
        less \
        vim \
        htop \
        dnsutils
RUN git clone -b "${DEV_BRANCH}" --single-branch --depth 1 https://gitlab.com/arl2/palaestrai.git /palaestrai
RUN python3 -m pip install -U -e '.[full-dev]' --prefer-binary;

ENTRYPOINT ["/palaestrai/containers/start.sh"]



FROM $BUILD_BASE_TESTING AS testing
COPY [".", "/palaestrai/"]
RUN python3 -m pip install -U '.[full-dev]' --prefer-binary

ENTRYPOINT []



FROM $BUILD_BASE_MASTER AS master
WORKDIR /palaestrai

COPY [".", "/palaestrai/"]
RUN python3 -m pip install -U '.[full]' --prefer-binary

ENTRYPOINT ["/palaestrai/containers/start.sh"]



FROM $BUILD_TYPE AS final
WORKDIR /palaestrai

RUN \
    chmod 0755 /palaestrai/containers/start.sh \
    && chown -R palaestrai:users /palaestrai \
    && ls -Al /palaestrai
RUN apt-get autoremove -y \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/{palaestrai*,harl,arsenai,*mosaik*}
WORKDIR /workspace
