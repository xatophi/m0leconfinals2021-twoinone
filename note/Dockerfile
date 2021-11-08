FROM python:3-alpine

WORKDIR /usr/src/app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN apk update && apk add python3-dev gcc g++ libc-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt 

COPY app/ ./app
RUN rm app/db/db.sqlite && chown appuser:appgroup app/db

USER appuser


ENV EMAIL_NOTE=admin@m0lecon.it
ENV PASSWORD_NOTE=OB7DJ7BS69R4TsJZvZdf

RUN flask create-db


EXPOSE 8080/tcp


CMD gunicorn -w 4 --bind :8080 "app:create_app()" --user appuser --group appgroup