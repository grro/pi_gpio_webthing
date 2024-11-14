import logging
import gpiod
from gpiod.line import Direction, Value



class LedDevice:

    def __init__(self, name: str, gpio_number: int):
        logging.info("initialization of LED " + name + " on " + str(gpio_number))
        self.name = name
        self.gpio_number = gpio_number
        self.is_on = False
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
        with gpiod.request_lines("/dev/gpiochip0",consumer="led",config={
            self.gpio_number: gpiod.LineSettings(
                        direction=Direction.OUTPUT, output_value=Value.ACTIVE
                    )
                },
        ) as request:
            request.set_value(self.gpio_number, Value.ACTIVE if on else Value.INACTIVE)
            self.__notify_listener()
