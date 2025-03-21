from .devices import DeviceManager, DeviceCreator
from .data_manager import DataManager, NodeCreator
from .controller import ControllerManager, ControllerCreator
import asyncio

class Architecture:
    def __init__(self):
        self.devices: DeviceManager = None
        self.data_manager: DataManager = None
        self.controllers: ControllerManager = None
        self.is_running = None
        self.stop_event = None
        self.general_config = {}

    async def run(self):
        print("Architecture is running")
        self.is_running = await asyncio.create_task(self.__execute())

    async def __execute(self):
        try:
            await self.data_manager.start()
            await asyncio.gather(self.devices.start(), self.controllers.start())
        except Exception as e:
            await self.stop()
        
    async def stop(self):
        print("Architecture is stopping")
        await self.controllers.stop()
        self.stop_event.set()
        await self.devices.stop()
        await self.data_manager.stop()
        if self.is_running:
            await self.is_running

class ArchitectureBuilder:
    def __init__(self, general_config: dict[str, any], step_factor: float = 1):
        self.architecture = Architecture()
        self.architecture.general_config = general_config
        self.architecture.stop_event = asyncio.Event()
        self.architecture.data_manager = DataManager(self.architecture.stop_event)
        self.node_creator = NodeCreator(self.architecture.data_manager, self.architecture.stop_event)
        self.architecture.devices = DeviceManager(self.architecture.stop_event, step_factor)
        self.device_creator = DeviceCreator(self.architecture.devices, self.node_creator, self.architecture.general_config)
        self.architecture.controllers = ControllerManager(self.architecture.stop_event)
        self.controller_creator = ControllerCreator(self.architecture.controllers, self.architecture.devices, self.architecture.stop_event)

    def add_device(self, instance):
        self.device_creator.create(instance)

    def add_node(self, node_config: dict[str, str]):
        self.node_creator.create_node(node_config)

    def add_controller(self, instance):
        self.controller_creator.create(instance)

    def get_architecture(self):
        return self.architecture

