"""
认证控制器
处理用户登录、登出、获取当前用户信息等
"""
from flask import request
from flask_restful import Resource
import logging

from services.auth_service import auth_service
from services.user_service import user_service
from middleware.auth_middleware import token_required, admin_required

logger = logging.getLogger(__name__)


class LoginApi(Resource):
    """用户登录"""
    
    def post(self):
        """处理登录请求"""
        try:
            data = request.get_json()
            
            if not data:
                return {'success': False, 'message': '请求数据不能为空'}, 400
            
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not email or not password:
                return {'success': False, 'message': '邮箱和密码不能为空'}, 400
            
            # 验证用户
            user_info = auth_service.authenticate_user(email, password)
            if not user_info:
                logger.warning(f"登录失败: {email}")
                return {'success': False, 'message': '邮箱或密码错误'}, 401
            
            # 生成token
            token = auth_service.generate_token(user_info)
            
            logger.info(f"用户登录成功: {email}")
            
            return {
                'success': True,
                'message': '登录成功',
                'token': token,
                'user': {
                    'id': user_info['id'],
                    'email': user_info['email'],
                    'username': user_info['username'],
                    'is_admin': user_info['is_admin']
                }
            }, 200
            
        except Exception as e:
            logger.error(f"登录处理失败: {e}", exc_info=True)
            return {'success': False, 'message': '登录失败，请稍后重试'}, 500


class LogoutApi(Resource):
    """用户登出"""
    
    @token_required
    def post(self):
        """处理登出请求"""
        try:
            jti = request.current_user.get('jti')
            email = request.current_user.get('email')
            
            # 撤销token
            auth_service.revoke_token(jti)
            
            logger.info(f"用户登出: {email}")
            
            return {'success': True, 'message': '登出成功'}, 200
            
        except Exception as e:
            logger.error(f"登出处理失败: {e}", exc_info=True)
            return {'success': False, 'message': '登出失败'}, 500


class CurrentUserApi(Resource):
    """获取当前用户信息"""
    
    @token_required
    def get(self):
        """获取当前登录用户的详细信息"""
        try:
            user_id = request.current_user.get('user_id')
            
            # 从数据库获取最新的用户信息
            user = user_service.get_user_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            return {
                'success': True,
                'user': user
            }, 200
            
        except Exception as e:
            logger.error(f"获取当前用户信息失败: {e}", exc_info=True)
            return {'success': False, 'message': '获取用户信息失败'}, 500


class UpdateProfileApi(Resource):
    """更新当前用户资料"""
    
    @token_required
    def put(self):
        """更新当前用户的用户名和密码"""
        try:
            user_id = request.current_user.get('user_id')
            data = request.get_json()
            
            if not data:
                return {'success': False, 'message': '请求数据不能为空'}, 400
            
            # 只允许更新用户名和密码
            update_data = {}
            if 'username' in data:
                update_data['username'] = data['username']
            if 'password' in data:
                update_data['password'] = data['password']
            
            if not update_data:
                return {'success': False, 'message': '没有要更新的数据'}, 400
            
            # 更新用户信息
            user = user_service.update_user(user_id, **update_data)
            
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            logger.info(f"用户更新资料: {request.current_user.get('email')}")
            
            return {
                'success': True,
                'message': '资料更新成功',
                'user': user
            }, 200
            
        except Exception as e:
            logger.error(f"更新用户资料失败: {e}", exc_info=True)
            return {'success': False, 'message': '更新资料失败'}, 500


class UserManagementApi(Resource):
    """用户管理（仅管理员）"""
    
    @admin_required
    def get(self):
        """获取所有用户列表"""
        try:
            include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
            users = user_service.get_all_users(include_inactive=include_inactive)
            
            return {
                'success': True,
                'users': users,
                'total': len(users)
            }, 200
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}", exc_info=True)
            return {'success': False, 'message': '获取用户列表失败'}, 500
    
    @admin_required
    def post(self):
        """创建新用户"""
        try:
            data = request.get_json()
            
            if not data:
                return {'success': False, 'message': '请求数据不能为空'}, 400
            
            # 验证必需字段
            required_fields = ['email', 'password', 'username']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'message': f'缺少必需字段: {field}'}, 400
            
            # 创建用户
            user = user_service.create_user(
                email=data['email'],
                password=data['password'],
                username=data['username'],
                is_admin=data.get('is_admin', False)
            )
            
            logger.info(f"管理员创建用户: {data['email']}")
            
            return {
                'success': True,
                'message': '用户创建成功',
                'user': user
            }, 201
            
        except ValueError as e:
            return {'success': False, 'message': str(e)}, 400
        except Exception as e:
            logger.error(f"创建用户失败: {e}", exc_info=True)
            return {'success': False, 'message': '创建用户失败'}, 500


class UserDetailApi(Resource):
    """单个用户管理（仅管理员）"""
    
    @admin_required
    def get(self, user_id):
        """获取指定用户信息"""
        try:
            user = user_service.get_user_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            return {
                'success': True,
                'user': user
            }, 200
            
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}", exc_info=True)
            return {'success': False, 'message': '获取用户信息失败'}, 500
    
    @admin_required
    def put(self, user_id):
        """更新指定用户"""
        try:
            data = request.get_json()
            
            if not data:
                return {'success': False, 'message': '请求数据不能为空'}, 400
            
            # 更新用户
            user = user_service.update_user(user_id, **data)
            
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            logger.info(f"管理员更新用户: {user_id}")
            
            return {
                'success': True,
                'message': '用户更新成功',
                'user': user
            }, 200
            
        except Exception as e:
            logger.error(f"更新用户失败: {e}", exc_info=True)
            return {'success': False, 'message': '更新用户失败'}, 500
    
    @admin_required
    def delete(self, user_id):
        """删除指定用户"""
        try:
            # 不允许删除自己
            current_user_id = request.current_user.get('user_id')
            if user_id == current_user_id:
                return {'success': False, 'message': '不能删除自己的账号'}, 400
            
            # 删除用户
            success = user_service.delete_user(user_id)
            
            if not success:
                return {'success': False, 'message': '用户不存在'}, 404
            
            logger.info(f"管理员删除用户: {user_id}")
            
            return {
                'success': True,
                'message': '用户已删除'
            }, 200
            
        except Exception as e:
            logger.error(f"删除用户失败: {e}", exc_info=True)
            return {'success': False, 'message': '删除用户失败'}, 500


class ToggleUserStatusApi(Resource):
    """切换用户状态（启用/禁用）"""
    
    @admin_required
    def post(self, user_id):
        """切换指定用户的启用/禁用状态"""
        try:
            # 不允许禁用自己
            current_user_id = request.current_user.get('user_id')
            if user_id == current_user_id:
                return {'success': False, 'message': '不能禁用自己的账号'}, 400
            
            # 切换状态
            user = user_service.toggle_user_status(user_id)
            
            if not user:
                return {'success': False, 'message': '用户不存在'}, 404
            
            status_text = '启用' if user['is_active'] else '禁用'
            logger.info(f"管理员{status_text}用户: {user_id}")
            
            return {
                'success': True,
                'message': f'用户已{status_text}',
                'user': user
            }, 200
            
        except Exception as e:
            logger.error(f"切换用户状态失败: {e}", exc_info=True)
            return {'success': False, 'message': '操作失败'}, 500

