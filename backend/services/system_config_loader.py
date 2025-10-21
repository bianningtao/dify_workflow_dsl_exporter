"""
系统配置加载器
从 config_db.yaml 加载系统配置（JWT、用户系统、应用等）
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / 'config_db.yaml'


class SystemConfig:
    """系统配置单例类"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"系统配置加载成功: {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"加载系统配置失败: {e}")
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的路径
        
        例如: get('jwt.secret_key') 或 get('user_system.password_hash_rounds')
        
        Args:
            key: 配置键，支持点号分隔的嵌套路径
            default: 默认值
            
        Returns:
            配置值
        """
        if not self._config:
            return default
        
        # 支持点号分隔的嵌套配置
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self):
        """重新加载配置"""
        self._config = None
        self._load_config()


# 全局配置实例
system_config = SystemConfig()


# ===== JWT 配置 =====

def get_jwt_secret_key() -> str:
    """获取 JWT 密钥（优先从环境变量）"""
    return os.getenv('JWT_SECRET_KEY') or system_config.get('jwt.secret_key', 'default-secret-key-change-me')


def get_jwt_expires_days() -> int:
    """获取 JWT 过期天数"""
    env_value = os.getenv('JWT_EXPIRES_DAYS')
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass
    return system_config.get('jwt.expires_days', 7)


def get_jwt_issuer() -> str:
    """获取 JWT 签发者"""
    return os.getenv('JWT_ISSUER') or system_config.get('jwt.issuer', 'dify-workflow-exporter')


def get_jwt_algorithm() -> str:
    """获取 JWT 加密算法"""
    return system_config.get('jwt.algorithm', 'HS256')


# ===== 用户系统配置 =====

def get_password_hash_rounds() -> int:
    """获取密码加密轮数"""
    return system_config.get('user_system.password_hash_rounds', 12)


def get_default_admin_config() -> Dict[str, str]:
    """获取默认管理员配置"""
    return system_config.get('user_system.default_admin', {
        'email': 'admin@example.com',
        'username': '系统管理员',
        'password': 'admin123456'
    })


def get_password_policy() -> Dict[str, Any]:
    """获取密码策略配置"""
    return system_config.get('user_system.password_policy', {
        'min_length': 6,
        'require_uppercase': False,
        'require_lowercase': False,
        'require_numbers': False,
        'require_special_chars': False
    })


# ===== 应用配置 =====

def get_app_name() -> str:
    """获取应用名称"""
    return system_config.get('application.name', 'Dify Workflow DSL 管理器')


def get_app_version() -> str:
    """获取应用版本"""
    return system_config.get('application.version', '2.0.0')


def get_flask_config() -> Dict[str, Any]:
    """获取 Flask 配置"""
    default_config = {
        'debug': False,
        'host': '0.0.0.0',
        'port': 5001
    }
    
    config = system_config.get('application.flask', default_config)
    
    # 环境变量覆盖
    if os.getenv('FLASK_DEBUG'):
        config['debug'] = os.getenv('FLASK_DEBUG').lower() == 'true'
    if os.getenv('FLASK_HOST'):
        config['host'] = os.getenv('FLASK_HOST')
    if os.getenv('FLASK_PORT'):
        try:
            config['port'] = int(os.getenv('FLASK_PORT'))
        except ValueError:
            pass
    
    return config


def get_cors_config() -> Dict[str, Any]:
    """获取 CORS 配置"""
    return system_config.get('application.cors', {
        'enabled': True,
        'origins': ['http://localhost:5173', 'http://localhost:3000'],
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization']
    })


# ===== 日志配置 =====

def get_logging_config() -> Dict[str, Any]:
    """获取日志配置"""
    return system_config.get('logging', {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': {
            'enabled': True,
            'path': 'logs/app.log',
            'max_bytes': 10485760,
            'backup_count': 5
        }
    })


# ===== 安全配置 =====

def get_security_config() -> Dict[str, Any]:
    """获取安全配置"""
    return system_config.get('security', {
        'max_login_attempts': 5,
        'lockout_duration': 15,
        'session_timeout': 30
    })


# ===== 辅助函数 =====

def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    验证密码是否符合策略
    
    Args:
        password: 待验证的密码
        
    Returns:
        (是否有效, 错误消息)
    """
    policy = get_password_policy()
    
    # 检查最小长度
    min_length = policy.get('min_length', 6)
    if len(password) < min_length:
        return False, f'密码长度至少 {min_length} 个字符'
    
    # 检查是否需要大写字母
    if policy.get('require_uppercase', False):
        if not any(c.isupper() for c in password):
            return False, '密码必须包含至少一个大写字母'
    
    # 检查是否需要小写字母
    if policy.get('require_lowercase', False):
        if not any(c.islower() for c in password):
            return False, '密码必须包含至少一个小写字母'
    
    # 检查是否需要数字
    if policy.get('require_numbers', False):
        if not any(c.isdigit() for c in password):
            return False, '密码必须包含至少一个数字'
    
    # 检查是否需要特殊字符
    if policy.get('require_special_chars', False):
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, '密码必须包含至少一个特殊字符'
    
    return True, None


def generate_secret_key() -> str:
    """生成随机密钥（用于首次设置）"""
    import secrets
    return secrets.token_hex(32)


# ===== 配置检查 =====

def check_config_security():
    """检查配置安全性，输出警告"""
    warnings = []
    
    # 检查 JWT 密钥
    secret_key = get_jwt_secret_key()
    if secret_key in ['default-secret-key-change-me', 'your-secret-key-change-in-production-please-use-random-string']:
        warnings.append('⚠️  JWT 密钥使用默认值，生产环境请务必修改！')
        warnings.append(f'   建议使用: python -c "import secrets; print(secrets.token_hex(32))"')
    
    # 检查默认管理员密码
    admin_config = get_default_admin_config()
    if admin_config.get('password') == 'admin123456':
        warnings.append('⚠️  默认管理员密码未修改，请首次登录后立即修改！')
    
    # 检查 Flask debug 模式
    flask_config = get_flask_config()
    if flask_config.get('debug', False):
        warnings.append('⚠️  Flask debug 模式已启用，生产环境请关闭！')
    
    if warnings:
        logger.warning('配置安全检查发现问题:')
        for warning in warnings:
            logger.warning(warning)
    
    return warnings


if __name__ == '__main__':
    """测试配置加载"""
    import json
    
    print("=" * 60)
    print("系统配置测试")
    print("=" * 60)
    
    print("\n📦 JWT 配置:")
    print(f"  密钥: {get_jwt_secret_key()[:20]}... (已截断)")
    print(f"  过期天数: {get_jwt_expires_days()} 天")
    print(f"  签发者: {get_jwt_issuer()}")
    print(f"  算法: {get_jwt_algorithm()}")
    
    print("\n👤 用户系统配置:")
    print(f"  密码加密轮数: {get_password_hash_rounds()}")
    print(f"  默认管理员:")
    admin = get_default_admin_config()
    print(f"    邮箱: {admin['email']}")
    print(f"    用户名: {admin['username']}")
    print(f"    密码: {'*' * len(admin['password'])}")
    
    print("\n🔒 密码策略:")
    policy = get_password_policy()
    print(json.dumps(policy, indent=2, ensure_ascii=False))
    
    print("\n🚀 应用配置:")
    print(f"  名称: {get_app_name()}")
    print(f"  版本: {get_app_version()}")
    print(f"  Flask: {get_flask_config()}")
    
    print("\n🌐 CORS 配置:")
    cors = get_cors_config()
    print(f"  启用: {cors['enabled']}")
    print(f"  允许源: {', '.join(cors['origins'])}")
    
    print("\n📝 日志配置:")
    logging_cfg = get_logging_config()
    print(f"  级别: {logging_cfg['level']}")
    print(f"  文件: {logging_cfg['file']['path']}")
    
    print("\n🔐 安全配置:")
    security = get_security_config()
    print(json.dumps(security, indent=2, ensure_ascii=False))
    
    print("\n⚠️  安全检查:")
    warnings = check_config_security()
    if not warnings:
        print("  ✅ 未发现安全问题")
    
    print("\n🧪 密码策略测试:")
    test_passwords = [
        "123",           # 太短
        "123456",        # 符合默认策略
        "Admin123!",     # 强密码
    ]
    for pwd in test_passwords:
        valid, error = validate_password(pwd)
        status = "✅" if valid else "❌"
        print(f"  {status} '{pwd}': {error or '有效'}")
    
    print("\n" + "=" * 60)

