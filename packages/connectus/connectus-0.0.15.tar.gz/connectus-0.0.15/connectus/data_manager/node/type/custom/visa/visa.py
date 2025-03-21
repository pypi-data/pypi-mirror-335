from ...base import BaseNode
from .configuration import Configuration
from connectus.tools.structure.data import DataRequest, VariableData
import asyncio
import datetime

class VISA(BaseNode, Configuration):
    def __init__(self, node_config: dict[str, str], stop_event: asyncio.Event):
        BaseNode.__init__(self, stop_event)
        Configuration.__init__(self, node_config)

    async def connect(self):
        try:
            await self.create_client()
        except Exception as e:
            print("An error occurred while starting VISA:", e)
    
    async def disconnect(self):
        try:
            await asyncio.sleep(1)  # Wait for 1 second before closing the connection
            self.device.close()
            self.client.close()
        except Exception as e:
            print("An error occurred while disconnecting VISA:", e)

    async def write(self, request_list: list[DataRequest], node_params: dict[str, any]= None):
        try:
            if request_list:
                for request in request_list:
                    for variable in request.data.collection:
                        self.device.write(variable.value)
        except Exception as e:
            print("An error occurred while sending data with VISA protocol:", e)

    async def read(self, request_list: list[DataRequest], node_params: dict[str, any] = None):
        try:
            if request_list:
                for request in request_list:
                    for variable in request.data.collection:
                        value = await self._async_query(variable)
                        self.buffer.append(value)

        except Exception as e:
            print(f"An error occurred while reading the data: {e}")

    async def _async_query(self, variable):
        """Helper method to execute query_ascii_values asynchronously."""
        try:
            value = await asyncio.to_thread(self.device.query_ascii_values, variable.value)
            return VariableData(
                source="visa",
                name=variable.name,
                value=value[0] if value else None,
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                value_type=type(value[0]).__name__ if value else "None",
            )
        except Exception as e:
            return None  # Return None to avoid breaking `gather()`