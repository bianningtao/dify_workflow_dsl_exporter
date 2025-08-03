import json
import uuid
import yaml
import requests
import logging
from typing import Dict, Any, Optional, List, Union
from services.config_service import config
import base64
import time
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class WorkflowImportService:
    """工作流导入服务类"""
    
    def __init__(self):
        self.timeout = 30
        self.retry_count = 3
        self.retry_delay = 1
    
    def import_single_workflow(
        self,
        target_instance_id: str,
        import_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        导入单个工作流到目标Dify实例
        
        Args:
            target_instance_id: 目标实例ID
            import_data: 导入数据，包含mode、yaml_content等
            
        Returns:
            导入结果
        """
        try:
            # 获取目标实例配置
            instance = config.get_target_instance_by_id(target_instance_id)
            if not instance:
                return {
                    'success': False,
                    'error': f'目标实例 {target_instance_id} 不存在'
                }
            
            # 构建导入请求
            headers = config.get_target_instance_headers(target_instance_id)
            
            # 导入API端点（使用配置化端点）
            import_url = config.get_full_api_url('app_import', target_instance_id)
            
            # 准备请求数据
            request_data = {
                'mode': import_data.get('mode', 'yaml-content'),
                'yaml_content': import_data.get('yaml_content'),
                'yaml_url': import_data.get('yaml_url'),
                'name': import_data.get('name'),
                'description': import_data.get('description'),
                'icon_type': import_data.get('icon_type'),
                'icon': import_data.get('icon'),
                'icon_background': import_data.get('icon_background'),
                'app_id': import_data.get('app_id')
            }
            
            # 移除空值
            request_data = {k: v for k, v in request_data.items() if v is not None}
            
            # 发送导入请求
            response = self._make_request_with_retry(
                'POST', import_url, headers=headers, json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'import_id': result.get('id'),
                    'status': result.get('status'),
                    'app_id': result.get('app_id'),
                    'app_mode': result.get('app_mode'),
                    'current_dsl_version': result.get('current_dsl_version'),
                    'imported_dsl_version': result.get('imported_dsl_version'),
                    'warnings': result.get('warnings', [])
                }
            elif response.status_code == 202:
                # 需要确认的导入
                result = response.json()
                return {
                    'success': True,
                    'import_id': result.get('id'),
                    'status': 'pending',
                    'app_id': result.get('app_id'),
                    'app_mode': result.get('app_mode'),
                    'current_dsl_version': result.get('current_dsl_version'),
                    'imported_dsl_version': result.get('imported_dsl_version'),
                    'requires_confirmation': True
                }
            else:
                error_msg = f'导入失败: HTTP {response.status_code}'
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.exception(f"导入工作流时发生错误: {e}")
            return {
                'success': False,
                'error': f'导入失败: {str(e)}'
            }
    
    def confirm_import(
        self,
        target_instance_id: str,
        import_id: str
    ) -> Dict[str, Any]:
        """
        确认待处理的导入
        
        Args:
            target_instance_id: 目标实例ID
            import_id: 导入ID
            
        Returns:
            确认结果
        """
        try:
            headers = config.get_target_instance_headers(target_instance_id)
            
            # 确认导入API端点（使用配置化端点）
            confirm_url = config.get_full_api_url('import_confirm', target_instance_id, import_id=import_id)
            
            response = self._make_request_with_retry(
                'POST', confirm_url, headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('status'),
                    'app_id': result.get('app_id'),
                    'app_mode': result.get('app_mode')
                }
            else:
                error_msg = f'确认导入失败: HTTP {response.status_code}'
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.exception(f"确认导入时发生错误: {e}")
            return {
                'success': False,
                'error': f'确认导入失败: {str(e)}'
            }
    
    def batch_import_workflows(
        self,
        target_instance_id: str,
        workflow_files: List[Dict[str, Any]],
        import_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        批量导入工作流
        
        Args:
            target_instance_id: 目标实例ID
            workflow_files: 工作流文件列表 [{'filename': '', 'content': '', 'name': '', 'description': ''}]
            import_options: 导入选项 {'overwrite_existing': bool, 'ignore_errors': bool, 'create_new_on_conflict': bool}
            
        Returns:
            批量导入结果
        """
        results = []
        success_count = 0
        failed_count = 0
        warning_count = 0
        
        for workflow_file in workflow_files:
            filename = workflow_file.get('filename', 'unknown.yaml')
            content = workflow_file.get('content', '')
            
            logger.info(f"正在导入工作流文件: {filename}")
            
            try:
                # 解析YAML内容以获取应用信息
                yaml_data = yaml.safe_load(content)
                app_info = yaml_data.get('app', {})
                
                # 构建导入数据
                import_data = {
                    'mode': 'yaml-content',
                    'yaml_content': content,
                    'name': workflow_file.get('name') or app_info.get('name'),
                    'description': workflow_file.get('description') or app_info.get('description'),
                    'icon_type': app_info.get('icon_type', 'emoji'),
                    'icon': app_info.get('icon', '🤖'),
                    'icon_background': app_info.get('icon_background', '#FFEAD5')
                }
                
                # 如果启用了覆盖现有应用，需要先检查是否存在同名应用
                if import_options.get('overwrite_existing', False):
                    existing_app = self._find_app_by_name(
                        target_instance_id, 
                        import_data.get('name', '')
                    )
                    if existing_app:
                        import_data['app_id'] = existing_app['id']
                
                # 执行导入
                result = self.import_single_workflow(target_instance_id, import_data)
                
                # 处理需要确认的导入
                if result.get('requires_confirmation', False) and not import_options.get('ignore_errors', False):
                    confirm_result = self.confirm_import(
                        target_instance_id, 
                        result.get('import_id')
                    )
                    if confirm_result.get('success'):
                        result.update(confirm_result)
                        result['status'] = confirm_result.get('status')
                
                # 统计结果
                if result.get('success'):
                    success_count += 1
                    if result.get('status') in ['completed-with-warnings', 'pending']:
                        warning_count += 1
                else:
                    failed_count += 1
                    if import_options.get('ignore_errors', False):
                        logger.warning(f"忽略文件 {filename} 的导入错误: {result.get('error')}")
                    
                results.append({
                    'filename': filename,
                    'success': result.get('success', False),
                    'app_id': result.get('app_id'),
                    'app_name': import_data.get('name'),
                    'import_id': result.get('import_id'),
                    'status': result.get('status'),
                    'error': result.get('error'),
                    'warnings': result.get('warnings', [])
                })
                
            except Exception as e:
                error_msg = f"处理文件 {filename} 时发生错误: {str(e)}"
                logger.exception(error_msg)
                
                failed_count += 1
                results.append({
                    'filename': filename,
                    'success': False,
                    'error': error_msg
                })
                
                if not import_options.get('ignore_errors', False):
                    logger.error(f"批量导入因错误停止: {error_msg}")
                    break
        
        return {
            'results': results,
            'success_count': success_count,
            'total_count': len(workflow_files),
            'failed_count': failed_count,
            'warning_count': warning_count
        }
    
    def _find_app_by_name(self, target_instance_id: str, app_name: str) -> Optional[Dict[str, Any]]:
        """在目标实例中查找指定名称的应用"""
        try:
            headers = config.get_target_instance_headers(target_instance_id)
            
            # 应用列表API端点（使用配置化端点）
            apps_url = config.get_full_api_url('apps_list', target_instance_id)
            params = {'name': app_name, 'limit': 100}
            
            response = self._make_request_with_retry(
                'GET', apps_url, headers=headers, params=params
            )
            
            if response.status_code == 200:
                apps_data = response.json()
                apps = apps_data.get('data', [])
                
                for app in apps:
                    if app.get('name') == app_name:
                        return app
            
            return None
            
        except Exception as e:
            logger.exception(f"查找应用时发生错误: {e}")
            return None
    
    def get_target_instances(self) -> List[Dict[str, Any]]:
        """获取所有可用的目标实例"""
        instances = config.get_target_instances()
        result = []
        
        for instance in instances:
            # 不在这里测试连接状态，提高响应速度
            # 连接测试由前端单独调用
            result.append({
                'id': instance.get('id'),
                'name': instance.get('name'),
                'url': instance.get('url'),
                'is_default': instance.get('is_default', False),
                'auth_type': instance.get('auth', {}).get('type', 'unknown')
            })
        
        return result
    
    def _test_instance_connection(self, instance_id: str) -> str:
        """测试目标实例的连接状态"""
        try:
            headers = config.get_target_instance_headers(instance_id)
            
            # 尝试访问应用列表API来测试连接（使用配置化端点）
            test_url = config.get_full_api_url('apps_list', instance_id)
            
            response = requests.get(
                test_url, 
                headers=headers, 
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                return 'connected'
            else:
                return 'authentication_failed'
                
        except requests.exceptions.ConnectionError:
            return 'connection_failed'
        except requests.exceptions.Timeout:
            return 'timeout'
        except Exception as e:
            logger.exception(f"测试连接时发生错误: {e}")
            return 'unknown_error'
    
    def _make_request_with_retry(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> requests.Response:
        """带重试的HTTP请求"""
        last_exception = None
        
        for attempt in range(self.retry_count):
            try:
                response = requests.request(
                    method, 
                    url, 
                    timeout=self.timeout,
                    verify=False,
                    **kwargs
                )
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.retry_count - 1:
                    logger.warning(f"请求失败，正在重试 (尝试 {attempt + 1}/{self.retry_count}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"请求失败，已达到最大重试次数: {e}")
        
        # 如果所有重试都失败，抛出最后一个异常
        raise last_exception


# 全局导入服务实例
workflow_import_service = WorkflowImportService()