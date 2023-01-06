FROM python:3.9-slim-bullseye

RUN mkdir /app

WORKDIR /app

VOLUME /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000

EXPOSE 8000
