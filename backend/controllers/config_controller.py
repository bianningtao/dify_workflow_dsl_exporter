from flask_restful import Resource
from flask import request, jsonify
from services.config_service import config
from services.user_config_service import user_config_service
from middleware.auth_middleware import token_required
import logging
import yaml
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigDefaultsApi(Resource):
    """获取配置默认值的API"""
    
    def get(self):
        """获取所有配置的默认值（仅包含API端点）"""
        try:
            defaults = {
                "data_source": "api",
                "api": {
                    "base_url": "",
                    "auth": {
                        "type": "bearer",
                        "token": ""
                    },
                    "endpoints": {
                        "apps_list": "/console/api/apps",
                        "app_detail": "/console/api/apps/{app_id}",
                        "app_export": "/console/api/apps/{app_id}/export",
                        "app_import": "/console/api/apps/imports",
                        "workflow_draft": "/console/api/apps/{app_id}/workflows/draft",
                        "workflow_detail": "/console/api/workflows/{workflow_id}",
                        "environment_variables": "/console/api/apps/{app_id}/variables",
                        "import_status": "/console/api/apps/imports/{import_id}",
                        "import_confirm": "/console/api/apps/imports/{import_id}/confirm",
                        "check_dependencies": "/console/api/apps/imports/{import_id}/check-dependencies"
                    },
                    "params": {
                        "apps_list": {
                            "name": "",
                            "is_created_by_me": False,
                            "page": 1,
                            "limit": 50
                        },
                        "pagination": {
                            "default_page_size": 20,
                            "max_page_size": 100,
                            "api_page_size": 50
                        }
                    },
                    "timeout": 30,
                    "retry_count": 3,
                    "retry_delay": 1
                },
                "database": {
                    "type": "postgresql",
                    "host": "",
                    "port": 5432,
                    "database": "",
                    "username": "",
                    "password": "",
                    "pool_size": 10,
                    "max_overflow": 20,
                    "pool_timeout": 30,
                    "ssl_mode": "prefer",
                    "tables": {
                        "apps": "apps",
                        "workflows": "workflows",
                        "app_environment_variables": "app_environment_variables",
                        "workflow_nodes": "workflow_nodes",
                        "workflow_edges": "workflow_edges"
                    }
                },
                "export": {
                    "default_format": "yaml"
                },
                "logging": {
                    "level": "INFO",
                    "file": "logs/app.log",
                    "max_size": "10MB",
                    "backup_count": 5,
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "cache": {
                    "enabled": True,
                    "ttl": 300
                },
                "target_instances": [
                    {
                        "id": "default",
                        "name": "默认实例",
                        "url": "",
                        "auth": {
                            "type": "bearer",
                            "token": ""
                        },
                        "is_default": True
                    }
                ]
            }
            
            return {
                "success": True,
                "data": defaults
            }, 200
            
        except Exception as e:
            logger.error(f"获取配置默认值失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"获取配置默认值失败: {str(e)}"
            }, 500


class ConfigApi(Resource):
    """配置管理API"""
    
    @token_required
    def get(self):
        """获取当前用户的配置"""
        try:
            user_id = request.current_user.get('user_id')
            
            # 获取用户配置
            user_config_data = user_config_service.get_full_user_config(user_id)
            
            if user_config_data:
                # 用户有自己的配置，返回用户配置
                safe_config = self._filter_sensitive_data(user_config_data)
            else:
                # 用户还没有配置，返回空配置模板
                safe_config = {
                    "data_source": "api",
                    "api": {
                        "base_url": "",
                        "auth": {
                            "type": "bearer",
                            "token": ""
                        }
                    }
                }
            
            return {
                "success": True,
                "data": safe_config
            }, 200
            
        except Exception as e:
            logger.error(f"获取配置失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"获取配置失败: {str(e)}"
            }, 500
    
    @token_required
    def put(self):
        """更新当前用户的配置"""
        try:
            user_id = request.current_user.get('user_id')
            data = request.get_json()
            
            if not data:
                return {
                    "success": False,
                    "message": "请求数据不能为空"
                }, 400
            
            # 验证配置数据
            validation_result = self._validate_config(data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "message": validation_result["message"]
                }, 400
            
            # 保存配置到用户配置表
            user_config_service.save_full_user_config(user_id, data)
            
            logger.info(f"用户 {user_id} 的配置已更新")
            
            return {
                "success": True,
                "message": "配置更新成功"
            }, 200
            
        except Exception as e:
            logger.error(f"更新配置失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"更新配置失败: {str(e)}"
            }, 500
    
    def _filter_sensitive_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤敏感数据，但保留用于显示的部分信息"""
        import copy
        safe_config = copy.deepcopy(config_data)
        
        # 数据库密码 - 保持原样（包括空字符串）
        # 不需要特殊处理，直接返回原值
        
        # API认证信息 - 保持原样
        # 前端会根据值是否为空来决定是否显示
        
        # 目标实例的认证信息 - 保持原样
        # 保留所有值，包括空字符串
        
        return safe_config
    
    def _validate_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置数据"""
        # 检查必需字段
        if "data_source" not in config_data:
            return {
                "valid": False,
                "message": "缺少data_source字段"
            }
        
        data_source = config_data["data_source"]
        if data_source not in ["database", "api"]:
            return {
                "valid": False,
                "message": f"不支持的数据源类型: {data_source}"
            }
        
        # 验证数据源配置
        if data_source == "database":
            if "database" not in config_data:
                return {
                    "valid": False,
                    "message": "使用database数据源时必须提供database配置"
                }
            
            db_config = config_data["database"]
            required_fields = ["type", "host", "port", "database", "username"]
            for field in required_fields:
                if field not in db_config:
                    return {
                        "valid": False,
                        "message": f"数据库配置缺少必需字段: {field}"
                    }
        
        elif data_source == "api":
            if "api" not in config_data:
                return {
                    "valid": False,
                    "message": "使用api数据源时必须提供api配置"
                }
            
            api_config = config_data["api"]
            if "base_url" not in api_config:
                return {
                    "valid": False,
                    "message": "API配置缺少base_url字段"
                }
            
            if "auth" not in api_config:
                return {
                    "valid": False,
                    "message": "API配置缺少auth字段"
                }
            
            auth = api_config["auth"]
            if "type" not in auth:
                return {
                    "valid": False,
                    "message": "API认证配置缺少type字段"
                }
            
            auth_type = auth["type"]
            if auth_type == "bearer" and not auth.get("token"):
                return {
                    "valid": False,
                    "message": "Bearer认证需要提供token"
                }
            elif auth_type == "basic" and (not auth.get("username") or not auth.get("password")):
                return {
                    "valid": False,
                    "message": "Basic认证需要提供username和password"
                }
            elif auth_type == "api_key" and not auth.get("api_key"):
                return {
                    "valid": False,
                    "message": "API Key认证需要提供api_key"
                }
        
        return {
            "valid": True,
            "message": "配置验证通过"
        }
    
    def _update_target_instances(self, instances_data: list) -> None:
        """更新目标实例配置
        
        Args:
            instances_data: 目标实例列表
        """
        # 获取现有实例ID
        existing_instances = config.get_target_instances()
        existing_ids = {inst['id'] for inst in existing_instances}
        
        # 获取新的实例ID
        new_ids = {inst['id'] for inst in instances_data}
        
        # 删除不再存在的实例
        for instance_id in existing_ids - new_ids:
            config.delete_target_instance(instance_id)
            logger.info(f"删除目标实例: {instance_id}")
        
        # 更新或创建实例
        for instance in instances_data:
            instance_id = instance.get('id')
            if instance_id in existing_ids:
                # 更新现有实例
                config.update_target_instance(instance_id, instance)
                logger.info(f"更新目标实例: {instance_id}")
            else:
                # 创建新实例
                config.create_target_instance(instance)
                logger.info(f"创建目标实例: {instance_id}")


class ConfigResetApi(Resource):
    """重置配置为默认值的API"""
    
    def post(self):
        """重置配置为默认值（清空所有非端点配置）"""
        try:
            # 注意：数据库模式下，重置配置意味着清空所有配置值
            # API端点配置保留，其他配置重置为空或默认值
            
            # 重置系统配置为默认值
            config.set_system_config('data_source', 'api', 'string', '数据源类型')
            config.set_system_config('api_base_url', '', 'string', 'API基础URL')
            config.set_system_config('api_auth_type', 'bearer', 'string', 'API认证类型')
            config.set_system_config('api_timeout', 30, 'number', 'API超时时间')
            config.set_system_config('api_retry_count', 3, 'number', 'API重试次数')
            config.set_system_config('api_retry_delay', 1, 'number', 'API重试延迟')
            config.set_system_config('pagination_default_page_size', 20, 'number', '默认分页大小')
            config.set_system_config('pagination_max_page_size', 100, 'number', '最大分页大小')
            config.set_system_config('pagination_api_page_size', 50, 'number', 'API分页大小')
            config.set_system_config('export_default_format', 'yaml', 'string', '默认导出格式')
            config.set_system_config('logging_level', 'INFO', 'string', '日志级别')
            config.set_system_config('logging_file', 'logs/app.log', 'string', '日志文件路径')
            config.set_system_config('logging_max_size', '10MB', 'string', '日志文件最大大小')
            config.set_system_config('logging_backup_count', 5, 'number', '日志备份数量')
            config.set_system_config('cache_enabled', True, 'boolean', '是否启用缓存')
            config.set_system_config('cache_ttl', 300, 'number', '缓存过期时间')
            
            # 删除所有目标实例（保留一个默认的空实例）
            existing_instances = config.get_target_instances()
            for instance in existing_instances:
                config.delete_target_instance(instance['id'])
            
            # 创建一个默认空实例
            config.create_target_instance({
                'id': 'default',
                'name': '默认实例',
                'url': '',
                'auth': {'type': 'bearer', 'token': ''},
                'is_default': True,
                'is_active': True,
                'description': '默认Dify实例，需要配置URL和认证信息'
            })
            
            logger.info("配置已重置为默认值")
            
            return {
                "success": True,
                "message": "配置已重置为默认值"
            }, 200
            
        except Exception as e:
            logger.error(f"重置配置失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"重置配置失败: {str(e)}"
            }, 500


class ConfigValidateApi(Resource):
    """验证配置的API"""
    
    def post(self):
        """验证配置数据"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    "success": False,
                    "message": "请求数据不能为空"
                }, 400
            
            # 执行验证
            config_api = ConfigApi()
            validation_result = config_api._validate_config(data)
            
            if validation_result["valid"]:
                return {
                    "success": True,
                    "message": "配置验证通过",
                    "valid": True
                }, 200
            else:
                return {
                    "success": False,
                    "message": validation_result["message"],
                    "valid": False
                }, 400
            
        except Exception as e:
            logger.error(f"验证配置失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"验证配置失败: {str(e)}",
                "valid": False
            }, 500


class ConfigTestConnectionApi(Resource):
    """测试连接的API"""
    
    def post(self):
        """测试API或数据库连接"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    "success": False,
                    "message": "请求数据不能为空"
                }, 400
            
            data_source = data.get('data_source')
            
            if data_source == 'api':
                return self._test_api_connection(data.get('api', {}))
            elif data_source == 'database':
                return self._test_database_connection(data.get('database', {}))
            elif data_source == 'target_instance':
                # 测试目标实例连接
                return self._test_target_instance_connection(data.get('target_instance', {}))
            else:
                return {
                    "success": False,
                    "message": f"不支持的数据源类型: {data_source}"
                }, 400
            
        except Exception as e:
            logger.error(f"测试连接失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"测试连接失败: {str(e)}"
            }, 500
    
    def _test_api_connection(self, api_config: Dict[str, Any]) -> tuple:
        """测试API连接"""
        import requests
        
        try:
            base_url = api_config.get('base_url', '').rstrip('/')
            auth_config = api_config.get('auth', {})
            
            if not base_url:
                return {
                    "success": False,
                    "message": "API基础URL不能为空"
                }, 400
            
            # 构建请求头
            headers = {'Content-Type': 'application/json'}
            
            auth_type = auth_config.get('type')
            if auth_type == 'bearer':
                token = auth_config.get('token', '')
                if not token:
                    return {
                        "success": False,
                        "message": "Bearer Token不能为空"
                    }, 400
                headers['Authorization'] = f"Bearer {token}"
                
            elif auth_type == 'basic':
                username = auth_config.get('username', '')
                password = auth_config.get('password', '')
                if not username or not password:
                    return {
                        "success": False,
                        "message": "用户名和密码不能为空"
                    }, 400
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
                headers['Authorization'] = f"Basic {credentials}"
                
            elif auth_type == 'api_key':
                api_key = auth_config.get('api_key', '')
                api_key_header = auth_config.get('api_key_header', 'X-API-Key')
                if not api_key:
                    return {
                        "success": False,
                        "message": "API Key不能为空"
                    }, 400
                headers[api_key_header] = api_key
            
            # 测试连接 - 尝试访问apps列表端点
            test_url = f"{base_url}/console/api/apps?page=1&limit=1"
            
            logger.info(f"测试API连接: {test_url}")
            
            response = requests.get(
                test_url,
                headers=headers,
                timeout=10,
                verify=True
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "API连接测试成功！",
                    "details": {
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                }, 200
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "认证失败，请检查认证信息是否正确"
                }, 400
            elif response.status_code == 403:
                return {
                    "success": False,
                    "message": "权限不足，请检查API权限配置"
                }, 400
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": "API端点不存在，请检查base_url是否正确"
                }, 400
            else:
                return {
                    "success": False,
                    "message": f"连接失败，HTTP状态码: {response.status_code}"
                }, 400
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "连接超时，请检查网络或URL是否正确"
            }, 400
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "无法连接到服务器，请检查URL是否正确"
            }, 400
        except requests.exceptions.SSLError:
            return {
                "success": False,
                "message": "SSL证书验证失败"
            }, 400
        except Exception as e:
            logger.error(f"API连接测试异常: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"测试失败: {str(e)}"
            }, 500
    
    def _test_target_instance_connection(self, instance_config: Dict[str, Any]) -> tuple:
        """测试目标实例连接"""
        import requests
        
        try:
            url = instance_config.get('url', '').rstrip('/')
            auth_config = instance_config.get('auth', {})
            
            if not url:
                return {
                    "success": False,
                    "message": "目标实例URL不能为空"
                }, 400
            
            # 构建请求头
            headers = {'Content-Type': 'application/json'}
            
            auth_type = auth_config.get('type')
            if auth_type == 'bearer':
                token = auth_config.get('token', '')
                if not token:
                    return {
                        "success": False,
                        "message": "目标实例Token不能为空"
                    }, 400
                headers['Authorization'] = f"Bearer {token}"
                
            elif auth_type == 'basic':
                username = auth_config.get('username', '')
                password = auth_config.get('password', '')
                if not username or not password:
                    return {
                        "success": False,
                        "message": "目标实例用户名和密码不能为空"
                    }, 400
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
                headers['Authorization'] = f"Basic {credentials}"
                
            elif auth_type == 'api_key':
                api_key = auth_config.get('api_key', '')
                api_key_header = auth_config.get('api_key_header', 'X-API-Key')
                if not api_key:
                    return {
                        "success": False,
                        "message": "目标实例API Key不能为空"
                    }, 400
                headers[api_key_header] = api_key
            
            # 测试连接 - 尝试访问apps列表端点
            test_url = f"{url}/console/api/apps?page=1&limit=1"
            
            logger.info(f"测试目标实例连接: {test_url}")
            
            response = requests.get(
                test_url,
                headers=headers,
                timeout=10,
                verify=True
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "目标实例连接测试成功！",
                    "details": {
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                }, 200
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "认证失败，请检查Token或用户名密码是否正确"
                }, 400
            elif response.status_code == 403:
                return {
                    "success": False,
                    "message": "权限不足，请检查账号权限"
                }, 400
            else:
                return {
                    "success": False,
                    "message": f"连接失败，状态码: {response.status_code}"
                }, 400
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "连接超时，请检查网络或URL是否正确"
            }, 400
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "无法连接到目标实例，请检查URL是否正确"
            }, 400
        except requests.exceptions.SSLError:
            return {
                "success": False,
                "message": "SSL证书验证失败"
            }, 400
        except Exception as e:
            logger.error(f"目标实例连接测试异常: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"测试失败: {str(e)}"
            }, 500
    
    def _test_database_connection(self, db_config: Dict[str, Any]) -> tuple:
        """测试数据库连接"""
        try:
            db_type = db_config.get('type', 'postgresql')
            host = db_config.get('host', '')
            port = db_config.get('port', 5432)
            database = db_config.get('database', '')
            username = db_config.get('username', '')
            password = db_config.get('password', '')
            
            if not all([host, database, username]):
                return {
                    "success": False,
                    "message": "数据库连接信息不完整"
                }, 400
            
            if db_type == 'postgresql':
                import psycopg
                
                # 构建连接字符串
                conn_string = f"host={host} port={port} dbname={database} user={username} password={password}"
                
                logger.info(f"测试数据库连接: {host}:{port}/{database}")
                
                # 尝试连接
                conn = psycopg.connect(conn_string, connect_timeout=10)
                
                # 执行简单查询测试
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                conn.close()
                
                return {
                    "success": True,
                    "message": "数据库连接测试成功！",
                    "details": {
                        "database_type": db_type,
                        "host": host,
                        "port": port,
                        "database": database
                    }
                }, 200
            else:
                return {
                    "success": False,
                    "message": f"不支持的数据库类型: {db_type}"
                }, 400
                
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"数据库连接失败: {str(e)}"
            }, 400

