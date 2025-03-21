from abc import ABC, abstractmethod
from connectus.tools.structure.data import DataRequest

class BaseAcquisition(ABC):
    def __init__(self):
        pass

    def run(self) -> list[DataRequest]:
        try:
            response_list = self.controller.device_manager.get([DataRequest(action= 'get_data', device_ids= self.controller.device_ids)])
            resquests = []
            for response in response_list:
                if response.data.collection:
                    resquests = [DataRequest(action= 'update_data', data= response.data)]
            return resquests
        except Exception as e:
            print(f"An error occurred while running controller: {e}")