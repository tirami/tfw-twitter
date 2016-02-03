FROM ubuntu:14.04
WORKDIR /
ADD . /
RUN chmod -R 755 /
RUN apt-get update
RUN apt-get install -y python python-dev python-pip
RUN pip install -r requirements.txt
RUN python -m nltk.downloader stopwords
EXPOSE 5000
CMD python application.py