FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /application
# Ограничение доступа к папке с кодовой базой
RUN groupadd -r developers && useradd -d /application -r -g developers developer \
    && chown developer:developers -R /application
COPY requirements.txt /application

RUN pip install --no-cache-dir -r requirements.txt
COPY . /application

# make wait-for-postgres.sh executable
RUN chmod +x wait-for-postgres.sh
