FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y locales locales-all python3-psycopg2 curl unzip xvfb libxi6 libgconf-2-4 gnupg2

RUN curl -sS -o _chrome_key https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add _chrome_key
RUN echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update
RUN apt-get -y install google-chrome-stable=96.0.4664.45-1

RUN wget https://chromedriver.storage.googleapis.com/96.0.4664.45/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip

RUN mv chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

WORKDIR /code
ADD requirements.txt /code/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
ADD . /code
