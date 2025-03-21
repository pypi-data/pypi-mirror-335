from .layers import ConfigClient, ConfigDataAccess

class Configuration(ConfigClient, ConfigDataAccess): ## optimize this
    def __init__(self, node_config: dict[str, str]):
        ConfigClient.__init__(self, node_config)
        ConfigDataAccess.__init__(self, node_config['data_location'])
        self.step_time = self.node_config['step_time']
        self.type = 'communication'
        self.id = 'opc'