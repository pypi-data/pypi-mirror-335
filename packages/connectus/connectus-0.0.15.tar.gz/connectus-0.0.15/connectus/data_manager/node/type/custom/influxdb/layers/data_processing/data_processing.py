from influxdb_client import Point
from datetime import datetime

class DataProcessing:
    def __init__(self, node):
        self.node = node
        self.initial_time = str(datetime.now())

    def prepare_data(self, input_data: list[dict[str, any]]):
        ''' Convert the data to the correct format for the database'''
        output_data = []
        for measurement in input_data:
            point = Point(self.node.point_name)
            name = None
            value = None
            for name, value in measurement.items():
                if name == 'name':
                    name = value
                elif name == 'value':
                    value = value
                else:
                    point.tag(name, value)
            if name != None and value != None:
                point.field(name, value)
            else:
                raise ValueError('Field name or field value not found in the data')
            point.tag('experiment', self.node.experiment_name + ' ' + self.initial_time)
            output_data.append(point)
        return output_data