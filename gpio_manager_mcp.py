from typing import Dict
from gpio_manager import OutGpio, InGpio
from mcplib.server import MCPServer

class GpioManagerMCPServer(MCPServer):


    def __init__(self, name: str, port: int, in_gpios: Dict[str, InGpio], out_gpios: Dict[str, OutGpio]):
        super().__init__(name, port)
        self.out_gpios = out_gpios
        self.in_gpios = in_gpios
        for in_gpio in in_gpios.values():
            in_gpio.register_listener(lambda gpio=in_gpio: self.on_in_changed(gpio))

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


        @self.mcp.resource("inputpin://state")
        def get_input_sensor_state() -> str:
            """
            Retrieves the current logical state of all configured input sensors.

            This method acts as a continuous MCP resource endpoint ('inputpin://state'),
            providing a real-time overview of the system's hardware inputs. It iterates
            through all registered input GPIOs and formats their data into a readable list.

            Returns:
                str: A formatted multiline string detailing the identifier, description,
                     and current state (ON/OFF) of each sensor. If no input sensors are
                     registered, it returns a clear fallback message.
            """
            lines = ["Current GPIO Sensor Status:"]
            for name, sensor in self.in_gpios.items():
                state = "ON" if sensor.on else "OFF"
                desc = sensor.description or "No description"
                lines.append(f"- {name} ({desc}): {state}")

            if len(lines) == 1:
                return "No sensors connected."

            return "\n".join(lines)


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
                    description_line = f"\nDescription: {device.description}" if device.description else ""

                    return (f"Pin {dev_type} '{name}': {state}\n"
                            f"Last ON: {last_on} UTC\n"
                            f"Last OFF: {last_off} UTC\n"
                            f"Last Change: {last_change} UTC"
                            f"{description_line}")


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

    def on_in_changed(self, in_gpio: InGpio):
        status = "ON" if in_gpio.on else "OFF"
        identifier = in_gpio.description if in_gpio.description else "Unknown sensor"

        self.mcp.push_log(f"Sensor '{identifier}' changed to {status}.", level="info")
        self.mcp.push_resource_update("inputpin://state")

