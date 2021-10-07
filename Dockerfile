FROM python:3.9.4-slim

WORKDIR /server

COPY requirements.txt /server/

RUN pip install -r requirements.txt

COPY ./server /server
