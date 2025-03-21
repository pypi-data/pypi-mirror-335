from asyncua import ua

class ConfigDataAccess:
    def __init__(self, data_location: dict[str, any]):
        self.data_location = data_location
        self.devices = {}

    async def set_data_location(self):
        try:
            for device, folder in self.data_location.items():
                await self.add_device(device, folder)
        except Exception as e:
            print(f"An error occurred while setting the data location: {e}")

    async def add_device(self, device: str, folder: str):
        try:
            self.device_data = {
                'node': None,
                'folder': {
                    'node': None,
                    'variables': []
                }
            }
            self.device_data['node'] = await self.__search_node(self.client.get_objects_node(), device)
            self.device_data['folder']['node'] = await self.__search_node(self.device_data['node'], folder)
            self.devices[device] = self.device_data
            await self.__get_variables(self.device_data['folder']['node'])
        except Exception as e:
            print(f"An error occurred while adding the device: {e}")

    async def __get_variables(self, node):
        try:
            
            children_nodes = await node.get_children()
            for child_node in children_nodes:
                    node_class = await child_node.read_node_class()
                    if node_class == ua.NodeClass.Variable:
                        self.device_data['folder']['variables'].append({
                            'name': child_node.nodeid.Identifier,
                            'instance': child_node
                        })
                    else:
                        await self.__get_variables(child_node)
        except Exception as e:
            print(f"An error occurred while getting the variables: {e}")

    async def __search_node(self, node, child_name: str):
        try:
            children_nodes = await node.get_children()
            for child_node in children_nodes:
                if child_node.nodeid.Identifier == child_name:
                    return child_node
            raise Exception(f"Node {child_name} not found")
        except Exception as e:
            print(f"An error occurred while searching the node: {e}")