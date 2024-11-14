FROM python:3-alpine

ENV port 8642
ENV gpio ""


RUN apk update && apk add python3 py3-libgpiod py3-pip

RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
ADD requirements.txt /etc/app/.
RUN pip install -r requirements.txt

CMD python /etc/app/gpio_manager_webthing.py $port $gpio



