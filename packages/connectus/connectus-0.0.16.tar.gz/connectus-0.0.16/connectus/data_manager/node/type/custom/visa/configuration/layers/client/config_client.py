import pyvisa

class ConfigClient:
    def __init__(self, node_config: dict[str, str]):
        self.node_config = node_config
        self.client = pyvisa.ResourceManager(r'C:\Windows\system32\visa64.dll')
    async def create_client(self):
        try:
            await self.__set_parameters()
        except Exception as e:
            print(f"An error occurred while creating VISA client: {e}")

    async def __set_parameters(self):
        try:
            self.device = self.client.open_resource(self.resource_name, timeout=self.timeout, write_termination = self.write_termination, read_termination = self.read_termination)
        except KeyError as e:
            print(f"Error: {e} is missing in VISA server parameters.")
        except Exception as e:
            print(f"An error occurred while setting VISA parameters: {e}")