FROM python:3.6

RUN python3.6 -m pip install pip --upgrade
RUN apt-get install gcc g++

WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip3.6 install -r requirements.txt
# RUN python3.6 -m spacy download pt

EXPOSE 5000
EXPOSE 8888

ENV FLASK_APP=main.py FLASK_DEBUG=1

COPY . .
