FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /ReFlow
WORKDIR /ReFlow
ADD requirements.txt /ReFlow/
RUN pip install -r requirements.txt
ADD . /ReFlow/
