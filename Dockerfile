FROM python:3.10-slim-bullseye

RUN apt update && apt install -y git

ARG USERNAME
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN \
    groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

WORKDIR /home/src/magicparse

RUN pip install pytest

COPY . ./
RUN pip install -e .[dev]

USER $USERNAME

CMD ["bash"]
