"""
数据库配置服务
负责从MySQL数据库读取和管理系统配置
"""
import json
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from models.config_models import (
    Base,
    SystemConfig,
    TargetInstance,
    ApiEndpoint,
    DatabaseConnection,
    DatabaseTableMapping
)

logger = logging.getLogger(__name__)


class DatabaseConfigService:
    """数据库配置服务类"""
    
    def __init__(self, db_url: str):
        """初始化数据库连接
        
        Args:
            db_url: 数据库连接URL，格式：mysql+pymysql://user:password@host:port/database
        """
        self.db_url = db_url
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化数据库引擎"""
        try:
            self.engine = create_engine(
                self.db_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                echo=False
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("数据库引擎初始化成功")
        except Exception as e:
            logger.error(f"数据库引擎初始化失败: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """获取数据库会话（上下文管理器）"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """创建所有表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    # ==================== 系统配置相关方法 ====================
    
    def get_system_config(self, config_key: str, default=None) -> Any:
        """获取系统配置值
        
        Args:
            config_key: 配置键
            default: 默认值
            
        Returns:
            配置值（已根据类型解析）
        """
        with self.get_session() as session:
            config = session.query(SystemConfig).filter_by(config_key=config_key).first()
            if not config:
                return default
            
            # 根据类型解析配置值
            try:
                if config.config_type == 'json':
                    return json.loads(config.config_value) if config.config_value else default
                elif config.config_type == 'number':
                    return int(config.config_value) if config.config_value else default
                elif config.config_type == 'boolean':
                    return config.config_value.lower() == 'true' if config.config_value else default
                else:  # string
                    # 移除JSON字符串的引号
                    value = config.config_value
                    if value and value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    return value if value else default
            except Exception as e:
                logger.error(f"解析配置值失败 {config_key}: {e}")
                return default
    
    def set_system_config(self, config_key: str, config_value: Any, config_type: str = 'string', 
                         description: str = None, is_sensitive: bool = False):
        """设置系统配置
        
        Args:
            config_key: 配置键
            config_value: 配置值
            config_type: 配置类型
            description: 配置描述
            is_sensitive: 是否为敏感信息
        """
        with self.get_session() as session:
            # 将值转换为字符串存储
            if config_type == 'json':
                value_str = json.dumps(config_value, ensure_ascii=False)
            elif config_type == 'boolean':
                value_str = 'true' if config_value else 'false'
            elif config_type == 'string':
                # 字符串类型存储为JSON字符串格式
                value_str = json.dumps(config_value, ensure_ascii=False)
            else:
                value_str = str(config_value)
            
            config = session.query(SystemConfig).filter_by(config_key=config_key).first()
            if config:
                config.config_value = value_str
                if description:
                    config.description = description
            else:
                config = SystemConfig(
                    config_key=config_key,
                    config_value=value_str,
                    config_type=config_type,
                    description=description,
                    is_sensitive=is_sensitive
                )
                session.add(config)
    
    def get_all_system_configs(self) -> Dict[str, Any]:
        """获取所有系统配置"""
        with self.get_session() as session:
            configs = session.query(SystemConfig).all()
            result = {}
            for config in configs:
                try:
                    if config.config_type == 'json':
                        result[config.config_key] = json.loads(config.config_value) if config.config_value else None
                    elif config.config_type == 'number':
                        result[config.config_key] = int(config.config_value) if config.config_value else 0
                    elif config.config_type == 'boolean':
                        result[config.config_key] = config.config_value.lower() == 'true' if config.config_value else False
                    else:
                        value = config.config_value
                        if value and value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        result[config.config_key] = value
                except Exception as e:
                    logger.error(f"解析配置 {config.config_key} 失败: {e}")
                    result[config.config_key] = None
            return result
    
    # ==================== 目标实例相关方法 ====================
    
    def get_target_instances(self, include_inactive=False) -> List[Dict[str, Any]]:
        """获取所有目标实例
        
        Args:
            include_inactive: 是否包含未启用的实例
            
        Returns:
            目标实例列表
        """
        with self.get_session() as session:
            query = session.query(TargetInstance)
            if not include_inactive:
                query = query.filter_by(is_active=True)
            
            instances = query.all()
            return [inst.to_dict(include_sensitive=True) for inst in instances]
    
    def get_target_instance_by_id(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取目标实例
        
        Args:
            instance_id: 实例ID
            
        Returns:
            目标实例信息或None
        """
        with self.get_session() as session:
            instance = session.query(TargetInstance).filter_by(id=instance_id).first()
            return instance.to_dict(include_sensitive=True) if instance else None
    
    def create_target_instance(self, instance_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建目标实例
        
        Args:
            instance_data: 实例数据
            
        Returns:
            创建的实例信息
        """
        with self.get_session() as session:
            # 如果设置为默认实例，先取消其他实例的默认状态
            if instance_data.get('is_default'):
                session.query(TargetInstance).update({'is_default': False})
            
            # 提取认证信息
            auth = instance_data.get('auth', {})
            auth_type = auth.get('type', 'bearer')
            
            instance = TargetInstance(
                id=instance_data['id'],
                name=instance_data['name'],
                url=instance_data['url'],
                auth_type=auth_type,
                auth_token=auth.get('token') if auth_type == 'bearer' else None,
                auth_username=auth.get('username') if auth_type == 'basic' else None,
                auth_password=auth.get('password') if auth_type == 'basic' else None,
                auth_api_key=auth.get('api_key') if auth_type == 'api_key' else None,
                auth_api_key_header=auth.get('api_key_header', 'X-API-Key') if auth_type == 'api_key' else 'X-API-Key',
                is_default=instance_data.get('is_default', False),
                is_active=instance_data.get('is_active', True),
                description=instance_data.get('description')
            )
            session.add(instance)
            session.flush()
            return instance.to_dict(include_sensitive=True)
    
    def update_target_instance(self, instance_id: str, instance_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新目标实例
        
        Args:
            instance_id: 实例ID
            instance_data: 更新的数据
            
        Returns:
            更新后的实例信息或None
        """
        with self.get_session() as session:
            instance = session.query(TargetInstance).filter_by(id=instance_id).first()
            if not instance:
                return None
            
            # 如果设置为默认实例，先取消其他实例的默认状态
            if instance_data.get('is_default') and not instance.is_default:
                session.query(TargetInstance).filter(TargetInstance.id != instance_id).update({'is_default': False})
            
            # 更新基本信息
            if 'name' in instance_data:
                instance.name = instance_data['name']
            if 'url' in instance_data:
                instance.url = instance_data['url']
            if 'is_default' in instance_data:
                instance.is_default = instance_data['is_default']
            if 'is_active' in instance_data:
                instance.is_active = instance_data['is_active']
            if 'description' in instance_data:
                instance.description = instance_data['description']
            
            # 更新认证信息
            if 'auth' in instance_data:
                auth = instance_data['auth']
                auth_type = auth.get('type', instance.auth_type)
                instance.auth_type = auth_type
                
                # 清空所有认证字段
                instance.auth_token = None
                instance.auth_username = None
                instance.auth_password = None
                instance.auth_api_key = None
                
                # 根据类型设置相应字段
                if auth_type == 'bearer':
                    instance.auth_token = auth.get('token')
                elif auth_type == 'basic':
                    instance.auth_username = auth.get('username')
                    instance.auth_password = auth.get('password')
                elif auth_type == 'api_key':
                    instance.auth_api_key = auth.get('api_key')
                    instance.auth_api_key_header = auth.get('api_key_header', 'X-API-Key')
            
            session.flush()
            return instance.to_dict(include_sensitive=True)
    
    def delete_target_instance(self, instance_id: str) -> bool:
        """删除目标实例
        
        Args:
            instance_id: 实例ID
            
        Returns:
            是否删除成功
        """
        with self.get_session() as session:
            instance = session.query(TargetInstance).filter_by(id=instance_id).first()
            if not instance:
                return False
            session.delete(instance)
            return True
    
    # ==================== API端点相关方法 ====================
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """获取所有API端点配置
        
        Returns:
            端点键值对字典
        """
        with self.get_session() as session:
            endpoints = session.query(ApiEndpoint).filter_by(is_active=True).all()
            return {ep.endpoint_key: ep.endpoint_path for ep in endpoints}
    
    def get_api_endpoint(self, endpoint_key: str) -> Optional[str]:
        """获取指定API端点
        
        Args:
            endpoint_key: 端点键名
            
        Returns:
            端点路径或None
        """
        with self.get_session() as session:
            endpoint = session.query(ApiEndpoint).filter_by(endpoint_key=endpoint_key, is_active=True).first()
            return endpoint.endpoint_path if endpoint else None
    
    def set_api_endpoint(self, endpoint_key: str, endpoint_path: str, description: str = None):
        """设置API端点
        
        Args:
            endpoint_key: 端点键名
            endpoint_path: 端点路径
            description: 端点描述
        """
        with self.get_session() as session:
            endpoint = session.query(ApiEndpoint).filter_by(endpoint_key=endpoint_key).first()
            if endpoint:
                endpoint.endpoint_path = endpoint_path
                if description:
                    endpoint.description = description
            else:
                endpoint = ApiEndpoint(
                    endpoint_key=endpoint_key,
                    endpoint_path=endpoint_path,
                    description=description
                )
                session.add(endpoint)
    
    # ==================== 数据库连接相关方法 ====================
    
    def get_database_connections(self, include_inactive=False) -> List[Dict[str, Any]]:
        """获取所有数据库连接配置
        
        Args:
            include_inactive: 是否包含未启用的连接
            
        Returns:
            数据库连接列表
        """
        with self.get_session() as session:
            query = session.query(DatabaseConnection)
            if not include_inactive:
                query = query.filter_by(is_active=True)
            
            connections = query.all()
            return [conn.to_dict(include_sensitive=True) for conn in connections]
    
    def get_database_connection_by_name(self, connection_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取数据库连接
        
        Args:
            connection_name: 连接名称
            
        Returns:
            数据库连接信息或None
        """
        with self.get_session() as session:
            connection = session.query(DatabaseConnection).filter_by(connection_name=connection_name).first()
            return connection.to_dict(include_sensitive=True) if connection else None
    
    # ==================== 完整配置相关方法 ====================
    
    def get_full_config(self) -> Dict[str, Any]:
        """获取完整的系统配置
        
        Returns:
            完整配置字典，结构与原config.yaml相同
        """
        # 获取所有系统配置
        sys_configs = self.get_all_system_configs()
        
        # 获取API端点
        endpoints = self.get_api_endpoints()
        
        # 获取目标实例
        instances = self.get_target_instances()
        
        # 获取数据库连接
        db_connections = self.get_database_connections()
        
        # 构建完整配置结构
        config = {
            'data_source': sys_configs.get('data_source', 'api'),
            'api': {
                'base_url': sys_configs.get('api_base_url', ''),
                'auth': {
                    'type': sys_configs.get('api_auth_type', 'bearer'),
                    'token': sys_configs.get('api_bearer_token', ''),
                    'username': sys_configs.get('api_basic_username', ''),
                    'password': sys_configs.get('api_basic_password', ''),
                    'api_key': sys_configs.get('api_key_value', ''),
                    'api_key_header': sys_configs.get('api_key_header', 'X-API-Key')
                },
                'endpoints': endpoints,
                'params': {
                    'apps_list': {
                        'name': '',
                        'is_created_by_me': False,
                        'page': 1,
                        'limit': sys_configs.get('pagination_api_page_size', 50)
                    },
                    'pagination': {
                        'default_page_size': sys_configs.get('pagination_default_page_size', 20),
                        'max_page_size': sys_configs.get('pagination_max_page_size', 100),
                        'api_page_size': sys_configs.get('pagination_api_page_size', 50)
                    }
                },
                'timeout': sys_configs.get('api_timeout', 30),
                'retry_count': sys_configs.get('api_retry_count', 3),
                'retry_delay': sys_configs.get('api_retry_delay', 1)
            },
            'database': {},
            'export': {
                'default_format': sys_configs.get('export_default_format', 'yaml')
            },
            'logging': {
                'level': sys_configs.get('logging_level', 'INFO'),
                'file': sys_configs.get('logging_file', 'logs/app.log'),
                'max_size': sys_configs.get('logging_max_size', '10MB'),
                'backup_count': sys_configs.get('logging_backup_count', 5),
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'cache': {
                'enabled': sys_configs.get('cache_enabled', True),
                'ttl': sys_configs.get('cache_ttl', 300)
            },
            'target_instances': instances
        }
        
        # 如果有数据库连接配置，添加到配置中
        if db_connections:
            # 这里简化处理，只取第一个活跃的连接
            db_conn = db_connections[0]
            config['database'] = {
                'type': db_conn.get('db_type', 'postgresql'),
                'host': db_conn.get('host', ''),
                'port': db_conn.get('port', 5432),
                'database': db_conn.get('database_name', ''),
                'username': db_conn.get('username', ''),
                'password': '',  # 敏感信息不返回
                'ssl_mode': db_conn.get('ssl_mode', 'prefer'),
                'pool_size': db_conn.get('pool_size', 10),
                'max_overflow': db_conn.get('max_overflow', 20),
                'pool_timeout': db_conn.get('pool_timeout', 30),
                'tables': {}
            }
        
        return config
    
    def update_full_config(self, config_data: Dict[str, Any]):
        """更新完整配置
        
        Args:
            config_data: 配置数据
        """
        with self.get_session() as session:
            # 更新系统配置
            if 'data_source' in config_data:
                self.set_system_config('data_source', config_data['data_source'], 'string')
            
            # 更新API配置
            if 'api' in config_data:
                api_config = config_data['api']
                if 'base_url' in api_config:
                    self.set_system_config('api_base_url', api_config['base_url'], 'string')
                if 'auth' in api_config:
                    auth = api_config['auth']
                    if 'type' in auth:
                        self.set_system_config('api_auth_type', auth['type'], 'string')
                    # 保存认证token/credentials（敏感信息）
                    if 'token' in auth and auth['token']:
                        self.set_system_config('api_bearer_token', auth['token'], 'string', '​Bearer Token', is_sensitive=True)
                    if 'username' in auth:
                        self.set_system_config('api_basic_username', auth['username'], 'string', 'Basic认证用户名')
                    if 'password' in auth and auth['password']:
                        self.set_system_config('api_basic_password', auth['password'], 'string', 'Basic认证密码', is_sensitive=True)
                    if 'api_key' in auth and auth['api_key']:
                        self.set_system_config('api_key_value', auth['api_key'], 'string', 'API Key', is_sensitive=True)
                    if 'api_key_header' in auth:
                        self.set_system_config('api_key_header', auth['api_key_header'], 'string', 'API Key Header名称')
                if 'timeout' in api_config:
                    self.set_system_config('api_timeout', api_config['timeout'], 'number')
                if 'retry_count' in api_config:
                    self.set_system_config('api_retry_count', api_config['retry_count'], 'number')
                if 'retry_delay' in api_config:
                    self.set_system_config('api_retry_delay', api_config['retry_delay'], 'number')
                
                # 更新API端点
                if 'endpoints' in api_config:
                    for key, path in api_config['endpoints'].items():
                        self.set_api_endpoint(key, path)
                
                # 更新分页配置
                if 'params' in api_config and 'pagination' in api_config['params']:
                    pagination = api_config['params']['pagination']
                    if 'default_page_size' in pagination:
                        self.set_system_config('pagination_default_page_size', pagination['default_page_size'], 'number')
                    if 'max_page_size' in pagination:
                        self.set_system_config('pagination_max_page_size', pagination['max_page_size'], 'number')
                    if 'api_page_size' in pagination:
                        self.set_system_config('pagination_api_page_size', pagination['api_page_size'], 'number')
            
            # 更新导出配置
            if 'export' in config_data and 'default_format' in config_data['export']:
                self.set_system_config('export_default_format', config_data['export']['default_format'], 'string')
            
            # 更新日志配置
            if 'logging' in config_data:
                logging_config = config_data['logging']
                if 'level' in logging_config:
                    self.set_system_config('logging_level', logging_config['level'], 'string')
                if 'file' in logging_config:
                    self.set_system_config('logging_file', logging_config['file'], 'string')
                if 'max_size' in logging_config:
                    self.set_system_config('logging_max_size', logging_config['max_size'], 'string')
                if 'backup_count' in logging_config:
                    self.set_system_config('logging_backup_count', logging_config['backup_count'], 'number')
            
            # 更新缓存配置
            if 'cache' in config_data:
                cache_config = config_data['cache']
                if 'enabled' in cache_config:
                    self.set_system_config('cache_enabled', cache_config['enabled'], 'boolean')
                if 'ttl' in cache_config:
                    self.set_system_config('cache_ttl', cache_config['ttl'], 'number')
            
            # 更新目标实例（这里不处理，通过专门的API处理）
            # target_instances 通过 create_target_instance/update_target_instance 处理

