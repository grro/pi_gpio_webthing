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
            """Provides a comma-separated list of all registered input GPIO names."""
            return ", ".join(self.in_gpios.keys())

        @self.mcp.resource("db://names/out")
        def list_out_names() -> str:
            """Provides a comma-separated list of all registered output GPIO names."""
            return ", ".join(self.out_gpios.keys())

        @self.mcp.resource("db://{name}")
        def get_value(name: str) -> str:
            """
            Dynamic resource to retrieve the current state (ON/OFF) of a specific GPIO.
            Args:
                name: The dictionary key/name of the GPIO pin.
            """
            try:
                if name in self.in_gpios:
                    return "ON" if self.in_gpios[name].on else "OFF"
                elif name in self.out_gpios:
                    return "ON" if self.out_gpios[name].on else "OFF"
                return f"Error: GPIO '{name}' not found."
            except Exception as e:
                return f"Error retrieving {name}: {str(e)}"

        # --- MCP Tools ---
        # Tools are executable functions that allow the AI to perform actions.

        @self.mcp.tool()
        def set_value(name: str, on: bool) -> str:
            """
            Actionable tool to change the state of an output GPIO pin.

            :param name: The identifier of the pin (e.g., 'led_red', 'relay_1')
            :param on: Boolean value (True for ON, False for OFF)
            :return: A confirmation message or error string.
            """
            if name in self.out_gpios:
                # Triggers the hardware switch via the OutGpio manager
                self.out_gpios[name].switch(on)
                state = "ON" if on else "OFF"
                return f"Successfully set {name} to {state}"
            else:
                return f"GPIO {name} not found or is not an output GPIO."

# npx @modelcontextprotocol/inspector

