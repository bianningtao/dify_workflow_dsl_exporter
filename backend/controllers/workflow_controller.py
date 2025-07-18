from flask_restful import Resource
from services.workflow_service import WorkflowService

class WorkflowDraftApi(Resource):
    def get(self, app_id):
        """获取工作流草稿"""
        workflow_service = WorkflowService()
        
        # 获取或创建工作流
        workflow = workflow_service.get_draft_workflow(app_id)
        if not workflow:
            workflow = workflow_service.create_default_workflow(app_id)
        
        # 返回工作流数据
        return {
            "id": workflow.id,
            "app_id": workflow.app_id,
            "version": workflow.version,
            "graph": workflow.graph,
            "features": workflow.features,
            "environment_variables": [
                {
                    "name": env.name,
                    "value": env.value,
                    "value_type": env.value_type
                }
                for env in workflow.environment_variables
            ]
        } 