FROM python:3.10-slim-bullseye

RUN apt update && apt install -y git


RUN pip install pytest

WORKDIR /home/src/magicparse

COPY . ./
RUN pip install -e .[dev]

CMD ["bash"]
