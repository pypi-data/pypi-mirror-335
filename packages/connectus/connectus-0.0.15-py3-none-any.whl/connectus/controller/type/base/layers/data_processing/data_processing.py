from connectus.tools.structure.data import DataCollection, DataRequest
from abc import ABC, abstractmethod

class BaseDataProcessing(ABC):
    def __init__(self):
        pass
    
    def process(self, request_list: list[DataRequest]):
        try:
            if request_list:
                for request in request_list:
                    if 'update_data' == request.action:
                        self._process_data(request.data)
                    elif 'error' == request.data:
                        pass
                    else:
                        raise ValueError('Data type not recognized during processing data')
        except Exception as e:
            print('An error occurred during processing data: ', e)

    def _process_data(self, data_collection: DataCollection):
        ''' Update the device data with the new values and save them in the database'''
        try:
            if data_collection.collection:
                self.controller.data.update(data_collection)
        except Exception as e:
            print('An error occurred while processing the data update: ', e)