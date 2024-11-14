import sys
from webthing import (MultipleThings, Property, Thing, Value, WebThingServer)
from dataclasses import dataclass
from typing import List
import logging
import tornado.ioloop
from gpio_manager import LedDevice


@dataclass
class Config:
    type: str
    name: str
    port: int

    @staticmethod
    def parse(conf: str):
        logging.info("parsing " + conf)
        parts = conf.split(":")
        return Config(parts[0], parts[1], int(parts[2]))



class LedThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, led: LedDevice):
        Thing.__init__(
            self,
            'urn:dev:ops:led-1',
            'LED ' + led.name,
            ['LED'],
            ""
        )

        self.ioloop = tornado.ioloop.IOLoop.current()
        self.led = led
        self.led.set_listener(self.on_value_changed)

        self.is_on = Value(led.is_on, led.switch)
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
        self.is_on.notify_of_external_update(self.led.is_on)



def run_server(port: int, confs: List[Config]):
    leds = [LedThing(LedDevice(conf.name, conf.port)) for conf in confs if conf.type.lower() == 'led']
    server = WebThingServer(MultipleThings(leds, "leds"), port=port, disable_host_validation=True)
    try:
        logging.info('starting the server on port ' + str(port))
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('tornado.access').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    port = int(sys.argv[1])
    confs = [Config.parse(conf) for conf in sys.argv[2].split("&")]
    run_server(port, confs)
