import logging
import RPi.GPIO as GPIO



class OutGpio:

    def __init__(self, gpio_number: int, name: str, reverted: bool):
        self.name = name
        self.gpio_number = gpio_number
        self.reverted = reverted
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_number, GPIO.OUT)
        logging.info("GPIO OUT " + str(self.gpio_number) + " registered " + (" (reverted=true)" if self.reverted else ""))

    def switch(self, on:bool):
        logging.info("setting OUT " + str(self.gpio_number) + " " + ("on" if on else "off"))
        if self.reverted:
            on = not on
        if on:
            GPIO.output(self.gpio_number,GPIO.HIGH)
        else:
            GPIO.output(self.gpio_number,GPIO.LOW)

    def is_on(self) -> bool:
        return GPIO.input(self.gpio_number)