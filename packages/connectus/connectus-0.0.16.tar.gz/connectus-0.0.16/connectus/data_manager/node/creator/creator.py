from ..type.custom import UART, UDP, InfluxDB, OPC, TimeScaleDB, VISA
import asyncio

class NodeCreator:
    def __init__(self, data_manager, stop_event: asyncio.Event):
        self.stop_event = stop_event
        self.data_manager = data_manager
        self.id = 0

    def create_node(self, node_config: dict[str, str]):
        node_config['id'] = self.id
        name = node_config['name']
        if name == 'uart':
            node = UART(node_config, self.stop_event)
        elif name == 'udp':
            node = UDP(node_config, self.stop_event)
        # elif name == 'influxdb':
        #     node = InfluxDB(node_config, self.stop_event)
        elif name == 'opc':
            node = OPC(node_config, self.stop_event)
        elif name == 'timescaledb':
            node = TimeScaleDB(node_config, self.stop_event)
        elif name == 'visa':
            node = VISA(node_config, self.stop_event)
        else:
            raise ValueError(f"Node type {name} not supported")
        self.data_manager.add(node)
        self.id += 1
        return node