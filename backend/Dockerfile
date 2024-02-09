# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm as base

ENV ENV=dev
ENV PORT ""

WORKDIR /app/backend

# install python dependencies
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

# copy backend files
COPY . .

ENTRYPOINT [ "bash", "start.sh"]