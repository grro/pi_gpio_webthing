import sys
from webthing import (MultipleThings, Property, Thing, Value, WebThingServer)
from dataclasses import dataclass
from typing import List
import logging
import tornado.ioloop
from gpio_manager import OutGpio


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



class OutThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, out: OutGpio):
        Thing.__init__(
            self,
            'urn:dev:ops:gpio_out-1',
            'Out ' + out.name,
            ['GpioOut'],
            ""
        )

        self.ioloop = tornado.ioloop.IOLoop.current()
        self.out = out

        self.is_on = Value(out.is_on, out.switch)
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
        pass



def run_server(port: int, confs: List[Config]):
    leds = [OutThing(OutGpio(conf.port, conf.name)) for conf in confs if conf.type.lower() == 'led']
    server = WebThingServer(MultipleThings(leds, "outs"), port=port, disable_host_validation=True)
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
