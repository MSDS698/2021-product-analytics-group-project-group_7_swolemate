FROM python:3.9-slim-buster
COPY . /app
WORKDIR /app


RUN apt-get update
RUN apt-get -y install libpq-dev gcc

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
CMD flask run --host=0.0.0.0

