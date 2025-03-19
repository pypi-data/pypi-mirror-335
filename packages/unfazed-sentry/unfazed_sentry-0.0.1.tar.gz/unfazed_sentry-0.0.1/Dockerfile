FROM python:3.12.3-bullseye


COPY . /unfazed_sentry
WORKDIR /unfazed_sentry

RUN pip3 install uv
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
RUN uv sync
