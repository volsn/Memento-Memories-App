FROM python:3.7

MAINTAINER Mykola Volosnikov

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN mkdir /app

WORKDIR /app

COPY ./app/ /app

RUN mkdir -p /vol/web/media && mkdir -p /vol/web/static

RUN useradd -ms /bin/bash user && chown -R user:user /vol/ \
    && chmod -R 755 /vol/web

USER user
