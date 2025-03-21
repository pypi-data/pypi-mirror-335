from abc import ABC, abstractmethod
import asyncio

class BaseNode(ABC):
    def __init__(self, stop_event: asyncio.Event):
        self.stop_event = stop_event
        self.buffer = []

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    async def start(self, sample_time: int = 1): ## indicate what is start
        try:
            pass
            # while not self.stop_event.is_set():
            #     data = self.read()
            #     if data:
            #         self.buffer.append(data)
            #     await asyncio.sleep(sample_time)
            # await self.stop()
        except Exception as e:
            print('An error occurred during running a node: ', e)

    async def stop(self):
        try:
            self.stop_event.set()
            await self.disconnect()
        except Exception as e:
            print('An error occurred stopping a node: ', e)

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self):
        pass
    