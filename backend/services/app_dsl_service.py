import yaml
from typing import Dict, Any
from models.app import App, AppMode, Workflow
from services.workflow_service import WorkflowService

CURRENT_DSL_VERSION = "1.0"

class AppDslService:
    @classmethod
    def export_dsl(cls, app_model: App, include_secret: bool = False) -> str:
        """
        导出应用程序DSL
        :param app_model: App实例
        :param include_secret: 是否包含secret变量
        :return: YAML格式的DSL字符串
        """
        app_mode = AppMode(app_model.mode)
        
        export_data = {
            "version": CURRENT_DSL_VERSION,
            "kind": "app",
            "app": {
                "name": app_model.name,
                "mode": app_model.mode,
                "icon": "🤖" if app_model.icon_type == "image" else app_model.icon,
                "icon_background": "#FFEAD5" if app_model.icon_type == "image" else app_model.icon_background,
                "description": app_model.description,
                "use_icon_as_answer_icon": app_model.use_icon_as_answer_icon,
            },
        }
        
        if app_mode in {AppMode.ADVANCED_CHAT, AppMode.WORKFLOW}:
            cls._append_workflow_export_data(
                export_data=export_data, app_model=app_model, include_secret=include_secret
            )
        else:
            cls._append_model_config_export_data(export_data, app_model)
        
        return yaml.dump(export_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def _append_workflow_export_data(cls, *, export_data: Dict[str, Any], app_model: App, include_secret: bool) -> None:
        """
        附加工作流导出数据
        :param export_data: 导出数据
        :param app_model: App实例
        :param include_secret: 是否包含secret变量
        """
        workflow_service = WorkflowService()
        workflow = workflow_service.get_draft_workflow(app_model.id)
        
        if not workflow:
            # 如果没有找到工作流，创建一个默认的
            workflow = workflow_service.create_default_workflow(app_model.id)
        
        workflow_dict = workflow.to_dict(include_secret=include_secret)
        
        # 处理知识检索节点的数据集ID加密（简化版）
        for node in workflow_dict.get("graph", {}).get("nodes", []):
            if node.get("data", {}).get("type", "") == "knowledge-retrieval":
                dataset_ids = node["data"].get("dataset_ids", [])
                # 这里可以添加数据集ID加密逻辑
                node["data"]["dataset_ids"] = dataset_ids
        
        export_data["workflow"] = workflow_dict
        
        # 简化版依赖关系
        export_data["dependencies"] = []
    
    @classmethod
    def _append_model_config_export_data(cls, export_data: Dict[str, Any], app_model: App) -> None:
        """
        附加模型配置导出数据（简化版）
        :param export_data: 导出数据
        :param app_model: App实例
        """
        export_data["model_config"] = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "mode": "chat",
            "configs": {}
        } 