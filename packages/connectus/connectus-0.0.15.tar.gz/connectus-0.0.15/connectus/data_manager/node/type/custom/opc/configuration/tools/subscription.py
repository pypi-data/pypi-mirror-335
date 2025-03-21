from connectus.tools.structure.data import VariableData
from datetime import timezone

class SubscriptionHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    This class is just a sample class. Whatever class having these methods can be used
    """
    def __init__(self, changes_buffer):    
        self.buffer = changes_buffer  # To store updates

    def data_change(self, handle, node, value, attr):
        """
        Deprecated, use datachange_notification
        """
        pass

    def datachange_notification(self, node, value, data):
        """
        called for every datachange notification from server
        """
        item = VariableData(
            source= "opcua",
            name= node.nodeid.Identifier,
            value= value,
            timestamp= data.monitored_item.Value.SourceTimestamp.replace(tzinfo=timezone.utc),
            value_type= type(value).__name__,
        )

        self.buffer.append(item)

    def event_notification(self, event):
        """
        called for every event notification from server
        """
        pass

    def status_change_notification(self, status):
        """
        called for every status change notification from server
        """
        pass
