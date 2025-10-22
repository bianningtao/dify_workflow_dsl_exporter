from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from controllers.app_controller import AppExportApi
from controllers.workflow_controller import WorkflowDraftApi, WorkflowListApi, WorkflowBatchExportApi, WorkflowRefreshApi, ApiTestApi
from controllers.workflow_import_controller import (
    WorkflowImportApi, 
    WorkflowImportConfirmApi, 
    WorkflowBatchImportApi, 
    TargetInstancesApi, 
    TargetInstanceTestApi, 
    WorkflowFileValidateApi
)
from controllers.config_controller import (
    ConfigApi,
    ConfigDefaultsApi,
    ConfigResetApi,
    ConfigValidateApi,
    ConfigTestConnectionApi
)
from controllers.auth_controller import (
    LoginApi,
    LogoutApi,
    CurrentUserApi,
    UpdateProfileApi,
    UserManagementApi,
    UserDetailApi,
    ToggleUserStatusApi
)
from services.config_service import config
from services.system_config_loader import (
    check_config_security,
    get_app_name,
    get_app_version,
    get_flask_config,
    get_cors_config,
    get_logging_config
)
import os
import logging

def create_app():
    app = Flask(__name__)
    
    # 初始化配置系统
    try:
        # 创建必要的目录
        config.create_data_directories()
        
        # 配置日志
        logging_config = get_logging_config()
        log_level = getattr(logging, logging_config.get('level', 'INFO'))
        log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 创建日志目录
        log_file = logging_config.get('file', {}).get('path', 'logs/app.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        
        # 输出应用信息
        logger.info("=" * 60)
        logger.info(f"{get_app_name()} v{get_app_version()}")
        logger.info("=" * 60)
        
        # 安全检查
        warnings = check_config_security()
        if warnings:
            logger.warning("配置安全检查发现问题，请查看上方警告信息")
        
        logging.info(f"配置系统初始化成功，数据源: {config.get_data_source()}")
        
    except Exception as e:
        logging.error(f"配置系统初始化失败: {e}")
        raise
    
    # 配置 CORS
    cors_config = get_cors_config()
    if cors_config.get('enabled', True):
        CORS(
            app,
            resources={
                r"/api/*": {
                    "origins": cors_config.get('origins', ['http://localhost:5173', 'http://localhost:3000']),
                    "methods": cors_config.get('methods', ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']),
                    "allow_headers": cors_config.get('allow_headers', ['Content-Type', 'Authorization']),
                    "supports_credentials": True,
                    "expose_headers": ['Content-Type', 'Authorization'],
                    "max_age": 3600  # 预检请求缓存1小时
                }
            }
        )
        logger.info(f"CORS 已启用，允许的源: {', '.join(cors_config.get('origins', []))}")
    
    # 创建API实例
    api = Api(app)
    
    # 注册路由
    api.add_resource(AppExportApi, "/api/apps/<string:app_id>/export")
    api.add_resource(WorkflowDraftApi, "/api/apps/<string:app_id>/workflows/draft")
    api.add_resource(WorkflowListApi, "/api/workflows")
    api.add_resource(WorkflowBatchExportApi, "/api/workflows/batch-export")
    api.add_resource(WorkflowRefreshApi, "/api/workflows/refresh")
    api.add_resource(ApiTestApi, "/api/test-connection")
    
    # 工作流导入相关路由
    api.add_resource(WorkflowImportApi, "/api/workflows/import")
    api.add_resource(WorkflowImportConfirmApi, "/api/workflows/import/<string:import_id>/confirm")
    api.add_resource(WorkflowBatchImportApi, "/api/workflows/batch-import")
    api.add_resource(TargetInstancesApi, "/api/target-instances")
    api.add_resource(TargetInstanceTestApi, "/api/target-instances/<string:instance_id>/test")
    api.add_resource(WorkflowFileValidateApi, "/api/workflows/validate")
    
    # 配置管理相关路由
    api.add_resource(ConfigApi, "/api/config")
    api.add_resource(ConfigDefaultsApi, "/api/config/defaults")
    api.add_resource(ConfigResetApi, "/api/config/reset")
    api.add_resource(ConfigValidateApi, "/api/config/validate")
    api.add_resource(ConfigTestConnectionApi, "/api/config/test-connection")
    
    # 用户认证相关路由
    api.add_resource(LoginApi, "/api/auth/login")
    api.add_resource(LogoutApi, "/api/auth/logout")
    api.add_resource(CurrentUserApi, "/api/auth/me")
    api.add_resource(UpdateProfileApi, "/api/auth/profile")
    
    # 用户管理相关路由（仅管理员）
    api.add_resource(UserManagementApi, "/api/admin/users")
    api.add_resource(UserDetailApi, "/api/admin/users/<string:user_id>")
    api.add_resource(ToggleUserStatusApi, "/api/admin/users/<string:user_id>/toggle-status")
    
    return app

# 创建app实例供gunicorn使用
app = create_app()

if __name__ == "__main__":
    # 从配置文件加载 Flask 服务器配置
    flask_config = get_flask_config()
    
    print("\n" + "=" * 60)
    print(f"🚀 {get_app_name()} v{get_app_version()}")
    print("=" * 60)
    print(f"📍 服务地址: http://{flask_config['host']}:{flask_config['port']}")
    print(f"🔧 调试模式: {'开启' if flask_config['debug'] else '关闭'}")
    print("=" * 60)
    print()
    
    app.run(
        debug=flask_config.get('debug', False),
        host=flask_config.get('host', '0.0.0.0'),
        port=flask_config.get('port', 5001)
    ) 