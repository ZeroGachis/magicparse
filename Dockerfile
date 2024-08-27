FROM 007065811408.dkr.ecr.eu-west-3.amazonaws.com/python-3-11:1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

COPY . .

RUN poetry install --without dev && \
    poetry config http-basic.* --unset

CMD ["bash"]
