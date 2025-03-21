from connectus.tools.structure.data import DataRequest, DataResponse
import asyncio

class DeviceManager():
    def __init__(self, stop_event: asyncio.Event, step_factor: float = 1.0):
        self.devices = []
        self.stop_event = stop_event
        self.step_factor = step_factor
    
    def add(self, device):
        try:
            item = {}
            item['name'] = device.id
            item['instance'] = device
            self.devices.append(item)
        except Exception as e:
            print('An error occurred adding a device: ', e)

    async def start(self):
        print('Device Manager is running')
        update_bundle = []
        for device in self.devices:
            update = asyncio.create_task(self._run_device(device['instance']))
            update_bundle.append(update)
        await asyncio.gather(*update_bundle)
    
    def get(self, request_list: list[DataRequest]) -> list[DataResponse]:
        try:
            data = []
            for request in request_list:
                request_dict = request.nested_model()
                if not request_dict['device_ids']:
                    for device in self.devices:
                        data += device['instance'].get([request])
                else:
                    for device_id in request_dict['device_ids']:
                        for device in self.devices:
                            if device['name'] == device_id:
                                data += device['instance'].get([request])
                                break
            return data
        except Exception as e:
            print('An error occurred during get request: ', e)
    
    def set(self, request_list: list[DataRequest]):
        try:
            for request in request_list:
                for device_id in request.device_ids:
                    device_found = False
                    for device in self.devices:
                        if device['name'] == device_id:
                            device['instance'].set([request])
                            device_found = True
                            break
                    if not device_found:
                        print(f'Warning: Device with id {device_id} does not exist')
                    
        except Exception as e:
            print('An error occurred during set request: ', e)

    async def _run_device(self, device):
        while not self.stop_event.is_set():
            await device.run()
            await asyncio.sleep(device.step_time*self.step_factor)

    async def stop(self):
        print('Device Manager is stopping')
        for device in self.devices:
            await device['instance'].stop()
        print('All devices stopped')