FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN apt-get update -y && apt-get upgrade -y

# Ставим зависимости GDAL, PROJ
RUN apt-get install -y gdal-bin libgdal-dev
RUN apt-get install -y python3-gdal
RUN apt-get install -y binutils libproj-dev
RUN apt-get install -y cron
RUN cp app/fill_db.sh /etc/cron.daily/fill_db.sh

RUN mkdir /app
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt