"""
用户模型
定义用户相关的数据库表模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    """用户表模型"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, comment='用户ID（UUID）')
    email = Column(String(255), unique=True, nullable=False, index=True, comment='邮箱（登录账号）')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    username = Column(String(100), nullable=False, comment='用户名')
    is_admin = Column(Boolean, default=False, comment='是否为管理员')
    is_active = Column(Boolean, default=True, index=True, comment='是否启用')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    last_login_at = Column(DateTime, nullable=True, comment='最后登录时间')


class ConfigType(enum.Enum):
    """配置类型枚举"""
    string = 'string'
    number = 'number'
    boolean = 'boolean'
    json = 'json'


class UserSystemConfig(Base):
    """用户系统配置表模型"""
    __tablename__ = 'user_system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, comment='用户ID')
    config_key = Column(String(100), nullable=False, index=True, comment='配置键')
    config_value = Column(Text, comment='配置值')
    config_type = Column(SQLEnum(ConfigType), default=ConfigType.string, comment='配置类型')
    description = Column(Text, comment='配置描述')
    is_sensitive = Column(Boolean, default=False, comment='是否为敏感信息')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')


class AuthType(enum.Enum):
    """认证类型枚举"""
    bearer = 'bearer'
    basic = 'basic'
    api_key = 'api_key'


class UserTargetInstance(Base):
    """用户目标实例配置表模型"""
    __tablename__ = 'user_target_instances'
    
    id = Column(String(36), primary_key=True, comment='实例ID（UUID）')
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, comment='用户ID')
    instance_name = Column(String(100), nullable=False, comment='实例名称')
    instance_url = Column(String(500), nullable=False, comment='实例URL')
    auth_type = Column(SQLEnum(AuthType), default=AuthType.bearer, comment='认证类型')
    auth_config = Column(Text, comment='认证配置（JSON格式）')  # 存储为JSON字符串
    description = Column(Text, comment='实例描述')
    is_active = Column(Boolean, default=True, index=True, comment='是否启用')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')


class DBType(enum.Enum):
    """数据库类型枚举"""
    postgresql = 'postgresql'
    mysql = 'mysql'


class UserDatabaseConnection(Base):
    """用户数据库连接配置表模型"""
    __tablename__ = 'user_database_connections'
    
    id = Column(String(36), primary_key=True, comment='连接ID（UUID）')
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, comment='用户ID')
    connection_name = Column(String(100), nullable=False, comment='连接名称')
    db_type = Column(SQLEnum(DBType), default=DBType.postgresql, comment='数据库类型')
    host = Column(String(255), nullable=False, comment='主机地址')
    port = Column(Integer, nullable=False, comment='端口')
    database_name = Column(String(100), nullable=False, comment='数据库名')
    username = Column(String(100), nullable=False, comment='用户名')
    password_encrypted = Column(Text, comment='加密后的密码')
    ssl_mode = Column(String(50), default='prefer', comment='SSL模式')
    pool_size = Column(Integer, default=10, comment='连接池大小')
    max_overflow = Column(Integer, default=20, comment='最大溢出连接数')
    pool_timeout = Column(Integer, default=30, comment='连接池超时时间')
    is_active = Column(Boolean, default=True, index=True, comment='是否启用')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')


class UserSession(Base):
    """用户会话表模型"""
    __tablename__ = 'user_sessions'
    
    id = Column(String(36), primary_key=True, comment='会话ID（UUID）')
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, comment='用户ID')
    token_jti = Column(String(255), unique=True, nullable=False, index=True, comment='JWT JTI（唯一标识符）')
    expires_at = Column(DateTime, nullable=False, index=True, comment='过期时间')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')

