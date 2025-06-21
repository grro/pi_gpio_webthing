import logging
import RPi.GPIO as GPIO
from threading import Thread
from time import sleep



class OutGpio:

    def __init__(self, gpio_number: int, name: str, reverted: bool):
        self.name = name
        self.gpio_number = gpio_number
        self.reverted = reverted
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_number, GPIO.OUT)
        logging.info("GPIO OUT " + name + " registered on " + str(self.gpio_number) + (" (reverted=true)" if self.reverted else ""))
        self.switch(False)

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




class InGpio:

    def __init__(self, gpio_number: int, name: str, reverted: bool):
        self.name = name
        self.gpio_number = gpio_number
        self.reverted = reverted
        self.__on = None
        self.listener = lambda: None
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_number, GPIO.IN)
        logging.info("GPIO IN " + name + " registered on " + str(self.gpio_number) + (" (reverted=true)" if self.reverted else ""))
        GPIO.add_event_detect(self.gpio_number, GPIO.BOTH, callback=self.__check())
        Thread(target=self.__loop, daemon=True).start()

    @property
    def on(self) -> bool:
        return self.__on if not self.reverted else self.__on

    def register_listener(self, listener):
        self.listener = listener

    def __check(self):
        new_on = GPIO.input(self.gpio_number) == 1
        if new_on != self.__on:
            self.__on = new_on
            logging.info("GPIO IN " + self.name + " new state " + str(self.on) + " (GPIO: " + str(GPIO.input(self.gpio_number)) + ")")
            self.listener()

    def __loop(self):
        while True:
            try:
                self.__check()
            except Exception as e:
                logging.error("Error in GPIO IN " + self.name + " listener: " + str(e))
            finally:
                sleep(9)