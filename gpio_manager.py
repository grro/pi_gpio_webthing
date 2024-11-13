import logging
import RPi.GPIO as GPIO


class OutGpio:

    def __init__(self, name: str, gpio_number: int):
        logging.info("initialazation of out gpio " + name + " on " + str(gpio_number))
        self.name = name
        self.gpio_number = gpio_number
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_number, GPIO.OUT)
        self.__listener = lambda: None    # "empty" listener

    def set_listener(self,listener):
        self.__listener = listener

    def __notify_listener(self):
        try:
            self.__listener()
        except Exception as e:
            logging.warning(str(e))

    def switch(self, on: bool):
        if on:
            GPIO.output(self.gpio_number,GPIO.HIGH)
        else:
            GPIO.output(self.gpio_number,GPIO.LOW)
        self.__notify_listener()

    def is_on(self) -> bool:
        return GPIO.input(self.gpio_number)