import json
import logging
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .config_service import config
from models.app import App, Workflow, EnvironmentVariable, AppMode

class APIConnector:
    """API连接器，用于通过Dify API获取数据"""
    
    def __init__(self):
        self.config = config
        self.session = self._create_session()
        self.base_url = None
        self.headers = {}
        self._init_api_config()
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _init_api_config(self):
        """初始化API配置"""
        if not self.config.is_api_enabled():
            return
        
        api_config = self.config.get_api_config()
        self.base_url = api_config['base_url'].rstrip('/')
        self.headers = self.config.get_api_headers()
        
        # 设置会话头部
        self.session.headers.update(self.headers)
        
        # 设置超时
        self.timeout = api_config.get('timeout', 30)
        
        logging.info(f"API连接器初始化成功，基础URL: {self.base_url}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发送HTTP请求"""
        if not self.base_url:
            raise RuntimeError("API连接器未正确初始化")
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return {'data': response.text}
                
        except requests.exceptions.RequestException as e:
            logging.error(f"API请求失败: {method} {url} - {e}")
            return None
    
    def get_app_by_id(self, app_id: str) -> Optional[App]:
        """根据应用ID获取应用信息"""
        if not self.config.is_api_enabled():
            return None
        
        api_config = self.config.get_api_config()
        endpoint = api_config.get('endpoints', {}).get('apps', '/api/apps/{app_id}')
        endpoint = endpoint.format(app_id=app_id)
        
        try:
            response = self._make_request('GET', endpoint)
            if not response:
                logging.warning(f"未找到应用ID为 {app_id} 的应用")
                return None
            
            # 根据实际API响应格式调整
            app_data = response.get('data', response)
            
            return App(
                id=app_data.get('id', app_id),
                name=app_data.get('name', f'工作流应用 {app_id[:8]}'),
                mode=app_data.get('mode', AppMode.WORKFLOW.value),
                icon=app_data.get('icon', '🤖'),
                icon_type=app_data.get('icon_type', 'emoji'),
                icon_background=app_data.get('icon_background', '#FFEAD5'),
                description=app_data.get('description', ''),
                use_icon_as_answer_icon=app_data.get('use_icon_as_answer_icon', False),
                tenant_id=app_data.get('tenant_id', '')
            )
        except Exception as e:
            logging.error(f"获取应用信息失败: {e}")
            return None
    
    def get_workflow_by_app_id(self, app_id: str) -> Optional[Workflow]:
        """根据应用ID获取工作流信息"""
        if not self.config.is_api_enabled():
            return None
        
        api_config = self.config.get_api_config()
        endpoint = api_config.get('endpoints', {}).get('workflows', '/api/apps/{app_id}/workflows/draft')
        endpoint = endpoint.format(app_id=app_id)
        
        try:
            response = self._make_request('GET', endpoint)
            if not response:
                logging.warning(f"未找到应用ID为 {app_id} 的工作流")
                return None
            
            # 根据实际API响应格式调整
            workflow_data = response.get('data', response)
            
            # 获取环境变量
            environment_variables = self.get_environment_variables_by_app_id(app_id)
            
            return Workflow(
                id=workflow_data.get('id', ''),
                app_id=workflow_data.get('app_id', app_id),
                version=workflow_data.get('version', '1.0'),
                graph=workflow_data.get('graph', {}),
                features=workflow_data.get('features', {}),
                environment_variables=environment_variables
            )
        except Exception as e:
            logging.error(f"获取工作流信息失败: {e}")
            return None
    
    def get_all_workflows(self) -> List[Workflow]:
        """获取所有工作流"""
        if not self.config.is_api_enabled():
            return []
        
        api_config = self.config.get_api_config()
        endpoint = api_config.get('endpoints', {}).get('workflows_list', '/api/workflows')
        
        try:
            response = self._make_request('GET', endpoint)
            if not response:
                logging.warning("未找到工作流列表")
                return []
            
            workflows_data = response.get('data', response.get('workflows', []))
            workflows = []
            
            # 为每个工作流获取详细信息
            for workflow_item in workflows_data:
                app_id = workflow_item.get('app_id')
                if not app_id:
                    continue
                
                # 获取完整的工作流信息
                workflow = self.get_workflow_by_app_id(app_id)
                if workflow:
                    workflows.append(workflow)
            
            return workflows
            
        except Exception as e:
            logging.error(f"获取所有工作流失败: {e}")
            return []
    
    def get_environment_variables_by_app_id(self, app_id: str) -> List[EnvironmentVariable]:
        """根据应用ID获取环境变量"""
        if not self.config.is_api_enabled():
            return []
        
        api_config = self.config.get_api_config()
        endpoint = api_config.get('endpoints', {}).get('environment_variables', '/api/apps/{app_id}/env-variables')
        endpoint = endpoint.format(app_id=app_id)
        
        try:
            response = self._make_request('GET', endpoint)
            if not response:
                return []
            
            # 根据实际API响应格式调整
            env_data = response.get('data', response)
            if isinstance(env_data, dict):
                env_data = env_data.get('variables', [])
            
            environment_variables = []
            for env_var in env_data:
                environment_variables.append(
                    EnvironmentVariable(
                        name=env_var['name'],
                        value=env_var['value'],
                        value_type=env_var.get('value_type', 'string')
                    )
                )
            
            return environment_variables
        except Exception as e:
            logging.error(f"获取环境变量失败: {e}")
            return []
    
    def test_connection(self) -> bool:
        """测试API连接"""
        if not self.config.is_api_enabled():
            return False
        
        try:
            # 尝试获取一个简单的端点
            response = self._make_request('GET', '/api/ping')
            if response:
                return True
            
            # 如果ping端点不存在，尝试获取一个已知的端点
            response = self._make_request('GET', '/api/apps')
            return response is not None
            
        except Exception as e:
            logging.error(f"API连接测试失败: {e}")
            return False
    
    def get_app_list(self, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """获取应用列表"""
        if not self.config.is_api_enabled():
            return []
        
        try:
            response = self._make_request('GET', f'/api/apps?page={page}&limit={limit}')
            if not response:
                return []
            
            # 根据实际API响应格式调整
            apps_data = response.get('data', response)
            if isinstance(apps_data, dict):
                return apps_data.get('apps', [])
            elif isinstance(apps_data, list):
                return apps_data
            
            return []
        except Exception as e:
            logging.error(f"获取应用列表失败: {e}")
            return []
    
    def search_apps(self, query: str) -> List[Dict[str, Any]]:
        """搜索应用"""
        if not self.config.is_api_enabled():
            return []
        
        try:
            response = self._make_request('GET', f'/api/apps/search?q={query}')
            if not response:
                return []
            
            # 根据实际API响应格式调整
            apps_data = response.get('data', response)
            if isinstance(apps_data, dict):
                return apps_data.get('apps', [])
            elif isinstance(apps_data, list):
                return apps_data
            
            return []
        except Exception as e:
            logging.error(f"搜索应用失败: {e}")
            return []
    
    def get_app_export_data(self, app_id: str, include_secrets: bool = False) -> Optional[str]:
        """获取应用导出数据"""
        if not self.config.is_api_enabled():
            return None
        
        try:
            endpoint = f'/api/apps/{app_id}/export'
            params = {'include_secrets': include_secrets}
            
            response = self._make_request('GET', endpoint, params=params)
            if not response:
                return None
            
            # 根据实际API响应格式调整
            export_data = response.get('data', response)
            if isinstance(export_data, dict):
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            else:
                return str(export_data)
                
        except Exception as e:
            logging.error(f"获取应用导出数据失败: {e}")
            return None
    
    def get_workflows_paginated(self, page: int = 1, page_size: int = 20, search: str = "") -> dict:
        """
        分页获取工作流列表
        :param page: 页码（从1开始）
        :param page_size: 每页数量
        :param search: 搜索关键词
        :return: 包含工作流列表和总数的字典
        """
        if not self.config.is_api_enabled():
            return {"workflows": [], "total": 0}
        
        try:
            # 先获取所有工作流，然后在内存中进行分页（API通常不支持直接分页）
            all_workflows = self.get_all_workflows()
            
            # 搜索过滤
            if search:
                filtered_workflows = []
                search_lower = search.lower()
                for workflow in all_workflows:
                    # 搜索应用ID和可能的应用名称
                    app_name = getattr(workflow, 'app_name', f"工作流 {workflow.app_id[:8]}")
                    if (search_lower in workflow.app_id.lower() or 
                        search_lower in app_name.lower()):
                        filtered_workflows.append(workflow)
                all_workflows = filtered_workflows
            
            # 计算总数
            total = len(all_workflows)
            
            # 分页处理
            start = (page - 1) * page_size
            end = start + page_size
            paginated_workflows = all_workflows[start:end]
            
            return {
                "workflows": paginated_workflows,
                "total": total
            }
            
        except Exception as e:
            logging.error(f"API分页获取工作流失败: {e}")
            return {"workflows": [], "total": 0}
    
    def close(self):
        """关闭API连接器"""
        if self.session:
            self.session.close()
            logging.info("API连接器已关闭")


# 全局API连接器实例
api_connector = APIConnector() 