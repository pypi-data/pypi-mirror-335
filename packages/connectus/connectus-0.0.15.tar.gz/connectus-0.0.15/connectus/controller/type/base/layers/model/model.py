from abc import ABC, abstractmethod
from time import time

class BaseModel(ABC):
    def __init__(self):
        self.index = 0
        self.last_index = False
        self.time_executed = 0  # Total elapsed time since the model started
        self.start_time = time()
        self.step_start_time = 0  # Time at the start of the current step
        self.last_value = None

    def select_variable(self, variable_name: str):
        """Select the control variable for operation."""
        try:
            for command in self.controller.commands.collection:
                if variable_name in command.variable_name:
                    self.selected_command = command
                    return
        except Exception as e:
            print(f"An error occurred while selecting the variable: {e}")

    def set_curve(self, variable_curve: list[float], duration: list[float]):
        """
        Generate a curve for the selected variable.
        :param variable_curve: A list of values defining the curve.
        :param duration: A list of durations for each value in the curve.
        """
        if not hasattr(self, "selected_command") or not self.selected_command:
            raise ValueError("No control variable selected.")
        self.curve = variable_curve
        self.duration = duration

    def run(self):
        """Run the model."""
        try:
            if not hasattr(self, "curve") or not self.curve or not self.duration:
                raise ValueError("No curve or duration defined.")

            # Check stop conditions
            if not self.last_index:
                # Calculate elapsed time for the current step
                elapsed_step_time = time() - self.step_start_time
                self.time_executed = time() - self.start_time

                duration = self.duration[self.index]
                value = self.curve[self.index]

                # Move to the next step if the current duration is exceeded
                if elapsed_step_time >= duration:
                    self.step_start_time = time()  # Reset step start time
                    self.index += 1

                    # Check if we've reached the last index
                    if self.index >= len(self.curve):
                        self.last_index = True
                        return  # Stop processing further

                # Execute command if the value changes
                if self.last_value != value:
                    self.last_value = value
                    return self.selected_command.method(value)
        except Exception as e:
            print(f"An error occurred while running the model: {e}")
