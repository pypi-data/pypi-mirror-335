from ...base import BaseNode
from .configuration import Configuration
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
import asyncio

class InfluxDB(BaseNode, Configuration):
    def __init__(self, node_config: dict[str, any], stop_event: asyncio.Event):
        BaseNode.__init__(self, stop_event)
        Configuration.__init__(self, node_config)

    async def connect(self):
        try:
            self.client = InfluxDBClientAsync(url=self.url, token=self.token, org=self.org)
        except Exception as e:
            print(f"An error occurred while connecting to the database: {e}")

    async def write(self, data: list[dict[str, any]]):
        try:
            if data:
                points = self.data_processing.prepare_data(data)
                write_api = self.client.write_api()
                await write_api.write(bucket=self.bucket, record=points)
        except Exception as e:
            print(f"An error occurred while inserting the data: {e}")

    async def disconnect(self):
        await self.client.close()

    def read(self):
        pass