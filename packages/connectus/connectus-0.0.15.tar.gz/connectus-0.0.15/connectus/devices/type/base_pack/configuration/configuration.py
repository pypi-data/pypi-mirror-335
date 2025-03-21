
class Configuration:
    def __init__(self):
        self.__set_managers()

    def __set_managers(self):
        self.managers = {'device': None}

    def add_device_manager(self, device_manager: object):
        self.managers['device'] = device_manager
        self.managers['device'].add(self)

    def add_data_manager(self, data_manager: object):
        for _, device in self.devices.items():
            device.add_data_manager(data_manager)

    def _add_device(self, device: object):
        self.devices[device.id] = device