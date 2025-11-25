FROM ubuntu:24.04
FROM python:3.11.7

WORKDIR /opt/data/python

RUN pip install --no-cache-dir pandas==2.2.5 numpy==1.26.4