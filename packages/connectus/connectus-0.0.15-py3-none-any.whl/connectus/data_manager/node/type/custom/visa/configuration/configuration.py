from .layers import ConfigClient

class Configuration(ConfigClient):
    def __init__(self, node_config: dict[str, str]):
        ConfigClient.__init__(self, node_config)
        self.type = 'communication'
        self.id = 'visa'
        self.timeout = node_config.get('timeout')
        self.resource_name = node_config.get('resource_name')
        self.node_id = node_config.get('node_id')
        self.write_termination = node_config.get('write_termination')
        self.read_termination = node_config.get('read_termination')