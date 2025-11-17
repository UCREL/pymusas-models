FROM ubuntu:latest


RUN apt-get -y update \
    && apt-get install -y --no-install-recommends \
    git \
    make \
    wget \
    vim \
    build-essential \
    openssh-client \
    ca-certificates \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=ubuntu

USER $USERNAME
WORKDIR /home/$USERNAME


SHELL ["/bin/bash", "-c"]
RUN set -o pipefail \
    && wget -qO- https://astral.sh/uv/install.sh \
    | sh

ENV PATH="/home/$USERNAME/.local/bin/:$PATH"

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-install-workspace