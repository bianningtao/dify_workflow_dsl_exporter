from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from controllers.app_controller import AppExportApi
from controllers.workflow_controller import WorkflowDraftApi
from services.config_service import config
import os
import logging

def create_app():
    app = Flask(__name__)
    
    # 初始化配置系统
    try:
        # 创建必要的目录
        config.create_data_directories()
        
        # 配置日志
        logging_config = config.get_logging_config()
        log_level = getattr(logging, logging_config.get('level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(logging_config.get('file', 'logs/app.log')),
                logging.StreamHandler()
            ]
        )
        
        logging.info(f"配置系统初始化成功，数据源: {config.get_data_source()}")
        
    except Exception as e:
        logging.error(f"配置系统初始化失败: {e}")
        raise
    
    # 配置CORS
    CORS(app, origins=["http://localhost:3000"])
    
    # 创建API实例
    api = Api(app)
    
    # 注册路由
    api.add_resource(AppExportApi, "/api/apps/<string:app_id>/export")
    api.add_resource(WorkflowDraftApi, "/api/apps/<string:app_id>/workflows/draft")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000) 