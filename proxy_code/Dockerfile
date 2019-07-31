FROM ubuntu:18.04
MAINTAINER Mingxun Wang "mwang87@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential

RUN pip3 install flask
RUN pip3 install gunicorn
RUN pip3 install requests

RUN pip3 install pathvalidate
RUN pip3 install psutil
RUN pip3 install redis
RUN pip3 install -U Celery
RUN pip3 install pyamqp
RUN pip3 install pyMolNetEnhancer
RUN pip3 install requests_cache

COPY . /app
WORKDIR /app