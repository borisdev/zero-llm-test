FROM python:3.11.2-bullseye AS builder
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
