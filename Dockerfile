FROM ubuntu:14.04

RUN apt-get update

RUN apt-get install -y python python-dev python-pip

RUN pip install -r requirements.txt

RUN python -m nltk.downloader stopwords

EXPOSE 5000

CMD python runserver.py