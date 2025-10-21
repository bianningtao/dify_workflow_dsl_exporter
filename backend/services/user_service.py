"""
用户管理服务
处理用户的CRUD操作
"""
import uuid
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from datetime import datetime

from models.user import User
from services.db_config_loader import get_database_url
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


class UserService:
    """用户管理服务"""
    
    def __init__(self):
        """初始化用户服务"""
        db_url = get_database_url()
        self.engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.auth_service = AuthService()
        logger.info("用户服务初始化成功")
    
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
    
    def create_user(self, email: str, password: str, username: str, is_admin: bool = False) -> Dict[str, Any]:
        """创建用户
        
        Args:
            email: 邮箱
            password: 密码
            username: 用户名
            is_admin: 是否为管理员
            
        Returns:
            创建的用户信息
        """
        with self.get_session() as session:
            # 检查邮箱是否已存在
            existing_user = session.query(User).filter_by(email=email).first()
            if existing_user:
                raise ValueError(f"邮箱已存在: {email}")
            
            # 创建用户
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash=self.auth_service.hash_password(password),
                username=username,
                is_admin=is_admin,
                is_active=True
            )
            session.add(user)
            session.flush()
            
            logger.info(f"创建用户: {email}")
            
            return {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典或None
        """
        with self.get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            
            return {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
            }
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户信息
        
        Args:
            email: 邮箱
            
        Returns:
            用户信息字典或None
        """
        with self.get_session() as session:
            user = session.query(User).filter_by(email=email).first()
            if not user:
                return None
            
            return {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
            }
    
    def get_all_users(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """获取所有用户列表
        
        Args:
            include_inactive: 是否包含已禁用的用户
            
        Returns:
            用户列表
        """
        with self.get_session() as session:
            query = session.query(User)
            if not include_inactive:
                query = query.filter_by(is_active=True)
            
            users = query.order_by(User.created_at.desc()).all()
            
            return [{
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
            } for user in users]
    
    def update_user(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段（username, is_admin, is_active, password）
            
        Returns:
            更新后的用户信息或None
        """
        with self.get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            
            # 更新允许的字段
            if 'username' in kwargs:
                user.username = kwargs['username']
            if 'is_admin' in kwargs:
                user.is_admin = kwargs['is_admin']
            if 'is_active' in kwargs:
                user.is_active = kwargs['is_active']
            if 'password' in kwargs:
                user.password_hash = self.auth_service.hash_password(kwargs['password'])
            
            session.flush()
            
            logger.info(f"更新用户: {user.email}")
            
            return {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        with self.get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False
            
            session.delete(user)
            logger.info(f"删除用户: {user.email}")
            return True
    
    def toggle_user_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """切换用户启用/禁用状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            更新后的用户信息或None
        """
        with self.get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None
            
            user.is_active = not user.is_active
            session.flush()
            
            logger.info(f"切换用户状态: {user.email}, 新状态: {'启用' if user.is_active else '禁用'}")
            
            return {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            }


# 全局用户服务实例
user_service = UserService()

