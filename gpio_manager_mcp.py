from typing import Dict
from mcp_server import MCPServer
from gpio_manager import OutGpio, InGpio

class GpioManagerMCPServer(MCPServer):

    def __init__(self, name: str, port: int, in_gpios: Dict[str, InGpio], out_gpios: Dict[str, OutGpio]):
        super().__init__(name, port)
        self.out_gpios = out_gpios
        self.in_gpios = in_gpios

        @self.mcp.resource("db://names/in")
        def list_in_names() -> str:
            """Returns a list of all available input sensor names."""
            return ", ".join(self.in_gpios.keys())

        @self.mcp.resource("db://names/out")
        def list_out_names() -> str:
            """Returns a list of all available output actuator names."""
            return ", ".join(self.out_gpios.keys())

        # --- State and Telemetry Resources ---

        @self.mcp.resource("db://{name}/state")
        def get_pin_state(name: str) -> str:
            """Returns the current logical state (ON/OFF) of a pin."""
            try:
                if name in self.in_gpios:
                    return "ON" if self.in_gpios[name].on else "OFF"
                elif name in self.out_gpios:
                    return "ON" if self.out_gpios[name].on else "OFF"
                return f"Error: GPIO '{name}' not found."
            except Exception as e:
                return f"Error retrieving {name} state: {str(e)}"

        @self.mcp.resource("db://{name}/last_on")
        def get_last_on_time(name: str) -> str:
            """Returns the ISO timestamp of when the input pin was last activated."""
            try:
                if name in self.in_gpios:
                    return self.in_gpios[name].last_on.strftime("%Y-%m-%dT%H:%M:%S")
                return f"Error: '{name}' is not an input GPIO."
            except Exception as e:
                return f"Error retrieving {name} last_on: {str(e)}"

        @self.mcp.resource("db://{name}/last_off")
        def get_last_off_time(name: str) -> str:
            """Returns the ISO timestamp of when the input pin was last deactivated."""
            try:
                if name in self.in_gpios:
                    return self.in_gpios[name].last_off.strftime("%Y-%m-%dT%H:%M:%S")
                return f"Error: '{name}' is not an input GPIO."
            except Exception as e:
                return f"Error retrieving {name} last_off: {str(e)}"

        @self.mcp.resource("db://{name}/last_change")
        def get_last_change_time(name: str) -> str:
            """Returns the ISO timestamp of the last state change (input only)."""
            try:
                if name in self.in_gpios:
                    return self.in_gpios[name].last_change.strftime("%Y-%m-%dT%H:%M:%S")
                return f"Error: '{name}' is not an input GPIO."
            except Exception as e:
                return f"Error retrieving {name} last_change: {str(e)}"

        # --- Control Tools ---

        @self.mcp.tool()
        def set_value(name: str, on: bool) -> str:
            """
            Changes the state of an output pin.
            :param name: Identifier (e.g., 'fan', 'led')
            :param on: True to enable, False to disable
            """
            if name in self.out_gpios:
                self.out_gpios[name].switch(on)
                state = "ON" if on else "OFF"
                return f"Successfully set {name} to {state}"
            return f"GPIO {name} not found or is not an output."

# npx @modelcontextprotocol/inspector

