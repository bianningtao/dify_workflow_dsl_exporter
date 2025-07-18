from flask import request
from flask_restful import Resource, reqparse
from models.app import App, AppMode
from services.app_dsl_service import AppDslService
from services.workflow_service import WorkflowService
from services.config_service import config
from services.database_connector import database_connector
from services.api_connector import api_connector
from services.manual_import_service import manual_import_service
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
        
        try:
            # 导出DSL
            dsl_data = AppDslService.export_dsl(
                app_model=app_model, 
                include_secret=args["include_secret"]
            )
            
            return {"data": dsl_data}
            
        except Exception as e:
            return {"error": str(e)}, 500
    
    def _get_or_create_app_model(self, app_id: str) -> App:
        """获取或创建应用模型"""
        # 根据配置选择数据源
        if config.is_database_enabled():
            app_model = database_connector.get_app_by_id(app_id)
        elif config.is_api_enabled():
            app_model = api_connector.get_app_by_id(app_id)
        elif config.is_manual_enabled():
            app_model = manual_import_service.get_app_by_id(app_id)
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