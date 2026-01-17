from typing import Dict
from gpio_manager import OutGpio, InGpio
from mcplib.server import MCPServer

class GpioManagerMCPServer(MCPServer):

    def __init__(self, name: str, port: int, in_gpios: Dict[str, InGpio], out_gpios: Dict[str, OutGpio]):
        super().__init__(name, port)
        self.out_gpios = out_gpios
        self.in_gpios = in_gpios

        @self.mcp.tool(name="list_names", description="Returns lists of all available input sensor and output actuator names.")
        def list_names() -> str:
            """Provides the names of all connected hardware pins to the AI."""
            inputs = ", ".join(self.in_gpios.keys()) or "None"
            outputs = ", ".join(self.out_gpios.keys()) or "None"
            return f"Inputs: {inputs} | Outputs: {outputs}"

        @self.mcp.tool(name="get_description", description="Returns a human-readable description of what a specific pin is used for.")
        def get_description(name: str) -> str:
            """
            Args:
                name: The identifier of the pin.
            """
            if name in self.in_gpios:
                return f"Input '{name}': {self.in_gpios[name].description}"
            elif name in self.out_gpios:
                return f"Output '{name}': {self.out_gpios[name].description}"
            return f"Error: pin '{name}' not found."

        @self.mcp.tool(name="get_state", description="Returns the current logical state and telemetry (timestamps) of a specific pin.")
        def get_state(name: str) -> str:
            """
            Args:
                name: The identifier of the pin (e.g., 'motion_sensor', 'door_light').
            """
            try:
                if name in self.in_gpios:
                    sensor = self.in_gpios[name]
                    state = "ON" if sensor.on else "OFF"

                    last_on = sensor.last_on.strftime("%Y-%m-%dT%H:%M:%S") if sensor.last_on else "Never"
                    last_off = sensor.last_off.strftime("%Y-%m-%dT%H:%M:%S") if sensor.last_off else "Never"
                    last_change = sensor.last_change.strftime("%Y-%m-%dT%H:%M:%S") if sensor.last_change else "Never"

                    return (f"GPIO Input '{name}': {state}\n"
                            f"Last ON: {last_on}\n"
                            f"Last OFF: {last_off}\n"
                            f"Last Change: {last_change}")

                elif name in self.out_gpios:
                    actuator = self.out_gpios[name]
                    state = "ON" if actuator.on else "OFF"
                    return f"GPIO Output '{name}': {state}"

                return f"Error: pin '{name}' not found. Use 'list_names' to see available pins."

            except Exception as e:
                return f"Error retrieving {name} state: {str(e)}"

        @self.mcp.tool(name="set_state", description="Changes the state of an output actuator.")
        def set_state(name: str, on: bool) -> str:
            """
            Args:
                name: Identifier of the output (e.g., 'fan', 'led').
                on: True to enable (ON), False to disable (OFF).
            """
            if name in self.out_gpios:
                self.out_gpios[name].switch(on)
                state = "ON" if on else "OFF"
                return f"Successfully set {name} to {state}"
            return f"Error: pin '{name}' not found or is not an output actuator."

# npx @modelcontextprotocol/inspector