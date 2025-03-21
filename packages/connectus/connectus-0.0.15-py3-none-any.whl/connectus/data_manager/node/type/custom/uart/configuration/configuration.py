
class Configuration:
    def __init__(self, node_config: dict[str, str]):
        self.type = 'communication'
        self.id = 'uart'
        self.port = node_config['port']
        self.baudrate = node_config['baudrate']
        self.bytesize = node_config['bytesize']
        self.parity = node_config['parity']
        self.stopbits = node_config['stopbits']
        self.timeout = node_config['timeout'] ## We must use it ?
        self.addr = self.port