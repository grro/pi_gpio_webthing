FROM python:3.11

ENV port 8642
ENV gpio ""


RUN pip install lgpio pigpio gpio gpiozero

RUN wget https://github.com/Gadgetoid/PY_LGPIO/releases/download/0.2.2.0/lgpio-0.2.2.0.tar.gz
RUN pip install lgpio-0.2.2.0.tar.gz

RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
ADD requirements.txt /etc/app/.
RUN pip install -r requirements.txt

CMD python /etc/app/gpio_manager_webthing.py $port $gpio



