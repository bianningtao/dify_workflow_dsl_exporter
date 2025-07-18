from typing import Optional, Dict, Any, List
from models.app import Workflow, EnvironmentVariable, WorkflowNode, WorkflowEdge
import uuid

from .config_service import config
from .database_connector import database_connector
from .api_connector import api_connector
from .manual_import_service import manual_import_service

class WorkflowService:
    # 模拟数据库存储（仅作为fallback）
    _workflows: Dict[str, Workflow] = {}
    
    def get_draft_workflow(self, app_id: str) -> Optional[Workflow]:
        """
        获取草稿工作流
        :param app_id: 应用ID
        :return: 工作流实例或None
        """
        # 根据配置选择数据源
        if config.is_database_enabled():
            return database_connector.get_workflow_by_app_id(app_id)
        elif config.is_api_enabled():
            return api_connector.get_workflow_by_app_id(app_id)
        elif config.is_manual_enabled():
            return manual_import_service.get_workflow_by_app_id(app_id)
        else:
            # 使用内存存储作为fallback
            return self._workflows.get(app_id)
    
    def create_default_workflow(self, app_id: str) -> Workflow:
        """
        创建默认工作流
        :param app_id: 应用ID
        :return: 工作流实例
        """
        workflow = Workflow(
            id=str(uuid.uuid4()),
            app_id=app_id,
            version="1.0",
            graph={
                "nodes": [
                    {
                        "id": "start",
                        "type": "start",
                        "data": {
                            "type": "start",
                            "title": "开始",
                            "variables": []
                        },
                        "position": {"x": 100, "y": 100}
                    },
                    {
                        "id": "llm",
                        "type": "llm",
                        "data": {
                            "type": "llm",
                            "title": "LLM",
                            "model": {
                                "provider": "openai",
                                "name": "gpt-3.5-turbo",
                                "mode": "chat",
                                "completion_params": {}
                            },
                            "prompt_template": [
                                {
                                    "role": "system",
                                    "text": "你是一个有用的AI助手。"
                                },
                                {
                                    "role": "user",
                                    "text": "{{input}}"
                                }
                            ]
                        },
                        "position": {"x": 300, "y": 100}
                    },
                    {
                        "id": "end",
                        "type": "end",
                        "data": {
                            "type": "end",
                            "title": "结束",
                            "outputs": {}
                        },
                        "position": {"x": 500, "y": 100}
                    }
                ],
                "edges": [
                    {
                        "id": "start-llm",
                        "source": "start",
                        "target": "llm",
                        "source_handle": "source",
                        "target_handle": "target"
                    },
                    {
                        "id": "llm-end",
                        "source": "llm",
                        "target": "end",
                        "source_handle": "source",
                        "target_handle": "target"
                    }
                ]
            },
            features={
                "file_upload": {
                    "image": {
                        "enabled": False,
                        "number_limits": 3,
                        "detail": "high",
                        "transfer_methods": ["remote_url", "local_file"]
                    }
                },
                "opening_statement": "",
                "suggested_questions": [],
                "suggested_questions_after_answer": {
                    "enabled": False
                },
                "speech_to_text": {
                    "enabled": False
                },
                "text_to_speech": {
                    "enabled": False
                },
                "citation": {
                    "enabled": False
                },
                "moderation": {
                    "enabled": False
                }
            },
            environment_variables=[
                EnvironmentVariable(
                    name="OPENAI_API_KEY",
                    value="sk-test-key",
                    value_type="secret"
                ),
                EnvironmentVariable(
                    name="SYSTEM_PROMPT",
                    value="你是一个有用的AI助手",
                    value_type="string"
                )
            ]
        )
        
        self._workflows[app_id] = workflow
        return workflow
    
    def save_workflow(self, workflow: Workflow) -> None:
        """
        保存工作流
        :param workflow: 工作流实例
        """
        self._workflows[workflow.app_id] = workflow
    
    def get_workflow_by_id(self, workflow_id: str) -> Optional[Workflow]:
        """
        根据ID获取工作流
        :param workflow_id: 工作流ID
        :return: 工作流实例或None
        """
        for workflow in self._workflows.values():
            if workflow.id == workflow_id:
                return workflow
        return None 