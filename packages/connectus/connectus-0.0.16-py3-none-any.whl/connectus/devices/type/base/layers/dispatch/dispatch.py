from connectus.tools.structure.data import DataRequest
from abc import ABC, abstractmethod

class BaseDispatch(ABC):
    def __init__(self):
        pass
    
    async def send_command(self, request_list: list[DataRequest], node_params: dict[str, any]):
        if request_list:
            await self.device.node.write(request_list, node_params)
    
    async def read_command(self, request_list: list[DataRequest], node_params: dict[str, any]):
        if request_list:
            await self.device.node.read(request_list, node_params)

    