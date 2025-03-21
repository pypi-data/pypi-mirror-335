
class Configuration:
    def __init__(self, node_config: dict[str, str]):
        self.type = 'communication'
        self.id = 'udp'
        self.timeout = node_config['timeout']
        self.server_ip = node_config['ip']
        self.server_port = node_config['port']  # default server port
        self.node_id = node_config['node_id']