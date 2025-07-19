import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigService:
    """配置服务类，负责读取和管理配置文件"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        # 首先尝试当前目录
        config_path = Path("config.yaml")
        
        # 如果当前目录没有，尝试上级目录（项目根目录）
        if not config_path.exists():
            config_path = Path("../config.yaml")
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件未找到，请确保 config.yaml 存在于项目根目录或当前目录")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 应用环境变量覆盖
            config = self._apply_env_overrides(config)
            
            # 验证配置
            self._validate_config(config)
            
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {e}")
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        if 'env_mapping' not in config:
            return config
        
        for config_key, env_key in config['env_mapping'].items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # 解析嵌套的配置键 (如 'database.host')
                keys = config_key.split('.')
                current = config
                
                # 导航到倒数第二层
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # 设置最终值
                final_key = keys[-1]
                # 尝试转换数据类型
                try:
                    if env_value.lower() in ['true', 'false']:
                        current[final_key] = env_value.lower() == 'true'
                    elif env_value.isdigit():
                        current[final_key] = int(env_value)
                    elif '.' in env_value and env_value.replace('.', '').isdigit():
                        current[final_key] = float(env_value)
                    else:
                        current[final_key] = env_value
                except:
                    current[final_key] = env_value
        
        return config
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置文件"""
        required_fields = ['data_source']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"缺少必需的配置字段: {field}")
        
        data_source = config['data_source']
        
        if data_source not in ['database', 'api']:
            raise ValueError(f"不支持的数据源类型: {data_source}")
        
        # 验证对应的数据源配置
        if data_source == 'database':
            self._validate_database_config(config.get('database', {}))
        elif data_source == 'api':
            self._validate_api_config(config.get('api', {}))
    
    def _validate_database_config(self, db_config: Dict[str, Any]) -> None:
        """验证数据库配置"""
        required_fields = ['type', 'host', 'port', 'database', 'username', 'password']
        
        for field in required_fields:
            if field not in db_config:
                raise ValueError(f"缺少数据库配置字段: {field}")
        
        if db_config['type'] not in ['postgresql']:
            raise ValueError(f"不支持的数据库类型: {db_config['type']}")
    
    def _validate_api_config(self, api_config: Dict[str, Any]) -> None:
        """验证API配置"""
        required_fields = ['base_url', 'auth']
        
        for field in required_fields:
            if field not in api_config:
                raise ValueError(f"缺少API配置字段: {field}")
        
        auth_config = api_config['auth']
        if 'type' not in auth_config:
            raise ValueError("缺少API认证类型配置")
        
        auth_type = auth_config['type']
        if auth_type == 'bearer' and 'token' not in auth_config:
            raise ValueError("Bearer认证缺少token配置")
        elif auth_type == 'basic' and ('username' not in auth_config or 'password' not in auth_config):
            raise ValueError("Basic认证缺少用户名或密码配置")
        elif auth_type == 'api_key' and 'api_key' not in auth_config:
            raise ValueError("API Key认证缺少api_key配置")
    
        
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config.copy()
    
    def get_data_source(self) -> str:
        """获取数据源类型"""
        return self._config['data_source']
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self._config.get('database', {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self._config.get('api', {})
    

    
    def get_export_config(self) -> Dict[str, Any]:
        """获取导出配置"""
        return self._config.get('export', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self._config.get('logging', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self._config.get('security', {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        return self._config.get('cache', {})
    
    def is_database_enabled(self) -> bool:
        """检查是否启用数据库连接"""
        return self._config['data_source'] == 'database'
    
    def is_api_enabled(self) -> bool:
        """检查是否启用API连接"""
        return self._config['data_source'] == 'api'
    

    
    def is_cache_enabled(self) -> bool:
        """检查是否启用缓存"""
        return self._config.get('cache', {}).get('enabled', False)
    
    def reload_config(self) -> None:
        """重新加载配置文件"""
        self._config = self._load_config()
        logging.info("配置文件已重新加载")
    
    def get_connection_string(self) -> Optional[str]:
        """获取数据库连接字符串"""
        if not self.is_database_enabled():
            return None
        
        db_config = self.get_database_config()
        
        if db_config['type'] == 'postgresql':
            return (
                f"postgresql://{db_config['username']}:{db_config['password']}"
                f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
        
        return None
    
    def get_api_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        if not self.is_api_enabled():
            return {}
        
        api_config = self.get_api_config()
        auth_config = api_config.get('auth', {})
        headers = {}
        
        if auth_config.get('type') == 'bearer':
            headers['Authorization'] = f"Bearer {auth_config.get('token', '')}"
        elif auth_config.get('type') == 'basic':
            # 添加基本认证支持
            import base64
            username = auth_config.get('username', '')
            password = auth_config.get('password', '')
            credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            headers['Authorization'] = f"Basic {credentials}"
        elif auth_config.get('type') == 'api_key':
            header_name = auth_config.get('api_key_header', 'X-API-Key')
            headers[header_name] = auth_config.get('api_key', '')
        
        return headers
    
    def create_data_directories(self) -> None:
        """创建必要的数据目录"""
        # 创建日志目录
        logging_config = self.get_logging_config()
        log_file = logging_config.get('file', 'logs/app.log')
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建缓存目录
        cache_config = self.get_cache_config()
        if cache_config.get('type') == 'file':
            cache_dir = Path(cache_config.get('file', {}).get('cache_dir', './cache'))
            cache_dir.mkdir(parents=True, exist_ok=True)


# 全局配置实例
config = ConfigService() 