FROM python:3.8.5-slim-buster

WORKDIR /app

ADD requirements.txt /app

RUN apt-get update && apt-get install -y gcc && pip install -r requirements.txt && apt-get clean

# docker build -t python_flask_docker_image python_flask_docker_image