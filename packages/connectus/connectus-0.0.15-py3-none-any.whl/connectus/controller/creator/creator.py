import asyncio

class ControllerCreator:
    def __init__(self, controller_manager, device_manager, stop_event: asyncio.Event):
        self.controller_manager = controller_manager
        self.device_manager = device_manager
        self.stop_event = stop_event

    def create(self, instance):
            try:
                self.controller = instance
                self._set_managers()
            except Exception as e:
                print("An error occurred while creating controller: ", e)

    def _set_managers(self):
        self.controller.device_manager = self.device_manager
        self.controller_manager.add(self.controller)
        self.controller.stop_event = self.stop_event
