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
    
    # agent-chat 和 chat 类型应用的默认 model_config 模板
    DEFAULT_MODEL_CONFIG_TEMPLATE = {
        'pre_prompt': '',
        'prompt_type': 'simple',
        'chat_prompt_config': {},
        'completion_prompt_config': {},
        'user_input_form': [],
        'dataset_query_variable': '',
        'opening_statement': '',
        'suggested_questions': [],
        'more_like_this': {'enabled': False},
        'suggested_questions_after_answer': {'enabled': False},
        'speech_to_text': {'enabled': False},
        'text_to_speech': {'enabled': False, 'voice': '', 'language': ''},
        'retriever_resource': {'enabled': False},
        'sensitive_word_avoidance': {'enabled': False},
        'file_upload': {'image': {'enabled': False, 'number_limits': 3, 'detail': 'high', 'transfer_methods': ['remote_url', 'local_file']}},
        'agent_mode': {'enabled': True, 'max_iteration': 5, 'strategy': 'function_call', 'tools': []},
    }
    
    def __init__(self):
        self.timeout = 30
        self.retry_count = 3
        self.retry_delay = 1
    
    def _fix_incomplete_dsl(self, yaml_content: str) -> tuple[str, List[str]]:
        """
        修复不完整的 DSL 文件，自动补全缺失的必要字段
        
        Args:
            yaml_content: 原始 YAML 内容
            
        Returns:
            (修复后的 YAML 内容, 修复信息列表)
        """
        fixes = []
        
        try:
            yaml_data = yaml.safe_load(yaml_content)
            if not yaml_data:
                return yaml_content, fixes
            
            app_mode = yaml_data.get('app', {}).get('mode', '')
            model_config = yaml_data.get('model_config', {})
            
            # 只处理 agent-chat 和 chat 类型的应用
            if app_mode in ['agent-chat', 'chat']:
                modified = False
                
                # 检查并补全缺失的必要字段
                for key, default_value in self.DEFAULT_MODEL_CONFIG_TEMPLATE.items():
                    if key not in model_config:
                        model_config[key] = default_value
                        fixes.append(f"补全缺失字段: model_config.{key}")
                        modified = True
                
                if modified:
                    yaml_data['model_config'] = model_config
                    # 重新生成 YAML 内容
                    yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    logger.info(f"DSL 文件已自动修复，补全了 {len(fixes)} 个字段")
            
        except Exception as e:
            logger.warning(f"尝试修复 DSL 时发生错误: {e}")
        
        return yaml_content, fixes
    
    def _get_instance_config(self, target_instance_id: str, user_id: str = None) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]], Optional[str]]:
        """
        获取目标实例的配置、请求头和基础URL
        
        Args:
            target_instance_id: 目标实例ID
            user_id: 用户ID，如果提供则从用户配置中获取
            
        Returns:
            (instance_config, headers, base_url) 的元组
        """
        if user_id:
            from services.user_config_service import user_config_service
            instances = user_config_service.get_user_target_instances(user_id)
            instance = next((inst for inst in instances if inst['id'] == target_instance_id), None)
            
            if not instance:
                return None, None, None
            
            # 构建请求头
            auth_config = instance.get('auth', {})
            auth_type = auth_config.get('type', 'bearer')
            headers = {'Content-Type': 'application/json'}
            
            if auth_type == 'bearer':
                token = auth_config.get('token', '')
                headers['Authorization'] = f"Bearer {token}"
            elif auth_type == 'basic':
                username = auth_config.get('username', '')
                password = auth_config.get('password', '')
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f"Basic {credentials}"
            elif auth_type == 'api_key':
                api_key = auth_config.get('api_key', '')
                header_name = auth_config.get('api_key_header', 'X-API-Key')
                headers[header_name] = api_key
            
            base_url = instance.get('url', '').rstrip('/')
            return instance, headers, base_url
        else:
            # 使用系统配置
            instance = config.get_target_instance_by_id(target_instance_id)
            if not instance:
                return None, None, None
            
            headers = config.get_target_instance_headers(target_instance_id)
            # 从系统配置获取base_url
            base_url = instance.get('url', '').rstrip('/')
            return instance, headers, base_url
    
    def import_single_workflow(
        self,
        target_instance_id: str,
        import_data: Dict[str, Any],
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        导入单个工作流到目标Dify实例
        
        Args:
            target_instance_id: 目标实例ID
            import_data: 导入数据，包含mode、yaml_content等
            user_id: 用户ID，如果提供则从用户配置中获取实例信息
            
        Returns:
            导入结果
        """
        try:
            # 获取目标实例配置
            instance, headers, base_url = self._get_instance_config(target_instance_id, user_id)
            
            if not instance:
                return {
                    'success': False,
                    'error': f'目标实例 {target_instance_id} 不存在'
                }
            
            # 自动修复不完整的 DSL 文件
            yaml_content = import_data.get('yaml_content')
            if yaml_content:
                fixed_content, fixes = self._fix_incomplete_dsl(yaml_content)
                if fixes:
                    logger.info(f"DSL 已自动修复: {', '.join(fixes[:3])}{'...' if len(fixes) > 3 else ''}")
                    import_data = dict(import_data)  # 创建副本避免修改原数据
                    import_data['yaml_content'] = fixed_content
            
            # 构建导入URL
            if user_id:
                import_url = f"{base_url}/console/api/apps/imports"
            else:
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
        import_id: str,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        确认待处理的导入
        
        Args:
            target_instance_id: 目标实例ID
            import_id: 导入ID
            user_id: 用户ID，如果提供则从用户配置中获取实例信息
            
        Returns:
            确认结果
        """
        try:
            # 获取目标实例配置
            instance, headers, base_url = self._get_instance_config(target_instance_id, user_id)
            
            if not instance:
                return {
                    'success': False,
                    'error': f'目标实例 {target_instance_id} 不存在'
                }
            
            # 构建确认URL
            if user_id:
                confirm_url = f"{base_url}/console/api/apps/imports/{import_id}/confirm"
            else:
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
        import_options: Dict[str, Any],
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        批量导入工作流
        
        Args:
            target_instance_id: 目标实例ID
            workflow_files: 工作流文件列表 [{'filename': '', 'content': '', 'name': '', 'description': ''}]
            import_options: 导入选项 {'overwrite_existing': bool, 'ignore_errors': bool, 'create_new_on_conflict': bool}
            user_id: 用户ID，如果提供则从用户配置中获取实例信息
            
        Returns:
            批量导入结果
        """
        results = []
        success_count = 0
        failed_count = 0
        warning_count = 0
        
        logger.info(f"开始批量导入 {len(workflow_files)} 个工作流文件到实例 {target_instance_id}")
        
        for workflow_file in workflow_files:
            filename = workflow_file.get('filename', 'unknown.yaml')
            content = workflow_file.get('content', '')
            
            logger.info(f"正在导入工作流文件: {filename}")
            
            try:
                # 自动修复不完整的 DSL 文件
                fixed_content, fixes = self._fix_incomplete_dsl(content)
                if fixes:
                    logger.info(f"文件 {filename} 已自动修复: {', '.join(fixes[:3])}{'...' if len(fixes) > 3 else ''}")
                
                # 解析YAML内容以获取应用信息
                yaml_data = yaml.safe_load(fixed_content)
                app_info = yaml_data.get('app', {})
                
                # 构建导入数据
                import_data = {
                    'mode': 'yaml-content',
                    'yaml_content': fixed_content,
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
                        import_data.get('name', ''),
                        user_id
                    )
                    if existing_app:
                        import_data['app_id'] = existing_app['id']
                
                # 执行导入
                result = self.import_single_workflow(target_instance_id, import_data, user_id)
                
                # 处理需要确认的导入
                if result.get('status') == 'pending' or result.get('requires_confirmation', False):
                    # 在批量导入中，自动确认所有需要确认的导入
                    logger.info(f"文件 {filename} 需要确认导入，正在自动确认...")
                    confirm_result = self.confirm_import(
                        target_instance_id, 
                        result.get('import_id'),
                        user_id
                    )
                    if confirm_result.get('success'):
                        result.update(confirm_result)
                        result['status'] = confirm_result.get('status', 'completed')
                        logger.info(f"文件 {filename} 导入确认成功，状态: {result['status']}")
                    else:
                        result['success'] = False
                        result['error'] = confirm_result.get('error', '确认导入失败')
                        logger.error(f"文件 {filename} 导入确认失败: {result['error']}")
                
                # 统计结果
                if result.get('success'):
                    success_count += 1
                    if result.get('status') in ['completed-with-warnings', 'pending']:
                        warning_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"文件 {filename} 导入失败: {result.get('error')}")
                    
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
                
                # 只有在严重错误且用户明确设置不忽略错误时才停止
                if not import_options.get('ignore_errors', False) and isinstance(e, (ConnectionError, TimeoutError)):
                    logger.error(f"批量导入因严重错误停止: {error_msg}")
                    break
                else:
                    logger.warning(f"文件 {filename} 处理失败，继续处理下一个文件: {error_msg}")
        
        logger.info(f"批量导入完成 - 总计: {len(workflow_files)}, 成功: {success_count}, 失败: {failed_count}, 警告: {warning_count}")
        
        return {
            'results': results,
            'success_count': success_count,
            'total_count': len(workflow_files),
            'failed_count': failed_count,
            'warning_count': warning_count
        }
    
    def _find_app_by_name(self, target_instance_id: str, app_name: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """在目标实例中查找指定名称的应用"""
        try:
            # 获取目标实例配置
            instance, headers, base_url = self._get_instance_config(target_instance_id, user_id)
            
            if not instance:
                return None
            
            # 构建应用列表URL
            if user_id:
                apps_url = f"{base_url}/console/api/apps"
            else:
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
    
    def get_target_instances(self, user_id: str = None) -> List[Dict[str, Any]]:
        """获取所有可用的目标实例
        
        Args:
            user_id: 用户ID，如果提供则获取用户配置的实例，否则获取系统配置的实例
        """
        # 如果提供了用户ID，从用户配置中获取
        if user_id:
            from services.user_config_service import user_config_service
            instances = user_config_service.get_user_target_instances(user_id)
        else:
            # 否则从系统配置中获取
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
    
    def _test_instance_connection(self, instance_id: str, user_id: str = None) -> str:
        """测试目标实例的连接状态
        
        Args:
            instance_id: 实例ID
            user_id: 用户ID，如果提供则从用户配置中获取实例信息
        """
        try:
            # 获取实例信息
            if user_id:
                from services.user_config_service import user_config_service
                instances = user_config_service.get_user_target_instances(user_id)
                instance = next((inst for inst in instances if inst['id'] == instance_id), None)
                
                if not instance:
                    logger.error(f"未找到用户实例: {instance_id}")
                    return 'unknown_error'
                
                # 构建请求头
                auth_config = instance.get('auth', {})
                auth_type = auth_config.get('type', 'bearer')
                headers = {'Content-Type': 'application/json'}
                
                if auth_type == 'bearer':
                    token = auth_config.get('token', '')
                    headers['Authorization'] = f"Bearer {token}"
                elif auth_type == 'basic':
                    username = auth_config.get('username', '')
                    password = auth_config.get('password', '')
                    import base64
                    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                    headers['Authorization'] = f"Basic {credentials}"
                elif auth_type == 'api_key':
                    api_key = auth_config.get('api_key', '')
                    header_name = auth_config.get('api_key_header', 'X-API-Key')
                    headers[header_name] = api_key
                
                # 构建测试URL
                base_url = instance.get('url', '').rstrip('/')
                test_url = f"{base_url}/console/api/apps?page=1&limit=1"
            else:
                # 使用系统配置
                headers = config.get_target_instance_headers(instance_id)
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