import logging
import RPi.GPIO as GPIO



class OutGpio:

    def __init__(self, gpio_number: int, name: str):
        self.name = name
        self.gpio_number = gpio_number
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_number, GPIO.OUT)

    def switch(self, on:bool):
        if on:
            logging.info("setting OUT " + str(self.gpio_number) + " on")
            GPIO.output(self.gpio_number,GPIO.HIGH)
        else:
            logging.info("setting OUT " + str(self.gpio_number) + " off")
            GPIO.output(self.gpio_number,GPIO.LOW)

    def is_on(self) -> bool:
        return GPIO.input(self.gpio_number)