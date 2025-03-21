from connectus.tools.structure.data import DataRequest
from abc import ABC, abstractmethod

class BaseDispatch(ABC):
    def __init__(self):
        pass

    def run(self, request_list: list[DataRequest]):
        if request_list:
            self.controller.device_manager.set(request_list)