from flask import request
from flask_restful import Resource, reqparse
from models.app import App, AppMode
from services.app_dsl_service import AppDslService
from services.workflow_service import WorkflowService
from services.config_service import config
from services.database_connector import database_connector
from services.api_connector import api_connector

import uuid

class AppExportApi(Resource):
    def get(self, app_id):
        """导出应用程序DSL"""
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument("include_secret", type=bool, default=False, location="args")
        args = parser.parse_args()
        
        # 获取或创建应用模型
        app_model = self._get_or_create_app_model(app_id)
        
        # 获取工作流信息
        workflow_service = WorkflowService()
        workflow = workflow_service.get_draft_workflow(app_id)
        
        try:
            # 导出DSL
            dsl_data = AppDslService.export_dsl(
                app_model=app_model, 
                include_secret=args["include_secret"]
            )
            
            # 生成文件名 - 使用工作流名称
            workflow_name = getattr(workflow, 'app_name', None) or app_model.name
            # 清理文件名，移除特殊字符
            safe_name = "".join(c for c in workflow_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')  # 空格替换为下划线
            if not safe_name:  # 如果名称为空，使用app_id作为fallback
                safe_name = f"workflow-{app_id[:8]}"
            
            filename = f"{safe_name}.yml"
            
            return {
                "data": dsl_data,
                "filename": filename,
                "workflow_name": workflow_name,
                "app_id": app_id
            }
            
        except Exception as e:
            return {"error": str(e)}, 500
    
    def _get_or_create_app_model(self, app_id: str) -> App:
        """获取或创建应用模型"""
        # 根据配置选择数据源
        if config.is_database_enabled():
            app_model = database_connector.get_app_by_id(app_id)
        elif config.is_api_enabled():
            app_model = api_connector.get_app_by_id(app_id)
        else:
            app_model = None
        
        # 如果没有找到应用，创建一个默认的
        if app_model is None:
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