FROM debian:latest

ENV port 8642
ENV gpio ""

RUN apt update && apt install -y python3 python3-pip python3-libgpiod


RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
ADD requirements.txt /etc/app/.
RUN pip3  install -r requirements.txt --break-system-packages

CMD python3 /etc/app/gpio_manager_webthing.py $port $gpio



