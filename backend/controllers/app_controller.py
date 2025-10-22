from flask import request
from flask_restful import Resource, reqparse
from models.app import App, AppMode
from services.app_dsl_service import AppDslService
from services.workflow_service import WorkflowService
from services.config_service import config
from services.database_connector import database_connector
from services.api_connector import api_connector
from middleware.auth_middleware import token_required
import logging
import uuid

logger = logging.getLogger(__name__)

class AppExportApi(Resource):
    def get(self, app_id):
        """导出应用程序DSL"""
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument("include_secret", type=bool, default=False, location="args")
        args = parser.parse_args()
        
        # 尝试获取用户ID（如果有认证token）
        user_id = None
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                from services.auth_service import auth_service
                token = auth_header[7:]
                payload = auth_service.verify_token(token)
                if payload:
                    user_id = payload.get('user_id')
                    logger.info(f"用户 {user_id} 请求导出应用 {app_id}")
        except Exception as e:
            logger.warning(f"解析认证token失败: {e}")
        
        # 创建WorkflowService实例（支持用户配置）
        workflow_service = WorkflowService(user_id=user_id)
        
        # 获取或创建应用模型
        app_model = self._get_or_create_app_model(app_id, workflow_service)
        
        # 获取工作流信息
        workflow = workflow_service.get_draft_workflow(app_id)
        
        try:
            # 导出DSL
            dsl_data = AppDslService.export_dsl(
                app_model=app_model, 
                include_secret=args["include_secret"],
                workflow_service=workflow_service
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
    
    def _get_or_create_app_model(self, app_id: str, workflow_service: WorkflowService) -> App:
        """获取或创建应用模型"""
        # 使用WorkflowService的方法，它会自动处理用户配置
        return workflow_service.get_or_create_app_model(app_id) 