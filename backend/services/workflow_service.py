from typing import Optional, Dict, Any, List
from models.app import Workflow, EnvironmentVariable, WorkflowNode, WorkflowEdge, App, AppMode
import uuid
import logging

from .config_service import config
from .user_config_service import user_config_service
from .database_connector import database_connector
from .api_connector import APIConnector


class WorkflowService:
    # 模拟数据库存储（仅作为fallback）
    _workflows: Dict[str, Workflow] = {}
    
    def __init__(self, user_id: Optional[str] = None):
        """
        初始化WorkflowService
        :param user_id: 用户ID，如果提供则使用用户配置
        """
        self.user_id = user_id
        self._user_api_connector = None
        
        if user_id:
            # 加载用户配置并创建专用的APIConnector
            user_config = user_config_service.get_full_user_config(user_id)
            logging.info(f"加载用户 {user_id} 的配置: {user_config is not None}")
            
            if user_config:
                logging.info(f"用户配置数据源: {user_config.get('data_source')}")
                if user_config.get('data_source') == 'api':
                    api_config = user_config.get('api', {})
                    logging.info(f"用户 API 配置: base_url={api_config.get('base_url')}, auth_type={api_config.get('auth', {}).get('type')}")
                    
                    self._user_api_connector = APIConnector()
                    # 使用用户配置初始化APIConnector
                    self._user_api_connector._init_with_user_config(user_config)
                    logging.info(f"用户 {user_id} 的 APIConnector 已创建")
            else:
                logging.warning(f"用户 {user_id} 没有配置数据")
    
    def _get_api_connector(self):
        """获取API连接器（优先使用用户的，否则使用全局的）"""
        if self._user_api_connector:
            return self._user_api_connector
        # Fallback to global connector
        from .api_connector import api_connector
        return api_connector
    
    def get_draft_workflow(self, app_id: str) -> Optional[Workflow]:
        """
        获取草稿工作流
        :param app_id: 应用ID
        :return: 工作流实例或None
        """
        # 根据配置选择数据源
        if config.is_database_enabled():
            return database_connector.get_workflow_by_app_id(app_id)
        elif config.is_api_enabled() or self._user_api_connector:
            return self._get_api_connector().get_workflow_by_app_id(app_id)
        else:
            # 使用内存存储作为fallback
            return self._workflows.get(app_id)
    
    def get_all_workflows(self) -> List[Workflow]:
        """
        获取所有工作流列表
        :return: 工作流列表
        """
        workflows = []
        
        # 根据配置选择数据源
        if config.is_database_enabled():
            workflows = database_connector.get_all_workflows()
        elif config.is_api_enabled() or self._user_api_connector:
            workflows = self._get_api_connector().get_all_workflows()
        else:
            # 使用内存存储作为fallback
            workflows = list(self._workflows.values())
        
        # 如果没有工作流，创建一些示例工作流用于演示
        if not workflows:
            sample_app_ids = ["demo-app-001", "demo-app-002", "demo-app-003"]
            for app_id in sample_app_ids:
                workflow = self.create_default_workflow(app_id)
                workflows.append(workflow)
        
        return workflows
    
    def get_or_create_app_model(self, app_id: str) -> App:
        """
        获取或创建应用模型
        :param app_id: 应用ID
        :return: 应用实例
        """
        # 根据配置选择数据源
        app_model = None
        if config.is_database_enabled():
            app_model = database_connector.get_app_by_id(app_id)
        elif config.is_api_enabled() or self._user_api_connector:
            app_model = self._get_api_connector().get_app_by_id(app_id)
        
        # 如果没有找到应用，尝试从工作流中获取应用信息
        if app_model is None:
            workflow = self.get_draft_workflow(app_id)
            if workflow and hasattr(workflow, 'app_name'):
                # 使用工作流中的应用信息创建App对象
                app_model = App(
                    id=app_id,
                    name=workflow.app_name,
                    mode=getattr(workflow, 'app_mode', AppMode.WORKFLOW.value),
                    icon="🚀",
                    icon_type="emoji",
                    icon_background="#E4FBCC",
                    description=getattr(workflow, 'app_description', ''),
                    use_icon_as_answer_icon=False,
                    tenant_id=str(uuid.uuid4())
                )
            else:
                # 如果还是没有找到，创建一个默认的
                logging.warning(f"无法获取应用 {app_id} 的信息，使用默认值")
                app_model = App(
                    id=app_id,
                    name=f"工作流应用 {app_id[:8]}",
                    mode=AppMode.WORKFLOW.value,
                    icon="🚀",
                    icon_type="emoji",
                    icon_background="#E4FBCC",
                    description="这是一个示例工作流应用",
                    use_icon_as_answer_icon=False,
                    tenant_id=str(uuid.uuid4())
                )
        
        return app_model
    
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
                            "outputs": []
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

    def clear_cache(self):
        """清除缓存，强制刷新数据"""
        if config.is_api_enabled() or self._user_api_connector:
            self._get_api_connector().clear_cache()
            logging.info("工作流服务缓存已清除")

    def get_workflows_paginated(self, page: int = 1, page_size: int = 20, search: str = "") -> dict:
        """
        分页获取工作流列表
        :param page: 页码（从1开始）
        :param page_size: 每页数量
        :param search: 搜索关键词
        :return: 包含工作流列表和总数的字典
        """
        # 根据配置选择数据源
        if config.is_database_enabled():
            return database_connector.get_workflows_paginated(page, page_size, search)
        elif config.is_api_enabled() or self._user_api_connector:
            return self._get_api_connector().get_workflows_paginated(page, page_size, search)
        else:
            # 使用内存存储作为fallback
            workflows = list(self._workflows.values())
            
            # 如果没有工作流，创建一些示例工作流
            if not workflows:
                sample_app_ids = ["demo-app-001", "demo-app-002", "demo-app-003"]
                for app_id in sample_app_ids:
                    workflow = self.create_default_workflow(app_id)
                    workflows.append(workflow)
            
            # 搜索过滤
            if search:
                workflows = [w for w in workflows if search.lower() in w.app_id.lower()]
            
            # 分页处理
            total = len(workflows)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_workflows = workflows[start:end]
            
            return {
                "workflows": paginated_workflows,
                "total": total
            } 