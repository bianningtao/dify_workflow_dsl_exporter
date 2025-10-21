"""
配置服务 - 从MySQL数据库读取配置
所有配置都存储在数据库中，提供统一的配置访问接口
"""
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from services.db_config_loader import get_database_url
from services.database_config_service import DatabaseConfigService

logger = logging.getLogger(__name__)


class ConfigService:
    """配置服务类，负责从数据库读取和管理配置"""
    
    _instance = None
    _db_service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._db_service is None:
            self._initialize_db_service()
    
    def _initialize_db_service(self):
        """初始化数据库服务"""
        try:
            db_url = get_database_url()
            self._db_service = DatabaseConfigService(db_url)
            logger.info("配置服务初始化成功（数据库模式）")
        except Exception as e:
            logger.error(f"配置服务初始化失败: {e}")
            raise RuntimeError(f"无法连接到配置数据库: {e}")
    
    def reload_config(self):
        """重新加载配置（重新初始化数据库连接）"""
        self._initialize_db_service()
    
    # ==================== 数据源配置 ====================
    
    def get_data_source(self) -> str:
        """获取数据源类型"""
        return self._db_service.get_system_config('data_source', 'api')
    
    # ==================== API配置 ====================
    
    def is_api_enabled(self) -> bool:
        """检查数据源是否为API"""
        return self.get_data_source() == 'api'
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置
        
        Returns:
            API配置字典，包含 base_url, auth, timeout 等
        """
        auth_type = self.get_api_auth_type()
        auth_config = {'type': auth_type}
        
        # 根据认证类型添加相应的认证信息
        if auth_type == 'bearer':
            auth_config['token'] = self._db_service.get_system_config('api_bearer_token', '')
        elif auth_type == 'basic':
            auth_config['username'] = self._db_service.get_system_config('api_basic_username', '')
            auth_config['password'] = self._db_service.get_system_config('api_basic_password', '')
        elif auth_type == 'api_key':
            auth_config['api_key'] = self._db_service.get_system_config('api_key_value', '')
            auth_config['api_key_header'] = self._db_service.get_system_config('api_key_header', 'X-API-Key')
        
        return {
            'base_url': self.get_api_base_url(),
            'auth': auth_config,
            'endpoints': self.get_api_endpoints(),
            'params': {
                'apps_list': {
                    'name': '',
                    'is_created_by_me': False,
                    'page': 1,
                    'limit': self.get_api_page_size()
                },
                'pagination': {
                    'default_page_size': self.get_default_page_size(),
                    'max_page_size': self.get_max_page_size(),
                    'api_page_size': self.get_api_page_size()
                }
            },
            'timeout': self.get_api_timeout(),
            'retry_count': self.get_api_retry_count(),
            'retry_delay': self.get_api_retry_delay()
        }
    
    def get_api_base_url(self) -> str:
        """获取API基础URL"""
        return self._db_service.get_system_config('api_base_url', '')
    
    def get_api_auth_type(self) -> str:
        """获取API认证类型"""
        return self._db_service.get_system_config('api_auth_type', 'bearer')
    
    def get_api_timeout(self) -> int:
        """获取API超时时间"""
        return self._db_service.get_system_config('api_timeout', 30)
    
    def get_api_retry_count(self) -> int:
        """获取API重试次数"""
        return self._db_service.get_system_config('api_retry_count', 3)
    
    def get_api_retry_delay(self) -> int:
        """获取API重试延迟"""
        return self._db_service.get_system_config('api_retry_delay', 1)
    
    def get_api_endpoint(self, endpoint_key: str) -> str:
        """获取API端点路径
        
        Args:
            endpoint_key: 端点键名
            
        Returns:
            端点路径
        """
        return self._db_service.get_api_endpoint(endpoint_key) or ''
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """获取所有API端点"""
        return self._db_service.get_api_endpoints()
    
    def get_full_api_url(self, endpoint_key: str, instance_id: Optional[str] = None) -> str:
        """获取完整的API URL
        
        Args:
            endpoint_key: 端点键名
            instance_id: 目标实例ID（可选）
            
        Returns:
            完整的API URL
        """
        # 如果指定了目标实例，使用目标实例的URL
        if instance_id:
            instance = self.get_target_instance_by_id(instance_id)
            if instance:
                base_url = instance.get('url', '').rstrip('/')
            else:
                base_url = self.get_api_base_url().rstrip('/')
        else:
            base_url = self.get_api_base_url().rstrip('/')
        
        endpoint_path = self.get_api_endpoint(endpoint_key)
        if not endpoint_path:
            raise ValueError(f"未找到端点配置: {endpoint_key}")
        
        return f"{base_url}{endpoint_path}"
    
    def get_api_headers(self, instance_id: Optional[str] = None) -> Dict[str, str]:
        """获取API请求头
        
        Args:
            instance_id: 目标实例ID（可选）
            
        Returns:
            请求头字典
        """
        headers = {'Content-Type': 'application/json'}
        
        # 如果指定了目标实例，使用目标实例的认证信息
        if instance_id:
            return self.get_target_instance_headers(instance_id)
        
        # 否则使用默认API配置的认证信息
        auth_type = self.get_api_auth_type()
        
        if auth_type == 'bearer':
            token = self._db_service.get_system_config('api_bearer_token', '')
            if token:
                headers['Authorization'] = f'Bearer {token}'
        elif auth_type == 'basic':
            username = self._db_service.get_system_config('api_basic_username', '')
            password = self._db_service.get_system_config('api_basic_password', '')
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
        elif auth_type == 'api_key':
            api_key = self._db_service.get_system_config('api_key_value', '')
            api_key_header = self._db_service.get_system_config('api_key_header', 'X-API-Key')
            if api_key:
                headers[api_key_header] = api_key
        
        return headers
    
    # ==================== 分页配置 ====================
    
    def get_default_page_size(self) -> int:
        """获取默认分页大小"""
        return self._db_service.get_system_config('pagination_default_page_size', 20)
    
    def get_max_page_size(self) -> int:
        """获取最大分页大小"""
        return self._db_service.get_system_config('pagination_max_page_size', 100)
    
    def get_api_page_size(self) -> int:
        """获取API分页大小"""
        return self._db_service.get_system_config('pagination_api_page_size', 50)
    
    # ==================== 导出配置 ====================
    
    def get_export_default_format(self) -> str:
        """获取默认导出格式"""
        return self._db_service.get_system_config('export_default_format', 'yaml')
    
    # ==================== 日志配置 ====================
    
    def get_logging_level(self) -> str:
        """获取日志级别"""
        return self._db_service.get_system_config('logging_level', 'INFO')
    
    def get_logging_file(self) -> str:
        """获取日志文件路径"""
        return self._db_service.get_system_config('logging_file', 'logs/app.log')
    
    # ==================== 缓存配置 ====================
    
    def is_cache_enabled(self) -> bool:
        """是否启用缓存"""
        return self._db_service.get_system_config('cache_enabled', True)
    
    def get_cache_ttl(self) -> int:
        """获取缓存过期时间"""
        return self._db_service.get_system_config('cache_ttl', 300)
    
    # ==================== 目标实例配置 ====================
    
    def get_target_instances(self) -> List[Dict[str, Any]]:
        """获取所有目标实例配置"""
        return self._db_service.get_target_instances(include_inactive=False)
    
    def get_target_instance_by_id(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取目标实例配置
        
        Args:
            instance_id: 实例ID
            
        Returns:
            实例配置字典或None
        """
        return self._db_service.get_target_instance_by_id(instance_id)
    
    def get_target_instance_headers(self, instance_id: str) -> Dict[str, str]:
        """获取目标实例的请求头
        
        Args:
            instance_id: 实例ID
            
        Returns:
            请求头字典
        """
        instance = self.get_target_instance_by_id(instance_id)
        if not instance:
            raise ValueError(f"未找到目标实例: {instance_id}")
        
        headers = {'Content-Type': 'application/json'}
        auth = instance.get('auth', {})
        auth_type = auth.get('type', 'bearer')
        
        if auth_type == 'bearer':
            token = auth.get('token', '')
            if token:
                headers['Authorization'] = f'Bearer {token}'
        elif auth_type == 'basic':
            username = auth.get('username', '')
            password = auth.get('password', '')
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
        elif auth_type == 'api_key':
            api_key = auth.get('api_key', '')
            api_key_header = auth.get('api_key_header', 'X-API-Key')
            if api_key:
                headers[api_key_header] = api_key
        
        return headers
    
    # ==================== 数据库配置 ====================
    
    def is_database_enabled(self) -> bool:
        """检查数据源是否为数据库"""
        return self.get_data_source() == 'database'
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置
        
        Returns:
            数据库配置字典，包含 host, port, database, username, password 等
        """
        # 获取主数据库连接（通常是第一个或默认的）
        connections = self.get_database_connections()
        if connections:
            # 返回第一个活跃的数据库连接
            conn = connections[0]
            return {
                'host': conn.get('host', 'localhost'),
                'port': conn.get('port', 5432),
                'database': conn.get('database', ''),
                'username': conn.get('username', ''),
                'password': conn.get('password', ''),
                'ssl_mode': conn.get('ssl_mode', 'prefer'),
                'pool_size': conn.get('pool_size', 10),
                'pool_timeout': conn.get('pool_timeout', 30)
            }
        return {}
    
    def get_database_connections(self) -> List[Dict[str, Any]]:
        """获取所有数据库连接配置"""
        return self._db_service.get_database_connections(include_inactive=False)
    
    def get_database_connection_by_name(self, connection_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取数据库连接配置
        
        Args:
            connection_name: 连接名称
            
        Returns:
            连接配置字典或None
        """
        return self._db_service.get_database_connection_by_name(connection_name)
    
    # ==================== 完整配置 ====================
    
    def get_full_config(self) -> Dict[str, Any]:
        """获取完整的系统配置
        
        Returns:
            完整配置字典
        """
        return self._db_service.get_full_config()
    
    def update_full_config(self, config_data: Dict[str, Any]):
        """更新完整配置
        
        Args:
            config_data: 配置数据
        """
        self._db_service.update_full_config(config_data)
    
    # ==================== 系统配置 ====================
    
    def get_system_config(self, config_key: str, default=None) -> Any:
        """获取系统配置值
        
        Args:
            config_key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self._db_service.get_system_config(config_key, default)
    
    def set_system_config(self, config_key: str, config_value: Any, 
                         config_type: str = 'string', description: str = None):
        """设置系统配置
        
        Args:
            config_key: 配置键
            config_value: 配置值
            config_type: 配置类型
            description: 配置描述
        """
        self._db_service.set_system_config(config_key, config_value, config_type, description)
    
    # ==================== 目标实例管理 ====================
    
    def create_target_instance(self, instance_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建目标实例
        
        Args:
            instance_data: 实例数据
            
        Returns:
            创建的实例信息
        """
        return self._db_service.create_target_instance(instance_data)
    
    def update_target_instance(self, instance_id: str, instance_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新目标实例
        
        Args:
            instance_id: 实例ID
            instance_data: 更新的数据
            
        Returns:
            更新后的实例信息或None
        """
        return self._db_service.update_target_instance(instance_id, instance_data)
    
    def delete_target_instance(self, instance_id: str) -> bool:
        """删除目标实例
        
        Args:
            instance_id: 实例ID
            
        Returns:
            是否删除成功
        """
        return self._db_service.delete_target_instance(instance_id)
    
    # ==================== API端点管理 ====================
    
    def set_api_endpoint(self, endpoint_key: str, endpoint_path: str, description: str = None):
        """设置API端点
        
        Args:
            endpoint_key: 端点键名
            endpoint_path: 端点路径
            description: 端点描述
        """
        self._db_service.set_api_endpoint(endpoint_key, endpoint_path, description)
    
    # ==================== 工具方法 ====================
    
    def create_data_directories(self):
        """创建必要的数据目录"""
        import os
        from pathlib import Path
        
        # 创建日志目录
        log_file = self.get_logging_file()
        log_dir = Path(log_file).parent
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建日志目录: {log_dir}")
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置
        
        Returns:
            日志配置字典
        """
        return {
            'level': self.get_logging_level(),
            'file': self.get_logging_file(),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'max_size': self.get_system_config('logging_max_size', '10MB'),
            'backup_count': self.get_system_config('logging_backup_count', 5)
        }


# 全局配置服务实例
config = ConfigService()
