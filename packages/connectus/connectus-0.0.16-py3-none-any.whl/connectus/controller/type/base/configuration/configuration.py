from connectus.tools.structure.data import DataCollection

class Configuration():
    def __init__(self):
        self.device_manager = None
        self.stop_event = None
        self.data = DataCollection()
        self.state = DataCollection()
        self.config = DataCollection()
        self.device_ids = []