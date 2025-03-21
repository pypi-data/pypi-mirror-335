import json
from typing import List, Union, TypedDict

from .node import Node
from .edge import Edge
from .port import InputPort


class UIWarning(TypedDict, total=False):
    """UI警告类型。"""

    input_ports_shown_but_connected: list[dict]  # 显示的输入端口但被连接
    has_shown_input_ports: bool  # 是否存在显示的输入端口
    has_output_nodes: bool  # 是否存在输出节点


class WorkflowCheckResult(TypedDict, total=False):
    """工作流检查结果类型。"""

    no_cycle: bool  # 工作流是否不包含环
    no_isolated_nodes: bool  # 工作流是否不包含孤立节点
    ui_warnings: UIWarning  # UI相关警告


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

    def _check_dag(self) -> WorkflowCheckResult:
        """检查流程图是否为有向无环图，并检测是否存在孤立节点。

        Returns:
            WorkflowCheckResult: 包含检查结果的字典
                - no_cycle (bool): 如果流程图是有向无环图返回 True，否则返回 False
                - no_isolated_nodes (bool): 如果不存在孤立节点返回 True，否则返回 False
        """
        result: WorkflowCheckResult = {"no_cycle": True, "no_isolated_nodes": True}

        # 过滤掉触发器节点和辅助节点
        trigger_nodes = [
            node.id
            for node in self.nodes
            if hasattr(node, "category") and (node.category == "triggers" or node.category == "assistedNodes")
        ]

        # 获取需要检查的节点和边
        regular_nodes = [node.id for node in self.nodes if node.id not in trigger_nodes]
        regular_edges = [
            edge for edge in self.edges if edge.source not in trigger_nodes and edge.target not in trigger_nodes
        ]

        # ---------- 检查有向图是否有环 ----------
        # 构建邻接表
        adjacency = {node_id: [] for node_id in regular_nodes}
        for edge in regular_edges:
            if edge.source in adjacency:  # 确保节点在字典中
                adjacency[edge.source].append(edge.target)

        # 三种状态: 0 = 未访问, 1 = 正在访问, 2 = 已访问完成
        visited = {node_id: 0 for node_id in regular_nodes}

        def dfs_cycle_detection(node_id):
            # 如果节点正在被访问，说明找到了环
            if visited[node_id] == 1:
                return False

            # 如果节点已经访问完成，无需再次访问
            if visited[node_id] == 2:
                return True

            # 标记为正在访问
            visited[node_id] = 1

            # 访问所有邻居
            for neighbor in adjacency[node_id]:
                if neighbor in visited and not dfs_cycle_detection(neighbor):
                    return False

            # 标记为已访问完成
            visited[node_id] = 2
            return True

        # 对每个未访问的节点进行 DFS 检测环
        for node_id in regular_nodes:
            if visited[node_id] == 0:
                if not dfs_cycle_detection(node_id):
                    result["no_cycle"] = False
                    break

        # ---------- 检查是否存在孤立节点 ----------
        # 构建无向图邻接表
        undirected_adjacency = {node_id: [] for node_id in regular_nodes}
        for edge in regular_edges:
            if edge.source in undirected_adjacency and edge.target in undirected_adjacency:
                undirected_adjacency[edge.source].append(edge.target)
                undirected_adjacency[edge.target].append(edge.source)

        # 深度优先搜索来检测连通分量
        undirected_visited = set()

        def dfs_connected_components(node_id):
            undirected_visited.add(node_id)
            for neighbor in undirected_adjacency[node_id]:
                if neighbor not in undirected_visited:
                    dfs_connected_components(neighbor)

        # 计算连通分量数量
        connected_components_count = 0
        for node_id in regular_nodes:
            if node_id not in undirected_visited:
                connected_components_count += 1
                dfs_connected_components(node_id)

        # 如果连通分量数量大于1，说明存在孤立节点
        if connected_components_count > 1 and len(regular_nodes) > 0:
            result["no_isolated_nodes"] = False

        return result

    def _check_ui(self) -> UIWarning:
        """
        检查工作流的 UI 情况。
        以下情况会警告：
        1. 某个输入端口的 show=True，但是又有连线连接到该端口（实际运行时会被覆盖）。
        2. 整个工作流没有任何输入端口是 show=True 的，说明没有让用户输入的地方。
        3. 整个工作流没有任何输出节点，这样工作流结果无法呈现。
        """
        warnings: UIWarning = {
            "input_ports_shown_but_connected": [],
            "has_shown_input_ports": False,
            "has_output_nodes": False,
        }

        # 检查是否有任何显示的输入端口
        has_shown_input_ports = False

        # 找出所有连接的目标端口
        connected_ports = {(edge.target, edge.target_handle) for edge in self.edges}

        # 遍历所有节点
        for node in self.nodes:
            # 检查是否为输出节点
            if hasattr(node, "category") and node.category == "outputs":
                warnings["has_output_nodes"] = True

            # 检查节点的输入端口
            for port_name in node.ports.keys() if hasattr(node, "ports") else []:
                port = node.ports.get(port_name)
                # 确保是输入端口且设置为显示
                if hasattr(port, "show") and getattr(port, "show", False) and isinstance(port, InputPort):
                    has_shown_input_ports = True

                    # 检查显示的端口是否也被连接
                    if (node.id, port_name) in connected_ports:
                        warnings["input_ports_shown_but_connected"].append(
                            {"node_id": node.id, "node_type": node.type, "port_name": port_name}
                        )

        # 如果没有任何显示的输入端口
        warnings["has_shown_input_ports"] = has_shown_input_ports

        return warnings

    def check(self) -> WorkflowCheckResult:
        """检查流程图的有效性。

        Returns:
            WorkflowCheckResult: 包含各种检查结果的字典
        """
        dag_check = self._check_dag()
        ui_check = self._check_ui()

        # 合并结果
        result: WorkflowCheckResult = dag_check
        result["ui_warnings"] = ui_check

        return result
