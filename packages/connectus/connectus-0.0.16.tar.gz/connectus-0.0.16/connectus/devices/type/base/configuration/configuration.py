from connectus.tools.structure.data import DataCollection

class Configuration:
    def __init__(self):
        self.total_time = 0
        self._set_managers()
        self._set_variables()

    def _set_managers(self):
        self.managers = {'device': None, 'node': None}

    def add_device_manager(self, device_manager):
        self.managers['device'] = device_manager
        self.managers['device'].add(self)
    
    def add_data_manager(self, data_manager):
        self.managers['node'] = data_manager

    def _set_variables(self):
        self.data = DataCollection() # Received data from the real device (saved in the database)
        self.state = DataCollection() # State of the device (read only)
        self.config = DataCollection() # Configuration of the device (read/write)