from ...base import BaseNode
from .configuration import Configuration
import asyncio
import serial

class UART(BaseNode, Configuration):
    def __init__(self, node_config: dict[str, str], stop_event: asyncio.Event):
        BaseNode.__init__(self, stop_event)
        Configuration.__init__(self, node_config)

    async def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout)
            print("UART Server started with port: ", self.port)
        except Exception as e:
            print("An error ocurred while starting UART: ", e)
    
    async def disconnect(self):
        self.ser.close()

    def write(self, data: list[str], node_params: dict[str, any]):
        try:
            for msg in data:
                self.ser.write(msg)
        except Exception as e:
            print("An error ocurred while sending data with UART protocol: ", e)

    def read(self):
        try:
            line = self.ser.readline()
            return line
        except TimeoutError:
            pass
        except Exception as e:
            print("An error occurred while receiving data:", e)