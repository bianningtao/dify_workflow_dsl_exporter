"""
用户认证服务
处理用户登录、JWT token生成和验证
"""
import jwt
import bcrypt
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from models.user import User, UserSession
from services.db_config_loader import get_database_url
from services.system_config_loader import (
    get_jwt_secret_key,
    get_jwt_algorithm,
    get_jwt_expires_days,
    get_jwt_issuer,
    get_password_hash_rounds
)

logger = logging.getLogger(__name__)


class AuthService:
    """用户认证服务"""
    
    def __init__(self):
        """初始化认证服务"""
        db_url = get_database_url()
        self.engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("认证服务初始化成功")
    
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
    
    def hash_password(self, password: str) -> str:
        """哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            密码哈希
        """
        rounds = get_password_hash_rounds()
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码
        
        Args:
            password: 明文密码
            password_hash: 密码哈希
            
        Returns:
            是否匹配
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """验证用户登录
        
        Args:
            email: 邮箱
            password: 密码
            
        Returns:
            用户信息字典，如果验证失败则返回None
        """
        with self.get_session() as session:
            user = session.query(User).filter_by(email=email).first()
            
            if not user:
                logger.warning(f"用户不存在: {email}")
                return None
            
            if not user.is_active:
                logger.warning(f"用户已被禁用: {email}")
                return None
            
            if not self.verify_password(password, user.password_hash):
                logger.warning(f"密码错误: {email}")
                return None
            
            # 更新最后登录时间
            user.last_login_at = datetime.now()
            session.commit()
            
            return {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            }
    
    def generate_token(self, user_info: Dict[str, Any]) -> str:
        """生成JWT token
        
        Args:
            user_info: 用户信息
            
        Returns:
            JWT token字符串
        """
        jti = str(uuid.uuid4())  # JWT唯一标识符
        expires_days = get_jwt_expires_days()
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        payload = {
            'user_id': user_info['id'],
            'email': user_info['email'],
            'username': user_info['username'],
            'is_admin': user_info['is_admin'],
            'jti': jti,
            'exp': expires_at,
            'iat': datetime.utcnow(),
            'iss': get_jwt_issuer()  # 添加签发者
        }
        
        secret_key = get_jwt_secret_key()
        algorithm = get_jwt_algorithm()
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        
        # 保存会话记录
        with self.get_session() as session:
            user_session = UserSession(
                id=str(uuid.uuid4()),
                user_id=user_info['id'],
                token_jti=jti,
                expires_at=expires_at
            )
            session.add(user_session)
        
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token
        
        Args:
            token: JWT token字符串
            
        Returns:
            解码后的payload，如果验证失败则返回None
        """
        try:
            secret_key = get_jwt_secret_key()
            algorithm = get_jwt_algorithm()
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            
            # 检查token是否在会话表中（未被撤销）
            with self.get_session() as session:
                user_session = session.query(UserSession).filter_by(token_jti=payload['jti']).first()
                if not user_session:
                    logger.warning("Token已被撤销")
                    return None
                
                # 检查是否过期
                if user_session.expires_at < datetime.now():
                    logger.warning("Token已过期")
                    return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的Token: {e}")
            return None
    
    def revoke_token(self, jti: str) -> bool:
        """撤销token
        
        Args:
            jti: JWT JTI
            
        Returns:
            是否成功
        """
        try:
            with self.get_session() as session:
                user_session = session.query(UserSession).filter_by(token_jti=jti).first()
                if user_session:
                    session.delete(user_session)
                    logger.info(f"Token已撤销: {jti}")
                    return True
                return False
        except Exception as e:
            logger.error(f"撤销Token失败: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """清理过期的会话记录"""
        try:
            with self.get_session() as session:
                expired_count = session.query(UserSession).filter(
                    UserSession.expires_at < datetime.now()
                ).delete()
                logger.info(f"清理了{expired_count}个过期会话")
        except Exception as e:
            logger.error(f"清理过期会话失败: {e}")


# 全局认证服务实例
auth_service = AuthService()

