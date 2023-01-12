FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install --no-install-recommends -y build-essential curl libpq-dev

RUN mkdir /api

WORKDIR /api

VOLUME /api

COPY requirements.txt /api/requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000

EXPOSE 8000
