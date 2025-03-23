import json
from typing import List, Union, Dict, Any, Optional

from .node import Node
from .edge import Edge
from ..utils.layout import layout
from ..utils.check import WorkflowCheckResult, check_dag, check_ui


class Workflow:
    def __init__(self) -> None:
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []

    def add_node(self, node: Node):
        self.nodes.append(node)

    def add_nodes(self, nodes: List[Node]):
        self.nodes.extend(nodes)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def connect(
        self,
        source_node: Union[str, Node],
        source_port: str,
        target_node: Union[str, Node],
        target_port: str,
    ):
        # 获取源节点ID
        if isinstance(source_node, Node):
            source_node_id = source_node.id
        else:
            source_node_id = source_node

        # 获取目标节点ID
        if isinstance(target_node, Node):
            target_node_id = target_node.id
        else:
            target_node_id = target_node

        # 检查源节点是否存在
        source_node_exists = any(node.id == source_node_id for node in self.nodes)
        if not source_node_exists:
            raise ValueError(f"Source node not found: {source_node_id}")

        # 检查目标节点是否存在
        target_node_exists = any(node.id == target_node_id for node in self.nodes)
        if not target_node_exists:
            raise ValueError(f"Target node not found: {target_node_id}")

        # 检查源节点的端口是否存在
        source_node_obj = next(node for node in self.nodes if node.id == source_node_id)
        if not source_node_obj.has_output_port(source_port):
            raise ValueError(f"Source node {source_node_id} has no output port: {source_port}")

        # 检查目标节点的端口是否存在
        target_node_obj = next(node for node in self.nodes if node.id == target_node_id)
        if not target_node_obj.has_input_port(target_port):
            raise ValueError(f"Target node {target_node_id} has no input port: {target_port}")

        # 检查目标端口是否已有被连接的线
        for edge in self.edges:
            if edge.target == target_node_id and edge.target_handle == target_port:
                raise ValueError(
                    f"The input port {target_port} of the target node {target_node_id} is already connected: {edge.source}({edge.source_handle}) → {edge.target}({edge.target_handle})"
                )

        # 创建并添加边
        edge_id = f"vueflow__edge-{source_node_id}{source_port}-{target_node_id}{target_port}"
        edge = Edge(edge_id, source_node_id, source_port, target_node_id, target_port)
        self.add_edge(edge)

    def to_dict(self):
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "viewport": {"x": 0, "y": 0, "zoom": 1},
        }

    def to_json(self, ensure_ascii=False):
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)

    def to_mermaid(self) -> str:
        """生成 Mermaid 格式的流程图。

        Returns:
            str: Mermaid 格式的流程图文本
        """
        lines = ["flowchart TD"]

        # 创建节点类型到序号的映射
        type_counters = {}
        node_id_to_label = {}

        # 首先为所有节点生成标签
        for node in self.nodes:
            node_type = node.type.lower()
            if node_type not in type_counters:
                type_counters[node_type] = 0
            node_label = f"{node_type}_{type_counters[node_type]}"
            node_id_to_label[node.id] = node_label
            type_counters[node_type] += 1

        # 添加节点定义
        for node in self.nodes:
            node_label = node_id_to_label[node.id]
            lines.append(f'    {node_label}["{node_label} ({node.type})"]')

        lines.append("")  # 添加一个空行分隔节点和边的定义

        # 添加边的定义
        for edge in self.edges:
            source_label = node_id_to_label[edge.source]
            target_label = node_id_to_label[edge.target]
            label = f"{edge.source_handle} → {edge.target_handle}"
            lines.append(f"    {source_label} -->|{label}| {target_label}")

        return "\n".join(lines)

    def check(self) -> WorkflowCheckResult:
        """检查流程图的有效性。

        Returns:
            WorkflowCheckResult: 包含各种检查结果的字典
        """
        dag_check = check_dag(self)  # 检查流程图是否为有向无环图，并检测是否存在孤立节点。
        ui_check = check_ui(self)

        # 合并结果
        result = dag_check
        result["ui_warnings"] = ui_check

        return result

    def layout(self, options: Optional[Dict[str, Any]] = None) -> "Workflow":
        """对工作流中的节点进行自动布局，计算并更新每个节点的位置。

        此方法实现了一个简单的分层布局算法，将节点按照有向图的拓扑结构进行排列。

        Args:
            options: 布局选项，包括:
                - direction: 布局方向 ('TB', 'BT', 'LR', 'RL')，默认 'LR'
                - node_spacing: 同一层级节点间的间距，默认 500
                - layer_spacing: 不同层级间的间距，默认 400
                - margin_x: 图形左右边距，默认 20
                - margin_y: 图形上下边距，默认 20

        Returns:
            布局后的工作流对象
        """
        layout(self.nodes, self.edges, options)
        return self
