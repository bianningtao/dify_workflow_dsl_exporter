#!/usr/bin/env python3
"""
配置数据库初始化脚本
用于首次运行时创建数据库表并从config.yaml导入配置
"""
import sys
import yaml
import logging
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.db_config_loader import get_database_url
from services.database_config_service import DatabaseConfigService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_yaml_config(config_file='../config.yaml') -> dict:
    """从YAML文件加载配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    config_path = Path(__file__).parent / config_file
    
    if not config_path.exists():
        logger.warning(f"配置文件不存在: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        return {}


def init_database_tables(db_service: DatabaseConfigService):
    """初始化数据库表
    
    Args:
        db_service: 数据库服务实例
    """
    logger.info("开始创建数据库表...")
    try:
        db_service.create_tables()
        logger.info("✓ 数据库表创建成功")
    except Exception as e:
        logger.error(f"✗ 创建数据库表失败: {e}")
        raise


def import_system_config(db_service: DatabaseConfigService, yaml_config: dict):
    """导入系统配置
    
    Args:
        db_service: 数据库服务实例
        yaml_config: YAML配置字典
    """
    logger.info("开始导入系统配置...")
    
    try:
        # 数据源类型
        if 'data_source' in yaml_config:
            db_service.set_system_config('data_source', yaml_config['data_source'], 'string', '数据源类型')
        
        # API配置
        if 'api' in yaml_config:
            api = yaml_config['api']
            if 'base_url' in api:
                db_service.set_system_config('api_base_url', api['base_url'], 'string', 'API基础URL')
            if 'auth' in api and 'type' in api['auth']:
                db_service.set_system_config('api_auth_type', api['auth']['type'], 'string', 'API认证类型')
            if 'timeout' in api:
                db_service.set_system_config('api_timeout', api['timeout'], 'number', 'API超时时间')
            if 'retry_count' in api:
                db_service.set_system_config('api_retry_count', api['retry_count'], 'number', 'API重试次数')
            if 'retry_delay' in api:
                db_service.set_system_config('api_retry_delay', api['retry_delay'], 'number', 'API重试延迟')
            
            # 分页配置
            if 'params' in api and 'pagination' in api['params']:
                pagination = api['params']['pagination']
                if 'default_page_size' in pagination:
                    db_service.set_system_config('pagination_default_page_size', pagination['default_page_size'], 'number', '默认分页大小')
                if 'max_page_size' in pagination:
                    db_service.set_system_config('pagination_max_page_size', pagination['max_page_size'], 'number', '最大分页大小')
                if 'api_page_size' in pagination:
                    db_service.set_system_config('pagination_api_page_size', pagination['api_page_size'], 'number', 'API分页大小')
        
        # 导出配置
        if 'export' in yaml_config and 'default_format' in yaml_config['export']:
            db_service.set_system_config('export_default_format', yaml_config['export']['default_format'], 'string', '默认导出格式')
        
        # 日志配置
        if 'logging' in yaml_config:
            logging_config = yaml_config['logging']
            if 'level' in logging_config:
                db_service.set_system_config('logging_level', logging_config['level'], 'string', '日志级别')
            if 'file' in logging_config:
                db_service.set_system_config('logging_file', logging_config['file'], 'string', '日志文件路径')
            if 'max_size' in logging_config:
                db_service.set_system_config('logging_max_size', logging_config['max_size'], 'string', '日志文件最大大小')
            if 'backup_count' in logging_config:
                db_service.set_system_config('logging_backup_count', logging_config['backup_count'], 'number', '日志备份数量')
        
        # 缓存配置
        if 'cache' in yaml_config:
            cache = yaml_config['cache']
            if 'enabled' in cache:
                db_service.set_system_config('cache_enabled', cache['enabled'], 'boolean', '是否启用缓存')
            if 'ttl' in cache:
                db_service.set_system_config('cache_ttl', cache['ttl'], 'number', '缓存过期时间')
        
        logger.info("✓ 系统配置导入成功")
    except Exception as e:
        logger.error(f"✗ 导入系统配置失败: {e}")
        raise


def import_api_endpoints(db_service: DatabaseConfigService, yaml_config: dict):
    """导入API端点配置
    
    Args:
        db_service: 数据库服务实例
        yaml_config: YAML配置字典
    """
    logger.info("开始导入API端点配置...")
    
    try:
        if 'api' in yaml_config and 'endpoints' in yaml_config['api']:
            endpoints = yaml_config['api']['endpoints']
            endpoint_descriptions = {
                'apps_list': '获取应用列表',
                'app_detail': '获取单个应用详情',
                'app_export': '应用导出',
                'app_import': '应用导入',
                'workflow_draft': '获取工作流草稿',
                'workflow_detail': '获取工作流详情',
                'environment_variables': '应用环境变量',
                'import_status': '获取导入状态',
                'import_confirm': '确认导入',
                'check_dependencies': '检查依赖'
            }
            
            for key, path in endpoints.items():
                description = endpoint_descriptions.get(key, '')
                db_service.set_api_endpoint(key, path, description)
                logger.info(f"  ✓ 导入端点: {key} -> {path}")
        
        logger.info("✓ API端点配置导入成功")
    except Exception as e:
        logger.error(f"✗ 导入API端点配置失败: {e}")
        raise


def import_target_instances(db_service: DatabaseConfigService, yaml_config: dict):
    """导入目标实例配置
    
    Args:
        db_service: 数据库服务实例
        yaml_config: YAML配置字典
    """
    logger.info("开始导入目标实例配置...")
    
    try:
        if 'target_instances' in yaml_config:
            instances = yaml_config['target_instances']
            for instance in instances:
                instance_data = {
                    'id': instance.get('id'),
                    'name': instance.get('name'),
                    'url': instance.get('url'),
                    'auth': instance.get('auth', {}),
                    'is_default': instance.get('is_default', False),
                    'is_active': True,
                    'description': instance.get('description', '')
                }
                db_service.create_target_instance(instance_data)
                logger.info(f"  ✓ 导入实例: {instance_data['id']} - {instance_data['name']}")
        
        logger.info("✓ 目标实例配置导入成功")
    except Exception as e:
        logger.error(f"✗ 导入目标实例配置失败: {e}")
        raise


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("配置数据库初始化脚本")
    logger.info("=" * 60)
    
    try:
        # 1. 获取数据库连接URL
        logger.info("\n[1/5] 读取数据库连接配置...")
        db_url = get_database_url()
        logger.info(f"✓ 数据库连接URL: {db_url.split('@')[1] if '@' in db_url else 'N/A'}")  # 隐藏密码
        
        # 2. 初始化数据库服务
        logger.info("\n[2/5] 初始化数据库服务...")
        db_service = DatabaseConfigService(db_url)
        logger.info("✓ 数据库服务初始化成功")
        
        # 3. 创建数据库表
        logger.info("\n[3/5] 创建数据库表...")
        init_database_tables(db_service)
        
        # 4. 加载YAML配置
        logger.info("\n[4/5] 加载YAML配置文件...")
        yaml_config = load_yaml_config()
        if not yaml_config:
            logger.warning("⚠ 未找到YAML配置文件，将使用默认配置")
        else:
            logger.info("✓ YAML配置文件加载成功")
        
        # 5. 导入配置到数据库
        logger.info("\n[5/5] 导入配置到数据库...")
        if yaml_config:
            import_system_config(db_service, yaml_config)
            import_api_endpoints(db_service, yaml_config)
            import_target_instances(db_service, yaml_config)
        else:
            logger.info("⚠ 跳过配置导入，使用数据库默认值")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ 配置数据库初始化完成！")
        logger.info("=" * 60)
        logger.info("\n提示：")
        logger.info("1. 现在可以启动应用程序")
        logger.info("2. 所有配置都将从数据库读取")
        logger.info("3. 可以通过设置界面修改配置")
        logger.info("4. 旧的config.yaml文件可以备份后删除")
        
    except Exception as e:
        logger.error("\n" + "=" * 60)
        logger.error(f"✗ 初始化失败: {e}")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()

