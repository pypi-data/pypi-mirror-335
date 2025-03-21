from .configuration import Configuration
from abc import ABC, abstractmethod
import asyncio

class BaseController(ABC, Configuration):
    def __init__(self):
        Configuration.__init__(self)

    async def start(self):
        print(f"Starting controller {self.id}")
        await self.initialize()
        print(f"Controller {self.id} is running")
        await self.run()
    
    @abstractmethod
    async def initialize(self):
        pass

    async def run(self):
        try:
            while self.is_running:
                data = self.acquisition.run()
                self.data_processing.process(data)
                output = self.model.run()
                self.dispatch.run(output)
                await self.check_stop()
                await asyncio.sleep(self.sample_time)
        except Exception as e:
            print(f"An error occurred while running the controller: {e}")

    async def stop(self):
        try:
            self.is_running = False
            output_data = self.data_processing.power_off()
            self.dispatch.run(output_data)
            print("Power off controller.")
        except Exception as e:
            print(f"An error occurred while stopping the controller: {e}")

