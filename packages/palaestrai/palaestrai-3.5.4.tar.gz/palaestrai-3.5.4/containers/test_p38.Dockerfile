FROM python:3.8
ENV DEBIAN_FRONTEND noninteractive
RUN mkdir -p /home/app/
RUN apt-get update \
    && apt-get install -y \
        sqlite3 \
        postgresql-client \
        build-essential \
        pandoc \
        graphviz \
        libgraphviz-dev \
    && apt-get autoremove -y \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /home/palaestrai
COPY ["generate-requirements.py", \
      "setup.py", \
      "README.rst", \
      "VERSION", \
      "tox.ini", \
      "mypy.ini", \
      "./"]
RUN python3 generate-requirements.py
RUN pip install -r requirements.txt
COPY ["src",  "src"]
COPY ["doc",  "doc"]
COPY ["tests", "tests"]
COPY ["palaestrai_completion.sh", \
      "palaestrai_completion.zsh", \
      "palaestrai_completion.fish", \
      "./"]
RUN pip install -e .[dev]
RUN apt-get autoremove -y && apt-get autoclean
