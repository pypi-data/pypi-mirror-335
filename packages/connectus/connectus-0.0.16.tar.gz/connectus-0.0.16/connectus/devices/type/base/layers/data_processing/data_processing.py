from .commands.manager import BaseCommandManager
from connectus.tools.structure.data import DataRequest, VariableData, DataCollection

class BaseDataProcessing(BaseCommandManager):
    def __init__(self):
        BaseCommandManager.__init__(self)

    async def process_data(self, request_list: list[DataRequest]):
        try:
            if request_list:
                for request in request_list:
                    if 'update_config' == request.action:
                        self._process_config(request.data)
                    elif 'update_data' == request.action:
                        await self._process_data(request.data)
                    elif 'update_state' == request.action:
                        self._process_state(request.data)
                    elif 'set_config' == request.action:
                        if self.device.device_type == 'simulated':
                            self._process_config(request.data)
                        elif self.device.device_type == 'real':
                            commands_request = self.get_commands(request.data)
                            await self.device.dispatch.send_command(commands_request, self.device.node_params)
                    elif 'error' == request.action:
                        pass
                    else:
                        raise ValueError('Data type not recognized during processing data')
        except Exception as e:
            print('An error occurred during processing data: ', e)

    def _process_config(self, data_collection: DataCollection):
        ''' Check if the configuration is correct and update the device configuration'''
        try:
            if data_collection:
                for data in data_collection.collection:
                    self.device.config.update(data)
        except Exception as e:
            print('An error occurred while processing the configuration: ', e)

    def _process_state(self, data_collection: DataCollection):
        ''' Check if the configuration is correct and update the device configuration'''
        try:
            if data_collection:
                for data in data_collection.collection:
                    self.device.state.update(data)
        except Exception as e:
            print('An error occurred while processing the configuration: ', e)
    
    async def _process_data(self, data_collection: DataCollection):
        ''' Update the device data with the new values and save them in the database'''
        try:
            if data_collection:
                for data in data_collection.collection:
                    self.device.data.update(data)
                    await self.device.managers['node'].save(data) ## esto es eficiente ?? check if it is better to use asyncio.create_task or await
        except Exception as e:
            print('An error occurred while processing the data update: ', e)
    
