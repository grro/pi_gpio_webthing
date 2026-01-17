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
            """Provides the identifiers of all connected hardware pins to the AI."""
            inputs = ", ".join(self.in_gpios.keys()) or "None"
            outputs = ", ".join(self.out_gpios.keys()) or "None"
            return f"Inputs: {inputs} | Outputs: {outputs}"

        @self.mcp.tool(name="get_description", description="Returns a human-readable description of a specific pin's purpose.")
        def get_description(name: str) -> str:
            """
            Retrieves the 'description' field of a pin (e.g., 'Main garden light').
            Args:
                name: The unique identifier of the pin.
            """
            if name in self.in_gpios:
                return f"Input '{name}': {self.in_gpios[name].description}"
            elif name in self.out_gpios:
                return f"Output '{name}': {self.out_gpios[name].description}"
            return f"Error: pin '{name}' not found."

        @self.mcp.tool(name="get_state", description="Returns the current logical state and activity timestamps (UTC) of a specific pin.")
        def get_state(name: str) -> str:
            """
            Provides real-time status (ON/OFF) and telemetry data.
            Args:
                name: The identifier of the pin (e.g., 'motion_sensor', 'led_strip').
            """
            try:
                # Identify if the pin is an input or an output
                device = self.in_gpios.get(name) or self.out_gpios.get(name)
                dev_type = "Input" if name in self.in_gpios else "Output"

                if device:
                    state = "ON" if device.on else "OFF"

                    # Formatting timestamps to ISO 8601 strings
                    last_on = device.last_on.strftime("%Y-%m-%dT%H:%M:%S") if device.last_on else "Never"
                    last_off = device.last_off.strftime("%Y-%m-%dT%H:%M:%S") if device.last_off else "Never"
                    last_change = device.last_change.strftime("%Y-%m-%dT%H:%M:%S") if device.last_change else "Never"

                    return (f"Pin {dev_type} '{name}': {state}\n"
                            f"Last ON: {last_on} UTC\n"
                            f"Last OFF: {last_off} UTC\n"
                            f"Last Change: {last_change} UTC")

                return f"Error: pin '{name}' not found. Use 'list_names' to see available pins."

            except Exception as e:
                return f"Error retrieving {name} state: {str(e)}"

        @self.mcp.tool(name="set_state", description="Changes the state of an output actuator.")
        def set_state(name: str, on: bool) -> str:
            """
            Physically switches an output pin.
            Args:
                name: Identifier of the output (e.g., 'fan', 'pump').
                on: True to enable (ON), False to disable (OFF).
            """
            if name in self.out_gpios:
                self.out_gpios[name].switch(on)
                state = "ON" if on else "OFF"
                return f"Successfully set {name} to {state}"
            return f"Error: pin '{name}' not found or is not an output actuator."