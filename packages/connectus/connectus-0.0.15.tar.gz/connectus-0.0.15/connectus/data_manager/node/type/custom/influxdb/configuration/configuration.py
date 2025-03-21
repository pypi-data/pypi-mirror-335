from ..layers import DataProcessing

class Configuration:
    def __init__(self, node_config: dict[str, any]):
        self.type = 'database'
        self.id = 'influxdb'
        self.url = node_config['url']
        self.token = node_config['token']
        self.org = node_config['org']
        self.bucket  = node_config['bucket']
        self.point_name = node_config['point_name']
        self.experiment_name = node_config['experiment_name']
        self.__set_layers()

    def __set_layers(self):
        self.data_processing = DataProcessing(self)