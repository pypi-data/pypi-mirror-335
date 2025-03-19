from enum import Enum
from typing import Optional, Any, Dict, List, Union


class PortType(Enum):
    TEXT = "text"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    SELECT = "select"
    RADIO = "radio"
    TEXTAREA = "textarea"
    INPUT = "input"
    FILE = "file"
    LIST = "list"
    COLOR = "color"
    TEMPERATURE = "temperature"


class Port:
    def __init__(
        self,
        name: str,
        port_type: Union[PortType, str],
        required: bool = True,
        show: bool = False,
        value: Any = None,
        options: Optional[List[Any]] = None,
        field_type: Optional[str] = None,
        is_output: bool = False,
        condition: Optional[str] = None,
        max_length: Optional[int] = None,
        support_file_types: Optional[List[str]] = None,
        multiple: Optional[bool] = None,
        group: Optional[str] = None,
        group_collpased: bool = False,
        has_tooltip: bool = False,
        max: Optional[Union[int, float]] = None,
        min: Optional[Union[int, float]] = None,
        max_count: Optional[int] = None,
        list: bool = False,
    ) -> None:
        self.name = name
        self.port_type = port_type
        self.required = required
        self.show = show
        self._value = value
        self.options = options
        self.field_type = field_type
        self.is_output = is_output
        self.condition = condition
        self.max_length = max_length
        self.support_file_types = support_file_types
        self.multiple = multiple
        self.group = group
        self.group_collpased = group_collpased
        self.has_tooltip = has_tooltip
        self.max = max
        self.min = min
        self.max_count = max_count
        self.list = list

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.name,
            "field_type": self.port_type.value if isinstance(self.port_type, PortType) else self.port_type,
            "required": self.required,
            "show": self.show,
            "value": self._value,
            "options": self.options,
            "type": self.field_type,
            "is_output": self.is_output,
            # "condition": f"(fieldsData) => {{ {self.condition} }}" if self.condition else "",
            "max_length": self.max_length,
            "support_file_types": ", ".join(self.support_file_types) if self.support_file_types else None,
            "multiple": self.multiple,
            "group": self.group,
            "group_collpased": self.group_collpased,
            "has_tooltip": self.has_tooltip,
            "max": self.max,
            "min": self.min,
            "list": self.list,
        }

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        if self.options:
            if value not in map(lambda x: x["value"], self.options):
                raise ValueError(f"Value `{value}` is not in Port `{self.name}` options {self.options}")
        self._value = value


class InputPort(Port):
    def __init__(
        self,
        name: str,
        port_type: Union[PortType, str],
        required: bool = True,
        show: bool = False,
        value: Any = None,
        options: Optional[List[Any]] = None,
        field_type: Optional[str] = None,
        condition: Optional[str] = None,
        max_length: Optional[int] = None,
        support_file_types: Optional[List[str]] = None,
        multiple: Optional[bool] = None,
        group: Optional[str] = None,
        group_collpased: bool = False,
        has_tooltip: bool = False,
        max: Optional[Union[int, float]] = None,
        min: Optional[Union[int, float]] = None,
        max_count: Optional[int] = None,
        list: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            port_type=port_type,
            required=required,
            show=show,
            value=value,
            options=options,
            field_type=field_type,
            is_output=False,
            condition=condition,
            max_length=max_length,
            support_file_types=support_file_types,
            multiple=multiple,
            group=group,
            group_collpased=group_collpased,
            has_tooltip=has_tooltip,
            max=max,
            min=min,
            max_count=max_count,
            list=list,
        )


class OutputPort(Port):
    def __init__(
        self,
        name: str = "output",
        port_type: Union[PortType, str] = PortType.TEXT,
        required: bool = True,
        show: bool = False,
        value: Any = None,
        options: Optional[List[Any]] = None,
        field_type: Optional[str] = None,
        condition: Optional[str] = None,
        max_length: Optional[int] = None,
        support_file_types: Optional[List[str]] = None,
        multiple: Optional[bool] = None,
        group: Optional[str] = None,
        group_collpased: bool = False,
        has_tooltip: bool = False,
        max: Optional[Union[int, float]] = None,
        min: Optional[Union[int, float]] = None,
        max_count: Optional[int] = None,
        list: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            port_type=port_type,
            required=required,
            show=show,
            value=value,
            options=options,
            field_type=field_type,
            is_output=True,
            condition=condition,
            max_length=max_length,
            support_file_types=support_file_types,
            multiple=multiple,
            group=group,
            group_collpased=group_collpased,
            has_tooltip=has_tooltip,
            max=max,
            min=min,
            max_count=max_count,
            list=list,
        )
