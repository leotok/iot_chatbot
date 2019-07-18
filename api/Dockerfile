FROM python:3.6

WORKDIR /usr/src/app

RUN apt-get install gcc g++

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN python -m spacy download pt

COPY . .

CMD [ "python", "./main.py" ]
