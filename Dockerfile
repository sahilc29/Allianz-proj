FROM python:3.9-alpine
USER root
RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \ 
    curl

RUN adduser -D -h /home/appuser appuser
COPY . /home/appuser
RUN chown -R appuser:appuser /home/appuser/app

USER appuser
RUN pip install --user --no-warn-script-location -r /home/appuser/requirements.txt

EXPOSE 8080
WORKDIR /home/appuser/app