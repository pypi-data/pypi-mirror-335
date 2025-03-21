from connectus.tools.structure.data import DataRequest, VariableData, DataCollection
from abc import ABC, abstractmethod
from datetime import datetime, timezone

class BaseAcquisition(ABC):
    def __init__(self):
        pass

    async def run(self) -> list[DataRequest]:
        if self.device.device_type == 'simulated':
            data = self.device.model.run()
            return data
        elif self.device.device_type == 'real':
            data = self.filter_messages(self.device.node.buffer)
            return data
                
    def process_request(self, request: DataRequest) -> list[DataRequest]:
        ''' convert data to the right format (power to voltage, etc.) '''
        try:
            requests = []
            if 'set_config' == request.action: ## we need to check if the request is valid (is a configurable value?)
                requests.append(request)
            else:
                raise ValueError('Invalid request type')
            return requests
        except Exception as e:
            print('An error occurred during processing request: ', e)
    
    async def stop(self) -> list[DataRequest]: ## We send the data to the database as NULL
        ''' stop the acquisition '''
        data = []
        for source, variables in self.device.data.nested_model().items():
            for name in variables:
                data.append(VariableData(
                    name= name, 
                    timestamp= datetime.now(timezone.utc), 
                    source= source, 
                    experiment_id= variables[name].get('experiment_id'), 
                    unit= variables[name].get('unit'), 
                    value_type= variables[name].get('value_type'), 
                    additional_info= variables[name].get('additional_info')
                ))

        return [DataRequest(action= 'update_data', device_ids= [self.device.id], data= DataCollection(collection=data))]
        