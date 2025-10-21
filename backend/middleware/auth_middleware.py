"""
认证中间件
提供token验证和权限检查装饰器
"""
from functools import wraps
from flask import request
from services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)


def token_required(f):
    """需要token的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            logger.warning("请求缺少认证token")
            return {'success': False, 'message': '缺少认证token'}, 401
        
        # 移除 "Bearer " 前缀
        if token.startswith('Bearer '):
            token = token[7:]
        
        # 验证token
        payload = auth_service.verify_token(token)
        if not payload:
            logger.warning("无效或过期的token")
            return {'success': False, 'message': '无效或过期的token'}, 401
        
        # 将用户信息添加到请求上下文
        request.current_user = payload
        logger.debug(f"用户认证成功: {payload.get('email')}")
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """需要管理员权限的装饰器"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not request.current_user.get('is_admin'):
            logger.warning(f"用户 {request.current_user.get('email')} 尝试访问管理员功能")
            return {'success': False, 'message': '需要管理员权限'}, 403
        
        return f(*args, **kwargs)
    
    return decorated


def get_current_user_id():
    """获取当前用户ID（需要在token_required装饰的函数中使用）"""
    if hasattr(request, 'current_user'):
        return request.current_user.get('user_id')
    return None


def get_current_user_email():
    """获取当前用户邮箱（需要在token_required装饰的函数中使用）"""
    if hasattr(request, 'current_user'):
        return request.current_user.get('email')
    return None


def is_current_user_admin():
    """检查当前用户是否为管理员（需要在token_required装饰的函数中使用）"""
    if hasattr(request, 'current_user'):
        return request.current_user.get('is_admin', False)
    return False

