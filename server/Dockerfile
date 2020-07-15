FROM python:3.6
RUN apt-get update
RUN apt-get install software-properties-common -yqq
RUN add-apt-repository ppa:ubuntugis/ppa
RUN apt-get update; exit 0
RUN apt-get install gdal-bin -yqq
RUN apt-get install libgdal-dev -yqq
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
RUN mkdir /app
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt