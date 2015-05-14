FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN git clone https://github.com/whitews/FlowIO.git /flowio
WORKDIR /flowio
RUN python setup.py install
RUN mkdir /ReFlow
WORKDIR /ReFlow
ADD requirements.txt /ReFlow/
RUN pip install -r requirements.txt
ADD . /ReFlow/
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
