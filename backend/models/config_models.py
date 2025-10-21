"""
配置数据库模型
使用SQLAlchemy ORM定义配置相关的数据库表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False, unique=True, comment='配置键')
    config_value = Column(Text, comment='配置值（JSON格式）')
    config_type = Column(String(50), nullable=False, default='string', comment='配置类型：string, number, boolean, json')
    description = Column(String(500), comment='配置描述')
    is_sensitive = Column(Boolean, default=False, comment='是否为敏感信息')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_config_key', 'config_key'),
        {'comment': '系统配置表'}
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'is_sensitive': self.is_sensitive,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TargetInstance(Base):
    """目标实例配置表"""
    __tablename__ = 'target_instances'
    
    id = Column(String(50), primary_key=True, comment='实例ID')
    name = Column(String(100), nullable=False, comment='实例名称')
    url = Column(String(500), nullable=False, comment='实例URL')
    auth_type = Column(String(20), nullable=False, default='bearer', comment='认证类型：bearer, basic, api_key')
    auth_token = Column(Text, comment='Bearer Token')
    auth_username = Column(String(100), comment='基本认证用户名')
    auth_password = Column(String(255), comment='基本认证密码')
    auth_api_key = Column(Text, comment='API Key')
    auth_api_key_header = Column(String(100), default='X-API-Key', comment='API Key Header名称')
    is_default = Column(Boolean, default=False, comment='是否为默认实例')
    is_active = Column(Boolean, default=True, comment='是否启用')
    description = Column(Text, comment='实例描述')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_is_default', 'is_default'),
        Index('idx_is_active', 'is_active'),
        {'comment': '目标实例配置表'}
    )
    
    def to_dict(self, include_sensitive=False):
        """转换为字典
        
        Args:
            include_sensitive: 是否包含敏感信息（token、密码等）
        """
        data = {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'auth_type': self.auth_type,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['auth'] = {
                'type': self.auth_type
            }
            if self.auth_type == 'bearer':
                data['auth']['token'] = self.auth_token or ''
            elif self.auth_type == 'basic':
                data['auth']['username'] = self.auth_username or ''
                data['auth']['password'] = self.auth_password or ''
            elif self.auth_type == 'api_key':
                data['auth']['api_key'] = self.auth_api_key or ''
                data['auth']['api_key_header'] = self.auth_api_key_header or 'X-API-Key'
        
        return data


class ApiEndpoint(Base):
    """API端点配置表"""
    __tablename__ = 'api_endpoints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint_key = Column(String(100), nullable=False, unique=True, comment='端点键名')
    endpoint_path = Column(String(500), nullable=False, comment='端点路径')
    description = Column(String(500), comment='端点描述')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_endpoint_key', 'endpoint_key'),
        {'comment': 'API端点配置表'}
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'endpoint_key': self.endpoint_key,
            'endpoint_path': self.endpoint_path,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DatabaseConnection(Base):
    """数据库连接配置表"""
    __tablename__ = 'database_connections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_name = Column(String(100), nullable=False, unique=True, comment='连接名称')
    db_type = Column(String(20), nullable=False, default='postgresql', comment='数据库类型')
    host = Column(String(255), nullable=False, comment='主机地址')
    port = Column(Integer, nullable=False, default=5432, comment='端口')
    database_name = Column(String(100), nullable=False, comment='数据库名')
    username = Column(String(100), nullable=False, comment='用户名')
    password = Column(String(255), comment='密码')
    ssl_mode = Column(String(20), default='prefer', comment='SSL模式')
    pool_size = Column(Integer, default=10, comment='连接池大小')
    max_overflow = Column(Integer, default=20, comment='最大溢出连接数')
    pool_timeout = Column(Integer, default=30, comment='连接池超时（秒）')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    table_mappings = relationship('DatabaseTableMapping', back_populates='connection', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_connection_name', 'connection_name'),
        {'comment': '数据库连接配置表'}
    )
    
    def to_dict(self, include_sensitive=False):
        """转换为字典
        
        Args:
            include_sensitive: 是否包含敏感信息（密码）
        """
        data = {
            'id': self.id,
            'connection_name': self.connection_name,
            'db_type': self.db_type,
            'host': self.host,
            'port': self.port,
            'database_name': self.database_name,
            'username': self.username,
            'ssl_mode': self.ssl_mode,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['password'] = self.password or ''
        
        return data


class DatabaseTableMapping(Base):
    """数据库表映射配置"""
    __tablename__ = 'database_table_mappings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_id = Column(Integer, ForeignKey('database_connections.id', ondelete='CASCADE'), nullable=False, comment='数据库连接ID')
    table_key = Column(String(100), nullable=False, comment='表键名')
    table_name = Column(String(100), nullable=False, comment='实际表名')
    description = Column(String(500), comment='表描述')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    connection = relationship('DatabaseConnection', back_populates='table_mappings')
    
    __table_args__ = (
        Index('idx_table_key', 'table_key'),
        {'comment': '数据库表映射配置'}
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'table_key': self.table_key,
            'table_name': self.table_name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

