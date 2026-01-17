import sys
from webthing import (MultipleThings, Property, Thing, Value, WebThingServer)
from dataclasses import dataclass
from typing import List
import logging
import tornado.ioloop
from gpio_manager import OutGpio, InGpio
from gpio_manager_web import GpioManagerWebServer
from gpio_manager_mcp import GpioManagerMCPServer


@dataclass
class Config:
    type: str
    name: str
    description: str
    port: int
    reverted: bool

    @staticmethod
    def parse(conf: str):
        logging.info("parsing " + conf)
        parts = conf.split(":")
        try:
            if len(parts) > 4:
                return Config(parts[0], parts[1], parts[2], int(parts[3]), bool(parts[4]))
            else:
                return Config(parts[0], parts[1], parts[2], int(parts[3]), False)
        except Exception as e:
            logging.error("error parsing '" + conf + "':   " + str(e))
            raise e


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



class InThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, in_gpio: InGpio):
        Thing.__init__(
            self,
            'urn:dev:ops:gpio_in-1',
            'In ' + in_gpio.name,
            ['GpioIn'],
            ""
        )

        self.ioloop = tornado.ioloop.IOLoop.current()
        self.in_gpio = in_gpio

        self.is_on = Value(in_gpio.on)
        self.add_property(
            Property(self,
                     'on',
                     self.is_on,
                     metadata={
                         'title': 'is on',
                         "type": "boolean",
                         'description': 'True if is on',
                         'readOnly': True,
                     }))

        self.last_on = Value(in_gpio.last_on.strftime("%Y-%m-%dT%H:%M:%S"))
        self.add_property(
            Property(self,
                     'last_on',
                     self.last_on,
                     metadata={
                         'title': 'last on',
                         "type": "string",
                         'description': 'datetime of last on (ISO8601)',
                         'readOnly': True,
                     }))

        self.last_off = Value(in_gpio.last_off.strftime("%Y-%m-%dT%H:%M:%S"))
        self.add_property(
            Property(self,
                     'last_off',
                     self.last_off,
                     metadata={
                         'title': 'last off',
                         "type": "string",
                         'description': 'datetime of last off (ISO8601)',
                         'readOnly': True,
                     }))

        self.last_change = Value(in_gpio.last_change.strftime("%Y-%m-%dT%H:%M:%S"))
        self.add_property(
            Property(self,
                     'last_change',
                     self.last_change,
                     metadata={
                         'title': 'last change',
                         "type": "string",
                         'description': 'datetime of last change (ISO8601)',
                         'readOnly': True,
                     }))

        self.in_gpio.register_listener(self.on_value_changed)

    def on_value_changed(self):
        self.ioloop.add_callback(self._on_value_changed)

    def _on_value_changed(self):
        self.is_on.notify_of_external_update(self.in_gpio.on)
        self.last_on.notify_of_external_update(self.in_gpio.last_on.strftime("%Y-%m-%dT%H:%M:%S"))
        self.last_off.notify_of_external_update(self.in_gpio.last_off.strftime("%Y-%m-%dT%H:%M:%S"))
        self.last_change.notify_of_external_update(self.in_gpio.last_change.strftime("%Y-%m-%dT%H:%M:%S"))


def run_server(name: str, port: int, confs: List[Config]):
    in_leds = [OutThing(OutGpio(conf.port, conf.name, conf.description, conf.reverted)) for conf in confs if conf.type.lower() == 'out']
    out_leds = [InThing(InGpio(conf.port, conf.name, conf.description, conf.reverted)) for conf in confs if conf.type.lower() == 'in']
    leds = in_leds + out_leds
    server = WebThingServer(MultipleThings(leds, "outs"), port=port, disable_host_validation=True)
    web_server = GpioManagerWebServer(port=port+1, in_gpios={thing.in_gpio.name: thing.in_gpio for thing in out_leds}, out_gpios={thing.out.name: thing.out for thing in in_leds})
    mcp_server = GpioManagerMCPServer(name, port=port+2, in_gpios={thing.in_gpio.name: thing.in_gpio for thing in out_leds}, out_gpios={thing.out.name: thing.out for thing in in_leds})
    try:
        logging.info('starting the server on port ' + str(port))
        web_server.start()
        mcp_server.start()
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        web_server.stop()
        mcp_server.stop()
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    try:
        logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger('tornado.access').setLevel(logging.ERROR)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
        name = sys.argv[1]
        port = int(sys.argv[2])
        gpio = sys.argv[3]
        logging.info("gpio: " + gpio)
        gpio = gpio.replace("_", " ")
        confs = [Config.parse(conf) for conf in gpio.split("&")]
        run_server(name, port, confs)
    except Exception as e:
        logging.error(str(e))
        raise e

