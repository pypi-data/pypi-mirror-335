import asyncua as opc

class ConfigClient:
    def __init__(self, node_config: dict[str, str]):
        self.node_config = node_config
        self.client = opc.Client(url=node_config['url'], timeout=int(self.node_config['timeout']))  # Initialize with the URL
        self.certificate_path = None
        self.private_key_path = None

    async def create_client(self):
        try:
            await self.__set_parameters()
            await self.client.connect()
        except Exception as e:
            print(f"An error occurred while creating OPC client: {e}")

    async def __set_parameters(self):
        try:
            self.client.application_uri = self.node_config['app_uri']
            self.client.set_user(self.node_config.get('user', ""))
            self.client.set_password(self.node_config.get('password', ""))
            await self.client.set_security_string(
                f"{self.node_config['policy']},"
                f"{self.node_config['mode']},"
                f"{self.node_config.get('certificate', '')},"
                f"{self.node_config.get('private_key', '')}"
            )
        except KeyError as e:
            print(f"Error: {e} is missing in OPC server parameters.")
        except Exception as e:
            print(f"An error occurred while setting OPC parameters: {e}")