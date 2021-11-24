FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y locales locales-all
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt
COPY . /code