"""
数据库配置加载器
负责从config_db.yaml或环境变量读取数据库连接配置
"""
import os
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseConfigLoader:
    """数据库配置加载器"""
    
    def __init__(self, config_file='config_db.yaml'):
        """初始化配置加载器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self._config = None
    
    def _load_from_file(self) -> dict:
        """从配置文件加载配置"""
        config_path = Path(__file__).parent.parent / self.config_file
        
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('config_database', {})
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            return {}
    
    def _load_from_env(self) -> dict:
        """从环境变量加载配置"""
        return {
            'type': os.getenv('CONFIG_DB_TYPE', 'mysql'),
            'host': os.getenv('CONFIG_DB_HOST'),
            'port': int(os.getenv('CONFIG_DB_PORT', 3306)),
            'database': os.getenv('CONFIG_DB_DATABASE'),
            'username': os.getenv('CONFIG_DB_USERNAME'),
            'password': os.getenv('CONFIG_DB_PASSWORD'),
            'charset': os.getenv('CONFIG_DB_CHARSET', 'utf8mb4'),
            'pool_size': int(os.getenv('CONFIG_DB_POOL_SIZE', 10)),
            'max_overflow': int(os.getenv('CONFIG_DB_MAX_OVERFLOW', 20)),
            'pool_timeout': int(os.getenv('CONFIG_DB_POOL_TIMEOUT', 30))
        }
    
    def get_config(self) -> dict:
        """获取数据库配置
        
        优先级：环境变量 > 配置文件
        
        Returns:
            数据库配置字典
        """
        if self._config is not None:
            return self._config
        
        # 从文件加载
        file_config = self._load_from_file()
        
        # 从环境变量加载
        env_config = self._load_from_env()
        
        # 合并配置（环境变量优先）
        config = {}
        for key in ['type', 'host', 'port', 'database', 'username', 'password', 
                   'charset', 'pool_size', 'max_overflow', 'pool_timeout']:
            # 环境变量存在且不为None，使用环境变量
            if env_config.get(key) is not None:
                config[key] = env_config[key]
            # 否则使用文件配置
            elif key in file_config:
                config[key] = file_config[key]
        
        self._config = config
        return config
    
    def get_database_url(self) -> str:
        """获取数据库连接URL
        
        Returns:
            数据库连接URL字符串
        """
        config = self.get_config()
        
        # 验证必需配置
        required_keys = ['host', 'database', 'username']
        missing_keys = [key for key in required_keys if not config.get(key)]
        if missing_keys:
            raise ValueError(f"缺少必需的数据库配置: {', '.join(missing_keys)}")
        
        db_type = config.get('type', 'mysql')
        host = config['host']
        port = config.get('port', 3306)
        database = config['database']
        username = config['username']
        password = config.get('password', '')
        charset = config.get('charset', 'utf8mb4')
        
        # 构建连接URL
        if db_type == 'mysql':
            # 使用pymysql驱动
            url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset={charset}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
        
        return url
    
    def validate_config(self) -> tuple[bool, str]:
        """验证配置是否完整
        
        Returns:
            (是否有效, 错误信息)
        """
        try:
            config = self.get_config()
            
            # 检查必需字段
            required_keys = ['host', 'database', 'username']
            missing_keys = [key for key in required_keys if not config.get(key)]
            
            if missing_keys:
                return False, f"缺少必需的配置: {', '.join(missing_keys)}"
            
            # 尝试构建URL
            self.get_database_url()
            
            return True, "配置验证成功"
        except Exception as e:
            return False, f"配置验证失败: {str(e)}"


# 全局配置加载器实例
_db_config_loader = None


def get_db_config_loader() -> DatabaseConfigLoader:
    """获取全局数据库配置加载器实例"""
    global _db_config_loader
    if _db_config_loader is None:
        _db_config_loader = DatabaseConfigLoader()
    return _db_config_loader


def get_database_url() -> str:
    """获取数据库连接URL（便捷函数）"""
    return get_db_config_loader().get_database_url()

