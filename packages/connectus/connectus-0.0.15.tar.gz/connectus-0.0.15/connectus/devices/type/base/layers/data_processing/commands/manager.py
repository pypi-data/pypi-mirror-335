from connectus.tools.structure.data import DataRequest, VariableData
from abc import ABC, abstractmethod

class BaseCommandManager(ABC):
    def __init__(self):
        pass

    def _get_state_value(self, name):
        """Retrieve the current state value for a specific field name."""
        for field in self.device.state:
            if field["name"] == name:
                return field["value"]
        return None  # Return None if name is not found

    def _is_value_within_limits(self, name, value):
        """Check if a value is within its allowed limits."""
        for limit in self.limits:
            if limit["name"] == name:
                return limit["min_value"] <= value <= limit["max_value"]
        return True  # No limits defined; assume valid

    def _is_command_needed(self, name, new_value):
        """Check if a command is needed based on the current state."""
        current_value = self._get_state_value(name)
        return current_value != new_value

    def get_commands(self, data: list[VariableData]) -> list[DataRequest]: # we must check which commands we must send to the device to set the new value (black box)
        
        # command = next(
        #     (cmd for cmd in self.device.config if cmd["name"] == name),
        #     None,
        # )
        # if not command:
        #     raise ValueError(f"Unknown command field: {name}")

        # if not self._is_value_within_limits(name, new_value):
        #     raise ValueError(f"Value {new_value} is out of allowed limits for '{name}'.")

        # if not self._is_command_needed(name, new_value):
        #     print(f"Command '{name}' with value '{new_value}' is not needed.")
        #     return
        commands_request = [
            DataRequest(
                action="set_config",
                device_ids=[self.device.id],
                data=data)
        ]
        return commands_request