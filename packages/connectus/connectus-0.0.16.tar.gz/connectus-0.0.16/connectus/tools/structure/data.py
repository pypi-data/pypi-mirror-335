from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

@dataclass
class CommandData:
    variable_name: str = field(metadata={"description": "The name of the variable"})
    method: callable = field(metadata={"description": "The method to be executed"})

    def nested_model(self) -> Dict[str, Dict[str, Any]]:
        """Converts the dataclass instance to a nested dictionary."""
        data = {self.variable_name: {"method": self.method}}
        return data

@dataclass
class CommandCollection:
    collection: List[CommandData] = field(default_factory=list)

    def _deep_update(self, source, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and key in source:
                self._deep_update(source[key], value)
            else:
                source[key] = value

    def _update_if_exists(self, data: CommandData):
        for existing_data in self.collection:
            if existing_data.variable_name == data.variable_name:
                self.collection.remove(existing_data)
                break
        self.collection.append(data)

    def update(self, data: Union[CommandData, 'CommandCollection']):
        """Adds a CommandData instance to the collection."""
        if isinstance(data, CommandData):
            self._update_if_exists(data)
        elif isinstance(data, CommandCollection):
            for new_data in data.collection:
                self._update_if_exists(new_data)

    def nested_model(self) -> Dict[str, Dict[str, Any]]:
        output = {}
        for data in self.collection:
            self._deep_update(output, data.nested_model())
        return output

@dataclass
class VariableData:
    source: str = field(metadata={"description": "Source identifier"})
    name: str = field(metadata={"description": "The name of the variable"})
    value: Optional[float] = field(default=None, metadata={"description": "The value of the variable"})
    timestamp: datetime = field(
        default_factory=datetime.now,
        metadata={"description": "Timestamp when the data was recorded"}
    )
    value_type: Optional[Any] = field(default=None, metadata={"description": "Type of the data value"})
    experiment_id: Optional[str] = field(default=None, metadata={"description": "Experiment identifier"})
    unit: Optional[str] = field(default=None, metadata={"description": "Unit of the data value, if applicable"})
    additional_info: Optional[Dict[str, Any]] = field(
        default_factory=dict, metadata={"description": "Additional optional information"}
    )

    def __post_init__(self):
        if self.value_type is None and self.value is not None:
            self.value_type = type(self.value).__name__

    def nested_model(self) -> Dict[str, Any]:
        """Converts the dataclass instance to a nested dictionary."""
        data = {
            self.source: {
                self.name: {
                    "timestamp": self.timestamp,
                    "additional_info": self.additional_info,
                }
            }
        }
        if self.value is not None:
            data[self.source][self.name]["value"] = self.value
        if self.experiment_id is not None:
            data[self.source][self.name]["experiment_id"] = self.experiment_id
        if self.unit is not None:
            data[self.source][self.name]["unit"] = self.unit
        if self.value_type is not None:
            data[self.source][self.name]["value_type"] = self.value_type
        return data
    
    def plain_model(self) -> Dict[str, Any]:
        """Converts the dataclass instance to a nested dictionary."""
        data = {
            "source": self.source,
            "name": self.name,
            "timestamp": self.timestamp,
            "additional_info": self.additional_info,
        }
        if self.value is not None:
            data["value"] = self.value
        if self.experiment_id is not None:
            data["experiment_id"] = self.experiment_id
        if self.unit is not None:
            data["unit"] = self.unit
        if self.value_type is not None:
            data["value_type"] = self.value_type
        return data

@dataclass
class DataCollection:
    collection: List[VariableData] = field(default_factory=list)

    def _deep_update(self, source, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and key in source:
                self._deep_update(source[key], value)
            else:
                source[key] = value

    def _update_if_exists(self, data: VariableData):
        for existing_data in self.collection:
            if existing_data.source == data.source and existing_data.name == data.name:
                self.collection.remove(existing_data)
                break
        self.collection.append(data)

    def update(self, data: Union[VariableData, 'DataCollection']):
        """Adds a VariableData instance to the collection."""
        if isinstance(data, VariableData):
            self._update_if_exists(data)
        elif isinstance(data, DataCollection):
            for new_data in data.collection:
                self._update_if_exists(new_data)

    def nested_model(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        output = {}
        for data in self.collection:
            self._deep_update(output, data.nested_model())
        return output
    
    def plain_model(self) -> List[Dict[str, Any]]:
        output = []
        for data in self.collection:
            output.append(data.plain_model())
        return output

@dataclass
class BaseExchange:
    device_ids: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class DataRequest(BaseExchange):
    action: str = field(default_factory=str, metadata={"description": "The action to be performed"})
    data: Optional [DataCollection] = field(default=None)

    def nested_model(self) -> Dict[str, Any]:
        """Converts the dataclass instance to a dictionary."""
        data = {
            "action": self.action,
            "device_ids": self.device_ids,
            "timestamp": self.timestamp,
            "data": self.data,
        }
        return data

@dataclass
class DataResponse(BaseExchange):
    response: str = field(default_factory=str, metadata={"description": "The response to the request"})
    data: Optional[DataCollection] = field(default=None)
    error_message: Optional[str] = field(default=None)

    def nested_model(self) -> Dict[str, Any]:
        """Converts the dataclass instance to a dictionary."""
        data = {
            "response": self.response,
            "device_ids": self.device_ids,
            "timestamp": self.timestamp,
            "data": self.data,
            "error_message": self.error_message,
        }
        return data
