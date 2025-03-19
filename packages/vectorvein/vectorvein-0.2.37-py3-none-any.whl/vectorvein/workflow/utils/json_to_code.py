import sys
import json
import importlib
from pathlib import Path
from typing import Optional, Union


def _get_workflow_package_path():
    """
    获取workflow包的根路径

    Returns:
        workflow包的根路径
    """
    # 获取当前文件的绝对路径
    current_file = Path(__file__).resolve()
    # workflow包的根路径应该是 workflow 目录的父目录
    package_root = current_file.parent.parent.parent
    return str(package_root)


def _safe_import_node_class(category: str, node_type: str):
    """
    安全地动态导入节点类

    Args:
        category: 节点类别
        node_type: 节点类型

    Returns:
        导入的类或None
    """
    try:
        # 确保workflow包路径在sys.path中
        package_root = _get_workflow_package_path()
        if package_root not in sys.path:
            sys.path.insert(0, package_root)

        module = importlib.import_module(f"vectorvein.workflow.nodes.{category}")
        return getattr(module, node_type)
    except (ImportError, AttributeError) as e:
        print(f"Warning: Failed to import {node_type} from {category}: {e}")
        return None


def to_python_str(value):
    if isinstance(value, str):
        # 使用repr()来正确处理字符串的转义
        return repr(value)
    return value


def generate_python_code(
    json_str: Optional[str] = None,
    json_file: Optional[Union[str, Path]] = None,
    skip_trigger: bool = True,
    skip_import: bool = False,
) -> str:
    """
    将工作流JSON文件转换为Python代码

    Args:
        json_str: JSON字符串
        json_file: JSON文件路径
        skip_trigger: 是否跳过触发器节点
        skip_import: 是否跳过导入语句


    Returns:
        生成的Python代码字符串
    """
    # 读取JSON文件
    if json_file:
        with open(json_file, "r", encoding="utf8") as f:
            workflow_data = json.load(f)
    elif json_str:
        workflow_data = json.loads(json_str)
    else:
        raise ValueError("json_file or json_str must be provided")

    code = []
    if not skip_import:
        code.append("from vectorvein.workflow.graph.workflow import Workflow")

    # 收集需要导入的节点类
    node_imports = set()
    node_instances = {}

    # 解析节点并生成导入语句
    for node in workflow_data["nodes"]:
        node_type = node["type"]
        category = node["category"]
        if skip_trigger and category == "triggers":
            continue

        if category == "assistedNodes":
            continue

        category, task_name = node["data"]["task_name"].split(".")

        # 动态导入节点类
        NodeClass = _safe_import_node_class(category, node_type)
        if NodeClass is None:
            continue

        node_imports.add(f"from vectorvein.workflow.nodes.{category} import {node_type}")

        # 创建节点实例以获取默认值
        node_instance = NodeClass()

        add_ports = []
        show_ports = []
        values = []
        for port_name, port in node["data"]["template"].items():
            if port_name not in node_instance.ports:
                add_ports.append(port)
                continue

            if port["show"]:
                show_ports.append(port["name"])

            # 比较端口值与默认值
            port_value = port["value"]
            default_value = node_instance.ports[port_name].value if port_name in node_instance.ports else None

            if port_value and port_value != default_value:
                values.append(port)

        node_instances[node["id"]] = {
            "var_name": f"{task_name}_{len(node_instances)}",
            "type": node_type,
            "show_ports": show_ports,
            "values": values,
            "add_ports": add_ports,
        }

    # 添加导入语句
    if not skip_import:
        code.extend(sorted(list(node_imports)))
        code.append("")

    # 生成节点实例化代码
    for info in node_instances.values():
        code.append(f"{info['var_name']} = {info['type']}()")

    code.append("")
    code.append("workflow = Workflow()")

    # 添加节点到工作流
    node_list = [f"    {info['var_name']}," for info in node_instances.values()]
    code.append(f"workflow.add_nodes([\n{'\n'.join(node_list)}\n])")

    code.append("")
    for info in node_instances.values():
        for port in info["add_ports"]:
            params = [
                f"name={to_python_str(port['name'])}",
                f"port_type={to_python_str(port['field_type'])}",
                f"value={to_python_str(port['value'])}",
            ]
            if port.get("show"):
                params.append(f"show={port['show']}")
            if port.get("options"):
                params.append(f"options={port['options']}")
            if port.get("is_output"):
                params.append(f"is_output={bool(port['is_output'])}")
            code.append(f"{info['var_name']}.add_port({', '.join(params)})")

        for port_name in info["show_ports"]:
            code.append(f"{info['var_name']}.ports['{port_name}'].show = True")

        for port in info["values"]:
            code.append(f"{info['var_name']}.ports['{port['name']}'].value = {to_python_str(port['value'])}")

    code.append("")

    # 生成边的连接代码
    for edge in workflow_data["edges"]:
        source_var = node_instances[edge["source"]]["var_name"]
        target_var = node_instances[edge["target"]]["var_name"]
        source_handle = edge["sourceHandle"]
        target_handle = edge["targetHandle"]
        code.append(f'workflow.connect({source_var}, "{source_handle}", {target_var}, "{target_handle}")')

    return "\n".join(code)
