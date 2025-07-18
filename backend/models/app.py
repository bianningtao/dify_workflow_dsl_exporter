from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid

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
    
    def to_dict(self, include_secret: bool = False) -> Dict[str, Any]:
        workflow_dict = {
            "version": self.version,
            "graph": self.graph,
            "features": self.features,
            "environment_variables": []
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