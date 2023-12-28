FROM python:3.10
RUN apt update -qq && apt upgrade -y
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

