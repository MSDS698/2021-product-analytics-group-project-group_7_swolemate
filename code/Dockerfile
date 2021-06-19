FROM python:3.9-slim-buster


RUN apt-get update
RUN apt-get -y install libpq-dev gcc

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000
CMD flask run --host=0.0.0.0


