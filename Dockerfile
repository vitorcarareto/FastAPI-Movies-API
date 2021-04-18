FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

# Install requirements
COPY ./requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENV APP_PATH=/app
RUN mkdir ${APP_PATH}
WORKDIR ${APP_PATH}
COPY . ${APP_PATH}
