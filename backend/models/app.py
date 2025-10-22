from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
from datetime import datetime

class AppMode(Enum):
    ADVANCED_CHAT = "advanced-chat"
    WORKFLOW = "workflow"
    CHAT = "chat"
    COMPLETION = "completion"
    AGENT_CHAT = "agent-chat"

class App(BaseModel):
    id: str
    name: str
    mode: str
    icon: str = "🤖"
    icon_type: str = "emoji"
    icon_background: str = "#FFEAD5"
    description: str = ""
    use_icon_as_answer_icon: bool = False
    tenant_id: str = ""
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)

class EnvironmentVariable(BaseModel):
    name: str
    value: str
    value_type: str = "string"  # string, secret

class WorkflowNode(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]
    position: Dict[str, float]
    
class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    source_handle: str
    target_handle: str

class Workflow(BaseModel):
    id: str
    app_id: str
    version: str = "1.0"
    graph: Dict[str, Any]
    features: Dict[str, Any] = {}
    environment_variables: List[EnvironmentVariable] = []
    
    # 应用相关信息（可选字段）
    app_name: Optional[str] = None
    app_description: Optional[str] = None
    app_mode: Optional[str] = None
    
    def to_dict(self, include_secret: bool = False) -> Dict[str, Any]:
        workflow_dict = {
            "version": self.version,
            "graph": self.graph,
            "features": self.features,
            "environment_variables": []
        }
        
        # 添加工作流信息
        if self.app_name:
            workflow_dict["workflow_name"] = self.app_name
        if self.app_description:
            workflow_dict["workflow_description"] = self.app_description
        if self.app_mode:
            workflow_dict["workflow_mode"] = self.app_mode
        
        # 添加元数据信息
        workflow_dict["workflow_metadata"] = {
            "app_id": self.app_id,
            "workflow_id": self.id,
            "version": self.version,
            "export_time": datetime.now().isoformat()
        }
        
        # 过滤环境变量
        for env_var in self.environment_variables:
            if env_var.value_type == "secret" and not include_secret:
                continue
            workflow_dict["environment_variables"].append({
                "name": env_var.name,
                "value": env_var.value,
                "value_type": env_var.value_type
            })
        
        return workflow_dict
    
    def _normalize_graph_old(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """规范化graph结构，确保与Dify导入格式兼容"""
        if not graph:
            return {"nodes": [], "edges": [], "viewport": {"x": 0, "y": 0, "zoom": 1}}
        
        normalized = {
            "nodes": [],
            "edges": [],
            "viewport": graph.get("viewport", {"x": 0, "y": 0, "zoom": 1})
        }
        
        # 规范化节点数据
        for original_node in graph.get("nodes", []):
            # 创建节点副本以避免修改原数据
            node = original_node.copy()
            if "data" in node and isinstance(node["data"], dict):
                node["data"] = node["data"].copy()
            
            # 特殊处理：如果是advanced-chat模式且节点类型为end，转换为answer
            node_type = node.get("type", "")
            if node_type == "end" and self.app_mode == "advanced-chat":
                node_type = "answer"
                node["type"] = "answer"
                node["data"]["type"] = "answer"
                # answer节点需要有answer字段，用于指定输出内容
                if "answer" not in node["data"]:
                    # 尝试从outputs中提取，或使用默认值
                    outputs = node["data"].get("outputs", [])
                    if outputs and isinstance(outputs, list) and len(outputs) > 0:
                        # 如果有outputs，使用第一个output的value
                        node["data"]["answer"] = outputs[0].get("value", "{{#llm.text#}}")
                    else:
                        # 默认使用LLM的输出
                        node["data"]["answer"] = "{{#llm.text#}}"
                # 移除outputs字段（answer节点不需要）
                if "outputs" in node["data"]:
                    del node["data"]["outputs"]
            
            position = node.get("position", {"x": 0, "y": 0})
            
            normalized_node = {
                "id": node.get("id", ""),
                "type": "custom",  # Dify使用custom类型
                "position": position,
                "positionAbsolute": node.get("positionAbsolute", position),  # 添加绝对位置
                "sourcePosition": node.get("sourcePosition", "right"),  # 添加连接点位置
                "targetPosition": node.get("targetPosition", "left"),
            }
            
            # 添加节点尺寸（如果有的话）
            if "width" in node:
                normalized_node["width"] = node["width"]
            else:
                normalized_node["width"] = 244  # Dify默认宽度
            
            if "height" in node:
                normalized_node["height"] = node["height"]
            else:
                # 根据节点类型设置默认高度
                node_type = node.get("type", "")
                if node_type == "start":
                    normalized_node["height"] = 54
                elif node_type == "answer":
                    normalized_node["height"] = 105
                else:
                    normalized_node["height"] = 90
            
            # 确保data字段包含type
            node_data = node.get("data", {})
            if not isinstance(node_data, dict):
                node_data = {}
            
            # 确保data中有type字段（与节点类型一致）
            if "type" not in node_data:
                node_data["type"] = node.get("type", "")
            
            # 确保data中有title字段
            if "title" not in node_data:
                node_data["title"] = node.get("type", "Node")
            
            # 确保有desc字段
            if "desc" not in node_data:
                node_data["desc"] = ""
            
            # 确保有selected字段
            if "selected" not in node_data:
                node_data["selected"] = False
            
            normalized_node["data"] = node_data
            
            # 添加selected字段（外层）
            if "selected" in node:
                normalized_node["selected"] = node["selected"]
            else:
                normalized_node["selected"] = False
            
            normalized["nodes"].append(normalized_node)
        
        # 规范化边数据
        for edge in graph.get("edges", []):
            normalized_edge = {
                "id": edge.get("id", ""),
                "source": edge.get("source", ""),
                "target": edge.get("target", ""),
                "sourceHandle": edge.get("sourceHandle", "source"),
                "targetHandle": edge.get("targetHandle", "target"),
                "type": "custom",  # Dify使用custom类型
            }
            
            # 添加data字段
            edge_data = edge.get("data", {})
            if not isinstance(edge_data, dict):
                edge_data = {}
            
            # 添加sourceType和targetType（从规范化后的节点获取）
            if "sourceType" not in edge_data:
                # 从规范化后的节点列表中查找
                source_node = next((n for n in normalized["nodes"] if n.get("id") == edge.get("source")), None)
                if source_node:
                    # 使用data中的真实类型（已经考虑了end->answer的转换）
                    edge_data["sourceType"] = source_node.get("data", {}).get("type", "")
            
            if "targetType" not in edge_data:
                target_node = next((n for n in normalized["nodes"] if n.get("id") == edge.get("target")), None)
                if target_node:
                    # 使用data中的真实类型（已经考虑了end->answer的转换）
                    edge_data["targetType"] = target_node.get("data", {}).get("type", "")
            
            # 添加isInLoop字段
            if "isInLoop" not in edge_data:
                edge_data["isInLoop"] = False
            
            normalized_edge["data"] = edge_data
            
            # 添加zIndex
            if "zIndex" in edge:
                normalized_edge["zIndex"] = edge["zIndex"]
            else:
                normalized_edge["zIndex"] = 0
            
            normalized["edges"].append(normalized_edge)
        
        return normalized 