"""
用户配置服务
管理基于用户的独立配置
"""
import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from models.user import UserSystemConfig, UserTargetInstance, UserDatabaseConnection
from models.config_models import ApiEndpoint  # 使用全局API端点表
from services.db_config_loader import get_database_url

logger = logging.getLogger(__name__)


class UserConfigService:
    """用户配置服务 - 管理每个用户独立的配置"""
    
    def __init__(self):
        """初始化用户配置服务"""
        db_url = get_database_url()
        self.engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("用户配置服务初始化成功")
    
    @contextmanager
    def get_session(self) -> Session:
        """获取数据库会话"""
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
    
    # ==================== 系统配置 ====================
    
    def get_user_config(self, user_id: str, config_key: str, default=None) -> Any:
        """获取用户配置值
        
        Args:
            user_id: 用户ID
            config_key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        with self.get_session() as session:
            config = session.query(UserSystemConfig).filter_by(
                user_id=user_id,
                config_key=config_key
            ).first()
            
            if not config:
                return default
            
            try:
                # 根据类型转换值
                if config.config_type.value == 'json':
                    return json.loads(config.config_value) if config.config_value else default
                elif config.config_type.value == 'number':
                    return int(config.config_value) if config.config_value else default
                elif config.config_type.value == 'boolean':
                    return config.config_value.lower() == 'true' if config.config_value else default
                else:  # string
                    return config.config_value if config.config_value else default
            except Exception as e:
                logger.error(f"解析配置失败 {config_key}: {e}")
                return default
    
    def set_user_config(self, user_id: str, config_key: str, config_value: Any, 
                        config_type: str = 'string', description: str = None,
                        is_sensitive: bool = False):
        """设置用户配置
        
        Args:
            user_id: 用户ID
            config_key: 配置键
            config_value: 配置值
            config_type: 配置类型
            description: 配置描述
            is_sensitive: 是否敏感信息
        """
        with self.get_session() as session:
            # 查找现有配置
            config = session.query(UserSystemConfig).filter_by(
                user_id=user_id,
                config_key=config_key
            ).first()
            
            # 转换值为字符串
            if config_type == 'json':
                value_str = json.dumps(config_value) if config_value is not None else ''
            elif config_type == 'boolean':
                value_str = 'true' if config_value else 'false'
            else:
                value_str = str(config_value) if config_value is not None else ''
            
            if config:
                # 更新现有配置
                config.config_value = value_str
                if config_type:
                    config.config_type = config_type
                if description:
                    config.description = description
                config.is_sensitive = is_sensitive
            else:
                # 创建新配置
                config = UserSystemConfig(
                    user_id=user_id,
                    config_key=config_key,
                    config_value=value_str,
                    config_type=config_type,
                    description=description,
                    is_sensitive=is_sensitive
                )
                session.add(config)
            
            logger.debug(f"设置用户配置: user={user_id}, key={config_key}")
    
    def get_all_user_configs(self, user_id: str) -> Dict[str, Any]:
        """获取用户所有配置
        
        Args:
            user_id: 用户ID
            
        Returns:
            配置字典
        """
        with self.get_session() as session:
            configs = session.query(UserSystemConfig).filter_by(user_id=user_id).all()
            
            result = {}
            for config in configs:
                try:
                    if config.config_type.value == 'json':
                        result[config.config_key] = json.loads(config.config_value) if config.config_value else None
                    elif config.config_type.value == 'number':
                        result[config.config_key] = int(config.config_value) if config.config_value else 0
                    elif config.config_type.value == 'boolean':
                        result[config.config_key] = config.config_value.lower() == 'true' if config.config_value else False
                    else:
                        result[config.config_key] = config.config_value
                except Exception as e:
                    logger.error(f"解析配置 {config.config_key} 失败: {e}")
                    result[config.config_key] = None
            
            return result
    
    # ==================== 目标实例配置 ====================
    
    def get_user_target_instances(self, user_id: str, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """获取用户的目标实例列表
        
        Args:
            user_id: 用户ID
            include_inactive: 是否包含未启用的实例
            
        Returns:
            实例列表
        """
        with self.get_session() as session:
            query = session.query(UserTargetInstance).filter_by(user_id=user_id)
            if not include_inactive:
                query = query.filter_by(is_active=True)
            
            instances = query.all()
            
            result = []
            for instance in instances:
                auth_config = json.loads(instance.auth_config) if instance.auth_config else {}
                # 获取auth_type的值（处理枚举和字符串两种情况）
                auth_type_value = instance.auth_type.value if hasattr(instance.auth_type, 'value') else instance.auth_type
                result.append({
                    'id': instance.id,
                    'name': instance.instance_name,
                    'url': instance.instance_url,
                    'auth': {
                        'type': auth_type_value,
                        **auth_config
                    },
                    'description': instance.description,
                    'is_active': instance.is_active
                })
            
            return result
    
    def create_user_target_instance(self, user_id: str, instance_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户目标实例
        
        Args:
            user_id: 用户ID
            instance_data: 实例数据
            
        Returns:
            创建的实例信息
        """
        import uuid
        
        with self.get_session() as session:
            auth_config = instance_data.get('auth', {})
            auth_type = auth_config.get('type', 'bearer')
            
            # 移除type字段，其余作为配置
            auth_config_data = {k: v for k, v in auth_config.items() if k != 'type'}
            
            instance = UserTargetInstance(
                id=instance_data.get('id', str(uuid.uuid4())),
                user_id=user_id,
                instance_name=instance_data['name'],
                instance_url=instance_data['url'],
                auth_type=auth_type,
                auth_config=json.dumps(auth_config_data),
                description=instance_data.get('description', ''),
                is_active=instance_data.get('is_active', True)
            )
            session.add(instance)
            session.flush()
            
            logger.info(f"创建用户目标实例: user={user_id}, instance={instance.instance_name}")
            
            return {
                'id': instance.id,
                'name': instance.instance_name,
                'url': instance.instance_url,
                'auth': {
                    'type': auth_type,
                    **auth_config_data
                },
                'description': instance.description,
                'is_active': instance.is_active
            }
    
    def update_user_target_instance(self, user_id: str, instance_id: str, 
                                    instance_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新用户目标实例
        
        Args:
            user_id: 用户ID
            instance_id: 实例ID
            instance_data: 更新数据
            
        Returns:
            更新后的实例信息或None
        """
        with self.get_session() as session:
            instance = session.query(UserTargetInstance).filter_by(
                id=instance_id,
                user_id=user_id
            ).first()
            
            if not instance:
                return None
            
            # 更新字段
            if 'name' in instance_data:
                instance.instance_name = instance_data['name']
            if 'url' in instance_data:
                instance.instance_url = instance_data['url']
            if 'auth' in instance_data:
                auth_config = instance_data['auth']
                # 获取当前auth_type的值（处理枚举和字符串两种情况）
                current_auth_type = instance.auth_type.value if hasattr(instance.auth_type, 'value') else instance.auth_type
                instance.auth_type = auth_config.get('type', current_auth_type)
                auth_config_data = {k: v for k, v in auth_config.items() if k != 'type'}
                instance.auth_config = json.dumps(auth_config_data)
            if 'description' in instance_data:
                instance.description = instance_data['description']
            if 'is_active' in instance_data:
                instance.is_active = instance_data['is_active']
            
            session.flush()
            
            logger.info(f"更新用户目标实例: user={user_id}, instance={instance_id}")
            
            auth_config = json.loads(instance.auth_config) if instance.auth_config else {}
            # 获取auth_type的值（处理枚举和字符串两种情况）
            auth_type_value = instance.auth_type.value if hasattr(instance.auth_type, 'value') else instance.auth_type
            return {
                'id': instance.id,
                'name': instance.instance_name,
                'url': instance.instance_url,
                'auth': {
                    'type': auth_type_value,
                    **auth_config
                },
                'description': instance.description,
                'is_active': instance.is_active
            }
    
    def delete_user_target_instance(self, user_id: str, instance_id: str) -> bool:
        """删除用户目标实例
        
        Args:
            user_id: 用户ID
            instance_id: 实例ID
            
        Returns:
            是否删除成功
        """
        with self.get_session() as session:
            instance = session.query(UserTargetInstance).filter_by(
                id=instance_id,
                user_id=user_id
            ).first()
            
            if not instance:
                return False
            
            session.delete(instance)
            logger.info(f"删除用户目标实例: user={user_id}, instance={instance_id}")
            return True
    
    # ==================== 完整配置 ====================
    
    def get_full_user_config(self, user_id: str) -> Dict[str, Any]:
        """获取用户的完整配置（与原config结构兼容）
        
        Args:
            user_id: 用户ID
            
        Returns:
            完整配置字典
        """
        # 获取所有系统配置
        sys_configs = self.get_all_user_configs(user_id)
        
        # 获取目标实例
        instances = self.get_user_target_instances(user_id)
        
        # 获取全局API端点（共享）
        with self.get_session() as session:
            endpoints = session.query(ApiEndpoint).filter_by(is_active=True).all()
            endpoints_dict = {ep.endpoint_key: ep.endpoint_path for ep in endpoints}
        
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
                'endpoints': endpoints_dict,
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
            'export': {
                'default_format': sys_configs.get('export_default_format', 'yaml')
            },
            'logging': {
                'level': sys_configs.get('logging_level', 'INFO'),
                'file': sys_configs.get('logging_file', 'logs/app.log'),
                'max_size': sys_configs.get('logging_max_size', '10MB'),
                'backup_count': sys_configs.get('logging_backup_count', 5)
            },
            'cache': {
                'enabled': sys_configs.get('cache_enabled', True),
                'ttl': sys_configs.get('cache_ttl', 300)
            },
            'target_instances': instances
        }
        
        return config
    
    def initialize_default_config_for_user(self, user_id: str):
        """为新用户初始化默认配置
        
        Args:
            user_id: 用户ID
        """
        # 设置默认系统配置
        default_configs = {
            'data_source': ('api', 'string', '数据源类型'),
            'api_base_url': ('', 'string', 'API基础URL'),
            'api_auth_type': ('bearer', 'string', 'API认证类型'),
            'api_timeout': (30, 'number', 'API超时时间'),
            'api_retry_count': (3, 'number', 'API重试次数'),
            'api_retry_delay': (1, 'number', 'API重试延迟'),
            'pagination_default_page_size': (20, 'number', '默认分页大小'),
            'pagination_max_page_size': (100, 'number', '最大分页大小'),
            'pagination_api_page_size': (50, 'number', 'API分页大小'),
            'export_default_format': ('yaml', 'string', '默认导出格式'),
            'logging_level': ('INFO', 'string', '日志级别'),
            'logging_file': ('logs/app.log', 'string', '日志文件路径'),
            'logging_max_size': ('10MB', 'string', '日志文件最大大小'),
            'logging_backup_count': (5, 'number', '日志备份数量'),
            'cache_enabled': (True, 'boolean', '是否启用缓存'),
            'cache_ttl': (300, 'number', '缓存过期时间')
        }
        
        for key, (value, config_type, description) in default_configs.items():
            self.set_user_config(user_id, key, value, config_type, description)
        
        logger.info(f"为用户初始化默认配置: user={user_id}")
    
    def save_full_user_config(self, user_id: str, config_data: Dict[str, Any]):
        """保存用户的完整配置
        
        Args:
            user_id: 用户ID
            config_data: 完整配置字典
        """
        # 保存API配置
        if 'api' in config_data:
            api_config = config_data['api']
            
            # 保存基础URL
            if 'base_url' in api_config:
                self.set_user_config(user_id, 'api_base_url', api_config['base_url'], 'string', 'API基础URL')
            
            # 保存认证配置
            if 'auth' in api_config:
                auth = api_config['auth']
                if 'type' in auth:
                    self.set_user_config(user_id, 'api_auth_type', auth['type'], 'string', 'API认证类型')
                
                # 根据认证类型保存对应的凭证
                if auth.get('type') == 'bearer' and 'token' in auth:
                    self.set_user_config(user_id, 'api_bearer_token', auth['token'], 'string', 'Bearer Token')
                elif auth.get('type') == 'basic':
                    if 'username' in auth:
                        self.set_user_config(user_id, 'api_basic_username', auth['username'], 'string', 'Basic认证用户名')
                    if 'password' in auth:
                        self.set_user_config(user_id, 'api_basic_password', auth['password'], 'string', 'Basic认证密码')
                elif auth.get('type') == 'api_key':
                    if 'api_key' in auth:
                        self.set_user_config(user_id, 'api_key_value', auth['api_key'], 'string', 'API Key')
                    if 'api_key_header' in auth:
                        self.set_user_config(user_id, 'api_key_header', auth['api_key_header'], 'string', 'API Key Header名称')
            
            # 保存超时和重试配置
            if 'timeout' in api_config:
                self.set_user_config(user_id, 'api_timeout', api_config['timeout'], 'number', 'API超时时间')
            if 'retry_count' in api_config:
                self.set_user_config(user_id, 'api_retry_count', api_config['retry_count'], 'number', 'API重试次数')
            if 'retry_delay' in api_config:
                self.set_user_config(user_id, 'api_retry_delay', api_config['retry_delay'], 'number', 'API重试延迟')
        
        # 保存数据源类型
        if 'data_source' in config_data:
            self.set_user_config(user_id, 'data_source', config_data['data_source'], 'string', '数据源类型')
        
        # 保存导出配置
        if 'export' in config_data:
            export_config = config_data['export']
            if 'default_format' in export_config:
                self.set_user_config(user_id, 'export_default_format', export_config['default_format'], 'string', '默认导出格式')
        
        # 保存分页配置
        if 'api' in config_data and 'params' in config_data['api'] and 'pagination' in config_data['api']['params']:
            pagination = config_data['api']['params']['pagination']
            if 'default_page_size' in pagination:
                self.set_user_config(user_id, 'pagination_default_page_size', pagination['default_page_size'], 'number', '默认分页大小')
            if 'max_page_size' in pagination:
                self.set_user_config(user_id, 'pagination_max_page_size', pagination['max_page_size'], 'number', '最大分页大小')
            if 'api_page_size' in pagination:
                self.set_user_config(user_id, 'pagination_api_page_size', pagination['api_page_size'], 'number', 'API分页大小')
        
        # 保存缓存配置
        if 'cache' in config_data:
            cache_config = config_data['cache']
            if 'enabled' in cache_config:
                self.set_user_config(user_id, 'cache_enabled', cache_config['enabled'], 'boolean', '是否启用缓存')
            if 'ttl' in cache_config:
                self.set_user_config(user_id, 'cache_ttl', cache_config['ttl'], 'number', '缓存过期时间')
        
        # 处理目标实例配置
        if 'target_instances' in config_data:
            target_instances = config_data['target_instances']
            
            # 获取现有的目标实例
            existing_instances = self.get_user_target_instances(user_id, include_inactive=True)
            existing_ids = {inst['id'] for inst in existing_instances}
            
            # 更新或创建目标实例
            new_ids = set()
            for instance_data in target_instances:
                instance_id = instance_data.get('id')
                new_ids.add(instance_id)
                
                if instance_id in existing_ids:
                    # 更新现有实例
                    self.update_user_target_instance(user_id, instance_id, instance_data)
                else:
                    # 创建新实例
                    self.create_user_target_instance(user_id, instance_data)
            
            # 删除不再存在的实例
            for instance_id in existing_ids - new_ids:
                self.delete_user_target_instance(user_id, instance_id)
        
        logger.info(f"用户配置已保存: user={user_id}")


# 全局用户配置服务实例
user_config_service = UserConfigService()

