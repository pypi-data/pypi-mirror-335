import uuid
from typing import Dict, Any, Optional, List, Union

from .port import PortType, Port, InputPort, OutputPort


class PortsDict(Dict[str, Port]):
    """自定义字典类，用于管理节点的端口，并强制执行端口添加权限。"""

    def __init__(self, owner_node: "Node", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._owner_node = owner_node
        self._initializing = True  # 初始化标志

    def __setitem__(self, key: str, value: Port) -> None:
        # 初始化阶段或端口已存在时，允许直接添加/更新
        if self._initializing or key in self:
            super().__setitem__(key, value)
            return

        # 对于新端口，检查添加权限
        if isinstance(value, OutputPort) and not self._owner_node.can_add_output_ports:
            raise ValueError(
                f"Node<{self._owner_node.id}> '{self._owner_node.type}' does not allow adding output ports"
            )
        elif isinstance(value, InputPort) and not self._owner_node.can_add_input_ports:
            raise ValueError(
                f"Node<{self._owner_node.id}> '{self._owner_node.type}' does not allow adding input ports"
            )

        super().__setitem__(key, value)

    def finish_initialization(self):
        """结束初始化阶段"""
        self._initializing = False


class Node:
    def __init__(
        self,
        node_type: str,
        category: str,
        task_name: str,
        description: str = "",
        ports: Optional[Dict[str, Any]] = None,
        node_id: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        seleted_workflow_title: str = "",
        is_template: bool = False,
        initialized: bool = False,
        can_add_input_ports: bool = False,
        can_add_output_ports: bool = False,
    ) -> None:
        self.id: str = node_id or str(uuid.uuid4())
        self.type: str = node_type
        self.category: str = category
        self.task_name: str = task_name
        self.description: str = description
        self.can_add_input_ports: bool = can_add_input_ports
        self.can_add_output_ports: bool = can_add_output_ports
        # 初始化自定义PortsDict
        self.ports = PortsDict(self)
        # 如果提供了初始端口，将它们添加到字典中
        if ports:
            for name, port in ports.items():
                self.ports[name] = port
        # 结束初始化阶段
        self.ports.finish_initialization()

        self.position: Dict[str, float] = position or {"x": 0, "y": 0}
        self.seleted_workflow_title: str = seleted_workflow_title
        self.is_template: bool = is_template
        self.initialized: bool = initialized
        self.ignored: bool = False
        self.lock: bool = False
        self.shadow: bool = False

    def add_port(
        self,
        name: str,
        port_type: Union[PortType, str],
        show: bool = False,
        value: Any = None,
        options: Optional[List[Any]] = None,
        is_output: bool = False,
        **kwargs,
    ):
        if is_output:
            if not self.can_add_output_ports:
                raise ValueError(f"Node<{self.id}> '{self.type}' does not allow adding output ports")
            self.ports[name] = OutputPort(
                name=name, port_type=port_type, show=show, value=value, options=options, **kwargs
            )
        else:
            if not self.can_add_input_ports:
                raise ValueError(f"Node<{self.id}> '{self.type}' does not allow adding input ports")
            self.ports[name] = InputPort(
                name=name, port_type=port_type, show=show, value=value, options=options, **kwargs
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "data": {
                "task_name": self.task_name,
                "has_inputs": self.has_inputs(),
                "description": self.description,
                "seleted_workflow_title": self.seleted_workflow_title,
                "is_template": self.is_template,
                "template": {
                    port_name: port.to_dict()
                    for port_name, port in self.ports.items()
                    if port_name not in ["debug", "seleted_workflow_title", "is_template"]
                },
            },
            "category": self.category,
            "position": self.position,
            "initialized": self.initialized,
            "ignored": self.ignored,
            "lock": self.lock,
            "shadow": self.shadow,
        }

    def has_inputs(self) -> bool:
        for port in self.ports.values():
            if isinstance(port, InputPort):
                return True
        return False

    def has_port(self, port_name: str) -> bool:
        return port_name in self.ports

    def has_input_port(self, port_name: str) -> bool:
        return port_name in self.ports and isinstance(self.ports[port_name], InputPort)

    def has_output_port(self, port_name: str) -> bool:
        return port_name in self.ports and isinstance(self.ports[port_name], OutputPort)
