FROM python_flask_docker_image

WORKDIR /app

ADD . /app

CMD ["uwsgi", "app.ini"]