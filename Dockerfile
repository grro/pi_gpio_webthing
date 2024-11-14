FROM python:3.11


ENV port 8642
ENV gpio ""

RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
RUN pip install gpiozero --break-system-packages
RUN pip install webthing>=0.15.0 --break-system-packages


CMD python /etc/app/gpio_manager_webthing.py $port $gpio
RUN /bin/bash



