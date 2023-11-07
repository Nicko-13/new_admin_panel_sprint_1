FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /application
COPY requirements.txt /application

RUN pip install --no-cache-dir -r requirements.txt
COPY . /application