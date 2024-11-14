import logging
import gpiod



class LedDevice:

    def __init__(self, name: str, gpio_number: int):
        logging.info("initialization of LED " + name + " on " + str(gpio_number))
        self.name = name
        self.gpio_number = gpio_number
        self.is_on = False
        chip = gpiod.Chip('/dev/gpiochip0')
        self.led = chip.get_line(self.gpio_number)
        config = gpiod.line_request()
        config.consumer = "Blink"
        config.request_type = gpiod.line_request.DIRECTION_OUTPUT
        self.led.request(config)
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
        self.led.set_value(1 if on else 0)
        self.is_on = True
        self.__notify_listener()
