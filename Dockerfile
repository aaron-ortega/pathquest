FROM python:3.9-alpine

EXPOSE 9000
WORKDIR /opt/pathquest/app
COPY . /opt/pathquest/app

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
