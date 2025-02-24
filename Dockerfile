FROM python:3.13-slim as requirements-stage
WORKDIR /tmp
RUN pip install poetry
RUN pip install poetry-plugin-export
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.13-slim
WORKDIR /code
ENV TZ=Asia/Taipei
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN apt-get update && apt-get -y install gcc
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./src /code/src
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]