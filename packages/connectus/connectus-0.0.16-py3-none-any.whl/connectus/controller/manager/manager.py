import asyncio

class ControllerManager:
    def __init__(self, stop_event: asyncio.Event):
        self.controllers = []
        self.stop_event = stop_event

    def add(self, controller):
        try:
            item = {}
            item['id'] = controller.id
            item['instance'] = controller
            self.controllers.append(item)
        except Exception as e:
            print('An error occurred adding a controller: ', e)

    async def start(self): ## all controllers are started in parallel
        start_bundle = []
        for controller in self.controllers:
            start_task = asyncio.create_task(controller['instance'].start())
            start_bundle.append(start_task)
        if start_bundle:
            await asyncio.gather(*start_bundle)

    async def stop(self):
        for controller in self.controllers:
            await controller['instance'].stop()