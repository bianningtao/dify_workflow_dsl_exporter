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
        # 添加简单缓存
        self._workflow_apps_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # 缓存5分钟
        # 添加token管理
        self._access_token = None
        self._refresh_token = None
        self._token_expiry = None
        self._init_api_config()
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._workflow_apps_cache is None or self._cache_timestamp is None:
            return False
        
        import time
        return (time.time() - self._cache_timestamp) < self._cache_ttl
    
    def _login_with_credentials(self) -> bool:
        """使用用户名密码登录获取access_token"""
        try:
            api_config = self.config.get_api_config()
            auth_config = api_config.get('auth', {})
            
            if auth_config.get('type') != 'basic':
                return False
            
            username = auth_config.get('username')
            password = auth_config.get('password')
            
            if not username or not password:
                logging.error("用户名或密码为空")
                return False
            
            # 登录请求
            login_url = f"{self.base_url.rstrip('/')}/console/api/login"
            login_data = {
                "email": username,
                "password": password,
                "language": "zh-Hans",
                "remember_me": True
            }
            
            response = self.session.post(login_url, json=login_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('result') == 'success' and result.get('data'):
                data = result['data']
                self._access_token = data.get('access_token')
                self._refresh_token = data.get('refresh_token')
                
                # 计算token过期时间（假设24小时有效）
                import time
                self._token_expiry = time.time() + (24 * 3600)  # 24小时
                
                logging.info("登录成功，获得访问令牌")
                return True
            else:
                logging.error(f"登录失败: {result}")
                return False
                
        except Exception as e:
            logging.error(f"登录请求失败: {e}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """刷新访问令牌"""
        try:
            if not self._refresh_token:
                return False
            
            # 刷新token请求
            refresh_url = f"{self.base_url.rstrip('/')}/console/api/refresh-token"
            headers = {"Authorization": f"Bearer {self._refresh_token}"}
            
            response = self.session.post(refresh_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('result') == 'success' and result.get('data'):
                data = result['data']
                self._access_token = data.get('access_token')
                
                # 更新过期时间
                import time
                self._token_expiry = time.time() + (24 * 3600)  # 24小时
                
                logging.info("访问令牌刷新成功")
                return True
            else:
                logging.error(f"令牌刷新失败: {result}")
                return False
                
        except Exception as e:
            logging.error(f"令牌刷新请求失败: {e}")
            return False
    
    def _is_token_valid(self) -> bool:
        """检查访问令牌是否有效"""
        if not self._access_token or not self._token_expiry:
            return False
        
        import time
        # 提前5分钟刷新token
        return time.time() < (self._token_expiry - 300)
    
    def _ensure_valid_token(self) -> bool:
        """确保有有效的访问令牌"""
        api_config = self.config.get_api_config()
        auth_config = api_config.get('auth', {})
        
        # 如果配置的是bearer token，直接返回True
        if auth_config.get('type') == 'bearer':
            return True
        
        # 如果配置的是basic认证，需要获取访问令牌
        if auth_config.get('type') == 'basic':
            # 检查当前token是否有效
            if self._is_token_valid():
                return True
            
            # 尝试刷新token
            if self._refresh_token and self._refresh_access_token():
                return True
            
            # 重新登录获取token
            return self._login_with_credentials()
        
        return False
    
    def _get_all_apps(self, search: str = "") -> List[Dict[str, Any]]:
        """获取所有应用的基本信息（带缓存）"""
        import time
        
        # 如果有搜索条件，不使用缓存
        if search or not self._is_cache_valid():
            all_apps = []
            api_page = 1
            
            # 从配置获取分页大小
            pagination_config = self._get_api_params('pagination')
            api_page_size = pagination_config.get('api_page_size', 50)
            
            logging.info(f"重新获取所有应用列表...")
            
            while True:
                # 使用配置化的端点构建URL
                full_endpoint = self._build_apps_list_url(page=api_page, limit=api_page_size, search=search)
                
                apps_response = self._make_request('GET', full_endpoint)
                if not apps_response:
                    break
                
                current_apps = apps_response.get('data', [])
                has_more = apps_response.get('has_more', False)
                
                if not current_apps:
                    break
                
                # 获取所有应用，不筛选类型
                for app_item in current_apps:
                    app_id = app_item.get('id')
                    if app_id:
                        all_apps.append({
                            'id': app_id,
                            'name': app_item.get('name', f"应用 {app_id[:8]}"),
                            'description': app_item.get('description', ''),
                            'mode': app_item.get('mode', 'chat'),
                            'has_workflow_field': app_item.get('workflow') is not None
                        })
                
                if not has_more:
                    break
                
                api_page += 1
                if api_page > 20:  # 安全限制
                    break
            
            logging.info(f"获取到 {len(all_apps)} 个应用")
            
            # 只有在没有搜索条件时才缓存
            if not search:
                self._workflow_apps_cache = all_apps  # 复用缓存变量
                self._cache_timestamp = time.time()
            
            return all_apps
        else:
            logging.info(f"使用缓存的应用列表: {len(self._workflow_apps_cache)} 个")
            return self._workflow_apps_cache
    
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
    
    def _get_endpoint(self, endpoint_key: str, **kwargs) -> str:
        """从配置获取API端点并格式化参数"""
        api_config = self.config.get_api_config()
        endpoints = api_config.get('endpoints', {})
        
        endpoint_template = endpoints.get(endpoint_key)
        if not endpoint_template:
            raise ValueError(f"未找到端点配置: {endpoint_key}")
        
        # 格式化端点中的参数
        try:
            return endpoint_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"端点 {endpoint_key} 缺少必需参数: {e}")
    
    def _get_api_params(self, param_key: str) -> dict:
        """从配置获取API查询参数"""
        api_config = self.config.get_api_config()
        params = api_config.get('params', {})
        return params.get(param_key, {})
    
    def _build_apps_list_url(self, page: int = 1, limit: int = None, search: str = "") -> str:
        """构建应用列表API URL"""
        endpoint = self._get_endpoint('apps_list')
        
        # 获取默认参数
        default_params = self._get_api_params('apps_list')
        
        # 构建查询参数
        params = {
            'page': page,
            'limit': limit or default_params.get('limit', 50),
            'name': search or default_params.get('name', ''),
            'is_created_by_me': str(default_params.get('is_created_by_me', False)).lower()
        }
        
        # 构建完整URL，正确处理参数类型
        query_parts = []
        for k, v in params.items():
            if isinstance(v, bool):
                query_parts.append(f"{k}={str(v).lower()}")
            else:
                query_parts.append(f"{k}={v}")
        
        query_string = '&'.join(query_parts)
        full_url = f"{endpoint}?{query_string}"
        
        return full_url
    
    def _init_api_config(self):
        """初始化API配置"""
        if not self.config.is_api_enabled():
            # 在database模式下，设置默认值以避免属性错误
            self.base_url = None
            self.headers = {}
            self.timeout = 30
            return
        
        api_config = self.config.get_api_config()
        self.base_url = api_config['base_url'].rstrip('/')
        
        # 获取认证配置
        auth_config = api_config.get('auth', {})
        
        # 如果是basic认证，尝试登录获取token
        if auth_config.get('type') == 'basic':
            if self._login_with_credentials():
                # 使用获取的access_token
                self.headers = {"Authorization": f"Bearer {self._access_token}"}
                logging.info("使用自动登录获得的访问令牌")
            else:
                logging.error("自动登录失败，无法获取访问令牌")
                return
        else:
            # 使用配置的认证头
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
        
        # 确保token有效（如果使用basic认证）
        if not self._ensure_valid_token():
            logging.error("无法获取有效的访问令牌")
            return None
        
        # 如果使用basic认证且有access_token，更新Authorization头
        api_config = self.config.get_api_config()
        auth_config = api_config.get('auth', {})
        if auth_config.get('type') == 'basic' and self._access_token:
            self.session.headers['Authorization'] = f"Bearer {self._access_token}"
        
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
        
        try:
            # 使用配置化的端点
            endpoint = self._get_endpoint('app_detail', app_id=app_id)
            
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
                description=app_data.get('description', ''),
                created_at=app_data.get('created_at', ''),
                updated_at=app_data.get('updated_at', '')
            )
        except Exception as e:
            logging.error(f"获取应用信息失败: {e}")
            return None
    
    def get_workflow_by_app_id(self, app_id: str) -> Optional[Workflow]:
        """根据应用ID获取工作流信息"""
        if not self.config.is_api_enabled():
            return None
        
        try:
            # 使用配置化的端点
            endpoint = self._get_endpoint('workflow_draft', app_id=app_id)
        except ValueError as e:
            logging.error(f"获取工作流端点失败: {e}")
            return None

        try:
            # 获取工作流信息
            response = self._make_request('GET', endpoint)
            if not response:
                logging.warning(f"未找到应用ID为 {app_id} 的工作流")
                return None
            
            # 根据实际API响应格式调整
            workflow_data = response.get('data', response)
            
            # 获取应用信息以获取应用名称
            app_info = self.get_app_by_id(app_id)
            app_name = app_info.name if app_info else f"工作流 {app_id[:8]}"
            app_description = app_info.description if app_info else ""
            app_mode = app_info.mode if app_info else "workflow"
            
            # 获取环境变量
            environment_variables = self.get_environment_variables_by_app_id(app_id)
            
            return Workflow(
                id=workflow_data.get('id', ''),
                app_id=workflow_data.get('app_id', app_id),
                version=workflow_data.get('version', '1.0'),
                graph=workflow_data.get('graph', {}),
                features=workflow_data.get('features', {}),
                environment_variables=environment_variables,
                app_name=app_name,
                app_description=app_description,
                app_mode=app_mode
            )
        except Exception as e:
            logging.error(f"获取工作流信息失败: {e}")
            return None
    
    def get_all_workflows(self) -> List[Workflow]:
        """获取所有工作流（使用缓存优化）"""
        if not self.config.is_api_enabled():
            return []
        
        try:
            # 获取所有工作流应用的基本信息（使用缓存）
            workflow_apps = self._get_all_apps()
            
            logging.info(f"开始获取 {len(workflow_apps)} 个工作流的详细信息")
            
            workflows = []
            for i, app_info in enumerate(workflow_apps):
                if i <= 5 or i % 10 == 0:  # 只显示前5个和每10个的详细信息
                    logging.info(f"处理第 {i+1}/{len(workflow_apps)} 个工作流应用: {app_info['name']} ({app_info['id']})")
                
                try:
                    workflow = self.get_workflow_by_app_id(app_info['id'])
                    if workflow:
                        # 确保工作流包含应用名称信息
                        workflow.app_name = app_info['name']
                        workflow.app_description = app_info['description']
                        workflow.app_mode = app_info['mode']
                        workflows.append(workflow)
                        if i <= 5:  # 只显示前5个的成功信息
                            logging.info(f"成功获取工作流: {app_info['name']}")
                    else:
                        logging.warning(f"无法获取工作流详情: {app_info['name']} ({app_info['id']})")
                except Exception as e:
                    logging.error(f"获取工作流时出错: {app_info['name']} ({app_info['id']}) - {e}")
            
            logging.info(f"成功获取 {len(workflows)} 个有效工作流，共处理了 {len(workflow_apps)} 个工作流应用")
            return workflows
            
        except Exception as e:
            logging.error(f"获取所有工作流失败: {e}")
            return []
    
    def get_environment_variables_by_app_id(self, app_id: str) -> List[EnvironmentVariable]:
        """根据应用ID获取环境变量"""
        if not self.config.is_api_enabled():
            return []
        
        # 暂时禁用环境变量获取以避免404错误
        logging.info(f"跳过环境变量获取 (应用ID: {app_id})")
        return []
    
    def test_connection(self) -> dict:
        """测试API连接是否正常"""
        if not self.config.is_api_enabled():
            return {"success": False, "error": "API未启用"}
        
        try:
            # 尝试获取第一页应用列表来测试连接
            endpoint = self._build_apps_list_url(page=1, limit=1)
            response = self._make_request('GET', endpoint)
            
            if response is not None:
                return {
                    "success": True, 
                    "message": "API连接测试成功",
                    "data": {
                        "total_apps": response.get('total', 0),
                        "endpoint": endpoint
                    }
                }
            else:
                return {
                    "success": False, 
                    "error": "API响应为空，请检查URL和认证信息"
                }
        except Exception as e:
            return {
                "success": False, 
                "error": f"API连接测试失败: {str(e)}"
            }
    
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
        高效分页获取应用列表（带缓存优化）- 显示所有应用类型
        :param page: 页码（从1开始）
        :param page_size: 每页数量
        :param search: 搜索关键词
        :return: 包含应用列表和总数的字典
        """
        if not self.config.is_api_enabled():
            return {"workflows": [], "total": 0}
        
        try:
            # 获取所有应用的基本信息（使用缓存）
            all_apps = self._get_all_apps(search)
            
            # 如果有搜索条件，进行本地过滤
            if search:
                search_lower = search.lower()
                filtered_apps = []
                for app in all_apps:
                    if (search_lower in app['name'].lower() or 
                        search_lower in app['id'].lower() or
                        search_lower in app['description'].lower()):
                        filtered_apps.append(app)
                all_apps = filtered_apps
            
            total_app_count = len(all_apps)
            logging.info(f"应用总数: {total_app_count}")
            
            # 计算分页范围
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_app_count)
            current_page_apps = all_apps[start_idx:end_idx]
            
            logging.info(f"获取第 {page} 页应用，范围: {start_idx}-{end_idx}")
            
            # 直接构造应用数据，不获取详细工作流信息
            apps = []
            for app_info in current_page_apps:
                try:
                    # 判断应用类型
                    app_mode = app_info['mode']
                    has_workflow = app_info['has_workflow_field']
                    is_workflow = (app_mode == 'workflow') or (app_mode == 'advanced-chat' and has_workflow)
                    
                    # 构造简化的工作流对象
                    from models.app import Workflow
                    workflow = Workflow(
                        id=app_info['id'],
                        app_id=app_info['id'],
                        version='draft',
                        graph={},
                        features={},
                        environment_variables=[],
                        app_name=app_info['name'],
                        app_description=app_info['description'],
                        app_mode=app_mode,
                        # 添加应用类型信息
                        is_workflow=is_workflow
                    )
                    apps.append(workflow)
                    
                except Exception as e:
                    logging.error(f"构造应用数据失败: {app_info['name']} ({app_info['id']}) - {e}")
            
            logging.info(f"分页获取完成: 第{page}页获取到 {len(apps)} 个应用，总计 {total_app_count} 个应用")
            
            return {
                "workflows": apps,
                "total": total_app_count
            }
            
        except Exception as e:
            logging.error(f"分页获取应用失败: {e}")
            return {"workflows": [], "total": 0}
    
    def clear_cache(self):
        """清除缓存，强制重新获取数据"""
        self._workflow_apps_cache = None
        self._cache_timestamp = None
        logging.info("API连接器缓存已清除")
    
    def close(self):
        """关闭API连接器"""
        if self.session:
            self.session.close()
            logging.info("API连接器已关闭")


# 全局API连接器实例
api_connector = APIConnector() 