import logging
from gpiozero import LED


class LedDevice:

    def __init__(self, name: str, gpio_number: int):
        logging.info("initialization of LED " + name + " on " + str(gpio_number))
        self.name = name
        self.gpio_number = gpio_number
        self.led = LED(self.gpio_number)
        self.__listener = lambda: None    # "empty" listener

    def set_listener(self,listener):
        self.__listener = listener

    def __notify_listener(self):
        try:
            self.__listener()
        except Exception as e:
            logging.warning(str(e))

    def switch(self, on: bool):
        logging.info("set LED to " + str(on))
        if on:
            self.led.on()
        else:
            self.led.close()
            self.__notify_listener()

    @property
    def is_on(self) -> bool:
        return self.led.is_active