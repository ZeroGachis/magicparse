FROM python:3.10-slim-bullseye

RUN apt update && apt install -y git

WORKDIR /home/src/csvmagic

RUN pip install \
    pytest \
    pre-commit

COPY . ./
RUN pre-commit install
RUN pip install -e .

CMD ["bash"]
