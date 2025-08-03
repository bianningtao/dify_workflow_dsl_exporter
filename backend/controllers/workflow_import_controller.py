from flask import request, jsonify
from flask_restful import Resource
import logging
from services.workflow_import_service import workflow_import_service
import json

logger = logging.getLogger(__name__)


class WorkflowImportApi(Resource):
    """单个工作流导入API"""
    
    def post(self):
        """导入单个工作流"""
        try:
            data = request.get_json()
            
            # 验证必需参数
            if not data:
                return {'error': '请求数据不能为空'}, 400
            
            target_instance_id = data.get('target_instance_id')
            if not target_instance_id:
                return {'error': '目标实例ID不能为空'}, 400
            
            mode = data.get('mode')
            if not mode or mode not in ['yaml-content', 'yaml-url']:
                return {'error': '导入模式必须是 yaml-content 或 yaml-url'}, 400
            
            if mode == 'yaml-content' and not data.get('yaml_content'):
                return {'error': 'YAML内容不能为空'}, 400
            
            if mode == 'yaml-url' and not data.get('yaml_url'):
                return {'error': 'YAML URL不能为空'}, 400
            
            # 构建导入数据
            import_data = {
                'mode': mode,
                'yaml_content': data.get('yaml_content'),
                'yaml_url': data.get('yaml_url'),
                'name': data.get('name'),
                'description': data.get('description'),
                'icon_type': data.get('icon_type'),
                'icon': data.get('icon'),
                'icon_background': data.get('icon_background'),
                'app_id': data.get('app_id')
            }
            
            # 执行导入
            result = workflow_import_service.import_single_workflow(
                target_instance_id, import_data
            )
            
            if result.get('success'):
                return result, 200
            else:
                return {'error': result.get('error')}, 400
                
        except Exception as e:
            logger.exception(f"导入工作流时发生错误: {e}")
            return {'error': f'服务器内部错误: {str(e)}'}, 500


class WorkflowImportConfirmApi(Resource):
    """工作流导入确认API"""
    
    def post(self, import_id):
        """确认待处理的导入"""
        try:
            data = request.get_json() or {}
            target_instance_id = data.get('target_instance_id')
            
            if not target_instance_id:
                return {'error': '目标实例ID不能为空'}, 400
            
            # 执行确认
            result = workflow_import_service.confirm_import(
                target_instance_id, import_id
            )
            
            if result.get('success'):
                return result, 200
            else:
                return {'error': result.get('error')}, 400
                
        except Exception as e:
            logger.exception(f"确认导入时发生错误: {e}")
            return {'error': f'服务器内部错误: {str(e)}'}, 500


class WorkflowBatchImportApi(Resource):
    """批量工作流导入API"""
    
    def post(self):
        """批量导入工作流"""
        try:
            data = request.get_json()
            
            # 验证必需参数
            if not data:
                return {'error': '请求数据不能为空'}, 400
            
            target_instance_id = data.get('target_instance_id')
            if not target_instance_id:
                return {'error': '目标实例ID不能为空'}, 400
            
            files = data.get('files', [])
            if not files:
                return {'error': '工作流文件列表不能为空'}, 400
            
            # 验证文件数据
            for i, file_data in enumerate(files):
                if not file_data.get('filename'):
                    return {'error': f'文件 {i+1} 缺少文件名'}, 400
                if not file_data.get('content'):
                    return {'error': f'文件 {i+1} 内容不能为空'}, 400
            
            # 获取导入选项
            import_options = data.get('import_options', {})
            
            # 执行批量导入
            result = workflow_import_service.batch_import_workflows(
                target_instance_id, files, import_options
            )
            
            return result, 200
            
        except Exception as e:
            logger.exception(f"批量导入工作流时发生错误: {e}")
            return {'error': f'服务器内部错误: {str(e)}'}, 500


class TargetInstancesApi(Resource):
    """目标实例列表API"""
    
    def get(self):
        """获取所有可用的目标实例"""
        try:
            instances = workflow_import_service.get_target_instances()
            return {'instances': instances}, 200
            
        except Exception as e:
            logger.exception(f"获取目标实例列表时发生错误: {e}")
            return {'error': f'服务器内部错误: {str(e)}'}, 500


class TargetInstanceTestApi(Resource):
    """目标实例连接测试API"""
    
    def post(self, instance_id):
        """测试指定目标实例的连接"""
        try:
            status = workflow_import_service._test_instance_connection(instance_id)
            return {'instance_id': instance_id, 'status': status}, 200
            
        except Exception as e:
            logger.exception(f"测试目标实例连接时发生错误: {e}")
            return {'error': f'服务器内部错误: {str(e)}'}, 500


class WorkflowFileValidateApi(Resource):
    """工作流文件验证API"""
    
    def post(self):
        """验证工作流文件格式"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '请求数据不能为空'}, 400
            
            yaml_content = data.get('yaml_content')
            if not yaml_content:
                return {'error': 'YAML内容不能为空'}, 400
            
            # 验证YAML格式
            try:
                import yaml
                yaml_data = yaml.safe_load(yaml_content)
                
                if not isinstance(yaml_data, dict):
                    return {'valid': False, 'error': 'YAML内容必须是一个对象'}, 200
                
                # 检查必需的字段
                if 'app' not in yaml_data:
                    return {'valid': False, 'error': '缺少 app 字段'}, 200
                
                app_data = yaml_data.get('app', {})
                if not app_data.get('name'):
                    return {'valid': False, 'error': '应用名称不能为空'}, 200
                
                if not app_data.get('mode'):
                    return {'valid': False, 'error': '应用模式不能为空'}, 200
                
                # 提取应用信息用于预览
                app_info = {
                    'name': app_data.get('name'),
                    'description': app_data.get('description', ''),
                    'mode': app_data.get('mode'),
                    'icon': app_data.get('icon', '🤖'),
                    'icon_type': app_data.get('icon_type', 'emoji'),
                    'icon_background': app_data.get('icon_background', '#FFEAD5'),
                    'version': yaml_data.get('version', '0.1.0')
                }
                
                return {
                    'valid': True, 
                    'app_info': app_info
                }, 200
                
            except yaml.YAMLError as e:
                return {'valid': False, 'error': f'YAML格式错误: {str(e)}'}, 200
            
        except Exception as e:
            logger.exception(f"验证工作流文件时发生错误: {e}")
            return {'error': f'服务器内部错误: {str(e)}'}, 500