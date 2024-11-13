import sys
from webthing import (MultipleThings, Property, Thing, Value, WebThingServer)
from dataclasses import dataclass
from typing import List
import logging
import tornado.ioloop
from gpio_manager import OutGpio


@dataclass
class Config:
    is_out: bool
    name: str
    port: int

    @staticmethod
    def parse(conf: str):
        parts = conf.split(":")
        return Config(bool(parts[0]), parts[1], int(parts[2]))



class OutGpioThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, gpio: OutGpio):
        Thing.__init__(
            self,
            'urn:dev:ops:gpio_out-1',
            'GPIO OUT ' + gpio.name,
            ['GpioOut'],
            ""
        )

        self.ioloop = tornado.ioloop.IOLoop.current()
        self.gpio = gpio
        self.gpio.set_listener(self.on_value_changed)

        self.is_on = Value(gpio.is_on(), gpio.switch)
        self.add_property(
            Property(self,
                     'is-on',
                     self.is_on,
                     metadata={
                         'title': 'is on',
                         "type": "boolean",
                         'description': 'True if is on',
                         'readOnly': False,
                     }))

    def on_value_changed(self):
        self.ioloop.add_callback(self._on_value_changed)

    def _on_value_changed(self):
        self.is_on.notify_of_external_update(self.gpio.is_on())



def run_server(port: int, configs: List[Config]):
    outs = [OutGpioThing(OutGpio(conf.name, conf.port)) for conf in configs if conf.is_out]
    server = WebThingServer(MultipleThings(outs, "outs"), port=port, disable_host_validation=True)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('tornado.access').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    run_server(int(sys.argv[1]), [Config.parse(conf) for conf in sys.argv[2].split("&")])
