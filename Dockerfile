FROM python:3.8
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt
RUN mkdir /app
COPY server /app
WORKDIR /app