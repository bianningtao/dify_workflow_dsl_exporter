from flask import request
from flask_restful import Resource, reqparse
from services.workflow_service import WorkflowService
from services.app_dsl_service import AppDslService
import zipfile
import io
import json
from datetime import datetime

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

class ApiTestApi(Resource):
    def get(self):
        """测试API连接"""
        try:
            from services.api_connector import api_connector
            result = api_connector.test_connection()
            
            if result["success"]:
                return result, 200
            else:
                return result, 503  # Service Unavailable
                
        except Exception as e:
            return {"success": False, "error": str(e)}, 500

class WorkflowRefreshApi(Resource):
    def post(self):
        """刷新工作流列表缓存"""
        try:
            workflow_service = WorkflowService()
            workflow_service.clear_cache()
            
            return {
                "message": "缓存已清除，数据将在下次请求时刷新",
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}, 500

class WorkflowListApi(Resource):
    def get(self):
        """获取所有工作流列表"""
        # 解析分页参数
        parser = reqparse.RequestParser()
        parser.add_argument("page", type=int, default=1, location="args", help="页码")
        parser.add_argument("page_size", type=int, default=20, location="args", help="每页数量")
        parser.add_argument("search", type=str, default="", location="args", help="搜索关键词")
        args = parser.parse_args()
        
        # 验证分页参数
        page = max(1, args["page"])
        page_size = max(5, min(100, args["page_size"]))  # 限制每页5-100条
        search = args["search"].strip() if args["search"] else ""
        
        workflow_service = WorkflowService()
        
        try:
            # 获取分页工作流数据
            result = workflow_service.get_workflows_paginated(
                page=page, 
                page_size=page_size, 
                search=search
            )
            
            workflows = result.get("workflows", [])
            total = result.get("total", 0)
            
            # 获取全量应用类型统计（不分页）
            all_apps_result = workflow_service.get_workflows_paginated(
                page=1, 
                page_size=total if total > 0 else 100, 
                search=search
            )
            all_apps = all_apps_result.get("workflows", [])
            
            # 计算应用类型统计
            type_stats = {}
            for workflow in all_apps:
                app_mode = getattr(workflow, 'app_mode', 'workflow')
                type_stats[app_mode] = type_stats.get(app_mode, 0) + 1
            
            # 转换为前端需要的格式
            workflow_list = []
            for workflow in workflows:
                workflow_list.append({
                    "id": workflow.id,
                    "app_id": workflow.app_id,
                    "app_name": getattr(workflow, 'app_name', f"工作流 {workflow.app_id[:8]}"),
                    "version": workflow.version,
                    "name": getattr(workflow, 'app_name', f"工作流 {workflow.app_id[:8]}"),  # 兼容前端
                    "node_count": len(workflow.graph.get("nodes", [])),
                    "has_secret_variables": any(
                        env.value_type == "secret" 
                        for env in workflow.environment_variables
                    ),
                    "last_modified": datetime.now().isoformat(),
                    "description": getattr(workflow, 'app_description', '') or '',
                    "app_mode": getattr(workflow, 'app_mode', 'workflow')  # 添加应用模式字段
                })
            
            # 计算分页信息
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "workflows": workflow_list,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                },
                "stats": type_stats  # 添加全量应用类型统计
            }
            
        except Exception as e:
            return {"error": str(e)}, 500

class WorkflowBatchExportApi(Resource):
    def post(self):
        """批量导出工作流DSL"""
        parser = reqparse.RequestParser()
        parser.add_argument("app_ids", type=list, location="json", required=True, 
                          help="应用ID列表")
        parser.add_argument("include_secret", type=bool, default=False, location="json")
        parser.add_argument("export_format", type=str, default="zip", location="json",
                          choices=["zip", "individual"], help="导出格式：zip或individual")
        
        args = parser.parse_args()
        
        workflow_service = WorkflowService()
        
        try:
            export_results = []
            
            # 为每个应用ID导出DSL
            for app_id in args["app_ids"]:
                try:
                    # 获取工作流
                    workflow = workflow_service.get_draft_workflow(app_id)
                    if not workflow:
                        workflow = workflow_service.create_default_workflow(app_id)
                    
                    # 获取或创建应用模型
                    app_model = workflow_service.get_or_create_app_model(app_id)
                    
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
                    
                    export_results.append({
                        "app_id": app_id,
                        "success": True,
                        "data": dsl_data,
                        "filename": filename,
                        "workflow_name": workflow_name
                    })
                    
                except Exception as e:
                    export_results.append({
                        "app_id": app_id,
                        "success": False,
                        "error": str(e),
                        "workflow_name": f"工作流 {app_id[:8]}"
                    })
            
            # 根据导出格式处理结果
            if args["export_format"] == "zip":
                # 创建ZIP文件
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for result in export_results:
                        if result["success"]:
                            zip_file.writestr(result["filename"], result["data"])
                        else:
                            # 为失败的导出创建错误文件
                            error_content = f"导出失败: {result['error']}"
                            zip_file.writestr(f"ERROR-{result['app_id']}.txt", error_content)
                
                zip_buffer.seek(0)
                
                # 返回ZIP文件的base64编码
                import base64
                zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
                
                return {
                    "export_format": "zip",
                    "filename": f"workflows-export-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    "data": zip_base64,
                    "results": export_results,
                    "success_count": sum(1 for r in export_results if r["success"]),
                    "total_count": len(export_results)
                }
            else:
                # 返回单独的文件
                return {
                    "export_format": "individual",
                    "results": export_results,
                    "success_count": sum(1 for r in export_results if r["success"]),
                    "total_count": len(export_results)
                }
                
        except Exception as e:
            return {"error": str(e)}, 500 