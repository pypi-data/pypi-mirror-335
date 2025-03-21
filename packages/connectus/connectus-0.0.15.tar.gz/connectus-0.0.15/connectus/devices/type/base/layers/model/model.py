from connectus.tools.structure.data import DataRequest
from abc import ABC, abstractmethod

class BaseModel(ABC):
    def __init__(self):
        pass
    
    def run(self) -> list[DataRequest]:
        try:
            points = []
            points.append(DataRequest(action= 'update_data', data= self.get_data()))
            return points
        except Exception as e:
            print('An error occurred during model run: ', e)