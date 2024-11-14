import logging
import gpiod
from gpiod.line import Direction, Value



class LedDevice:

    def __init__(self, name: str, gpio_number: int):
        logging.info("initialization of LED " + name + " on " + str(gpio_number))
        self.name = name
        self.gpio_number = gpio_number
        self.is_on = False
        self.chip=gpiod.Chip('gpiochip0')
        self.lines = self.chip.get_lines([ self.gpio_number ])
        self.lines.request(consumer='gpio', type=gpiod.LINE_REQ_DIR_OUT)
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
        self.lines.set_values([ 1 if on else 0 ])
        self.is_on = True
        self.__notify_listener()
