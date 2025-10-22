'''
Author: bianningtao ab2961513324@163.com
Date: 2025-10-22 11:28:35
LastEditors: bianningtao ab2961513324@163.com
LastEditTime: 2025-10-22 11:29:06
FilePath: /dify_workflow_dsl_exporter/backend/services/app_dsl_service.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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
        
        # 处理节点兼容性
        graph = workflow_dict.get("graph", {})
        nodes = graph.get("nodes", [])
        
        # 如果是advanced-chat模式，需要将end节点转换为answer节点
        if app_model.mode == "advanced-chat":
            for node in nodes:
                if node.get("type") == "end":
                    # 转换为answer节点
                    node["type"] = "answer"
                    if "data" in node:
                        node["data"]["type"] = "answer"
                        # answer节点需要answer字段指定输出内容
                        if "answer" not in node["data"]:
                            # 默认使用LLM的输出
                            node["data"]["answer"] = "{{#llm.text#}}"
                        # 移除outputs字段（answer节点不需要）
                        node["data"].pop("outputs", None)
        
        # 处理知识检索节点的数据集ID加密（简化版）
        for node in nodes:
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