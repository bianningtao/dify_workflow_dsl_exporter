import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2.pool import ThreadedConnectionPool
except ImportError:
    psycopg2 = None
    ThreadedConnectionPool = None

from .config_service import config
from models.app import App, Workflow, EnvironmentVariable, AppMode

class DatabaseConnector:
    """数据库连接器，用于从Dify数据库获取数据"""
    
    def __init__(self):
        self.config = config
        self.pool = None
        self._init_connection_pool()
    
    def _init_connection_pool(self):
        """初始化数据库连接池"""
        if not self.config.is_database_enabled():
            return
        
        if psycopg2 is None:
            raise ImportError("psycopg2 未安装。请运行: pip install psycopg2-binary")
        
        db_config = self.config.get_database_config()
        
        try:
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=db_config.get('pool_size', 10),
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['username'],
                password=db_config['password'],
                sslmode=db_config.get('ssl_mode', 'prefer'),
                cursor_factory=RealDictCursor
            )
            logging.info("数据库连接池初始化成功")
        except Exception as e:
            logging.error(f"数据库连接池初始化失败: {e}")
            raise
    
    def get_connection(self):
        """获取数据库连接"""
        if not self.pool:
            raise RuntimeError("数据库连接池未初始化")
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """归还数据库连接"""
        if self.pool:
            self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行数据库查询"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logging.error(f"数据库查询失败: {e}")
            raise
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_app_by_id(self, app_id: str) -> Optional[App]:
        """根据应用ID获取应用信息"""
        if not self.config.is_database_enabled():
            return None
        
        db_config = self.config.get_database_config()
        table_name = db_config.get('tables', {}).get('apps', 'apps')
        
        query = f"""
            SELECT id, name, mode, icon, icon_type, icon_background, 
                   description, use_icon_as_answer_icon, tenant_id, 
                   created_at, updated_at
            FROM {table_name}
            WHERE id = %s
        """
        
        try:
            results = self.execute_query(query, (app_id,))
            if not results:
                logging.warning(f"未找到应用ID为 {app_id} 的应用")
                return None
            
            app_data = results[0]
            return App(
                id=app_data['id'],
                name=app_data['name'],
                mode=app_data['mode'],
                icon=app_data.get('icon', '🤖'),
                icon_type=app_data.get('icon_type', 'emoji'),
                icon_background=app_data.get('icon_background', '#FFEAD5'),
                description=app_data.get('description', ''),
                use_icon_as_answer_icon=app_data.get('use_icon_as_answer_icon', False),
                tenant_id=app_data['tenant_id']
            )
        except Exception as e:
            logging.error(f"获取应用信息失败: {e}")
            return None
    
    def get_workflow_by_app_id(self, app_id: str) -> Optional[Workflow]:
        """根据应用ID获取工作流"""
        if not self.config.is_database_enabled():
            return None
            
        try:
            # 查询工作流基本信息（包括环境变量）
            workflow_query = """
                SELECT wf.id, wf.app_id, wf.version, wf.graph, wf.features, wf.environment_variables
                FROM workflows wf 
                WHERE wf.app_id = %s 
                ORDER BY wf.created_at DESC 
                LIMIT 1
            """
            
            results = self.execute_query(workflow_query, (app_id,))
            if not results:
                return None
            
            workflow_data = results[0]
            
            # 解析JSON字段
            graph = self._parse_json_field(workflow_data['graph'])
            features = self._parse_json_field(workflow_data['features']) 
            environment_variables_data = self._parse_json_field(workflow_data['environment_variables']) or []
            
            # 解析环境变量
            env_vars = []
            for env_var_data in environment_variables_data:
                if isinstance(env_var_data, dict):
                    env_vars.append(EnvironmentVariable(
                        name=env_var_data.get('name', ''),
                        value=env_var_data.get('value', ''),
                        value_type=env_var_data.get('value_type', 'string')
                    ))
            
            # 构造工作流对象
            workflow = Workflow(
                id=workflow_data['id'],
                app_id=workflow_data['app_id'],
                version=workflow_data['version'],
                graph=graph,
                features=features,
                environment_variables=env_vars
            )
            
            return workflow
            
        except Exception as e:
            logging.error(f"获取工作流失败: {e}")
            return None
    
    def get_all_workflows(self) -> List[Workflow]:
        """获取所有工作流"""
        if not self.config.is_database_enabled():
            return []
            
        try:
            # 查询所有工作流（包括环境变量）
            workflow_query = """
                SELECT wf.id, wf.app_id, wf.version, wf.graph, wf.features, wf.environment_variables
                FROM workflows wf 
                ORDER BY wf.created_at DESC
                LIMIT 50
            """
            
            results = self.execute_query(workflow_query)
            workflows = []
            
            for workflow_data in results:
                try:
                    # 解析JSON字段
                    graph = self._parse_json_field(workflow_data['graph'])
                    features = self._parse_json_field(workflow_data['features'])
                    environment_variables_data = self._parse_json_field(workflow_data['environment_variables']) or []
                    
                    # 解析环境变量
                    env_vars = []
                    for env_var_data in environment_variables_data:
                        if isinstance(env_var_data, dict):
                            env_vars.append(EnvironmentVariable(
                                name=env_var_data.get('name', ''),
                                value=env_var_data.get('value', ''),
                                value_type=env_var_data.get('value_type', 'string')
                            ))
                    
                    # 构造工作流对象
                    workflow = Workflow(
                        id=workflow_data['id'],
                        app_id=workflow_data['app_id'],
                        version=workflow_data['version'],
                        graph=graph,
                        features=features,
                        environment_variables=env_vars
                    )
                    
                    workflows.append(workflow)
                    
                except Exception as e:
                    logging.error(f"解析工作流数据失败 (ID: {workflow_data.get('id', 'unknown')}): {e}")
                    continue
            
            return workflows
            
        except Exception as e:
            logging.error(f"获取所有工作流失败: {e}")
            return []
    
    def get_environment_variables_by_app_id(self, app_id: str) -> List[EnvironmentVariable]:
        """根据应用ID获取环境变量"""
        if not self.config.is_database_enabled():
            return []
        
        query = """
            SELECT environment_variables
            FROM workflows
            WHERE app_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        try:
            results = self.execute_query(query, (app_id,))
            if not results:
                return []
            
            environment_variables_data = self._parse_json_field(results[0]['environment_variables']) or []
            environment_variables = []
            
            for env_var_data in environment_variables_data:
                if isinstance(env_var_data, dict):
                    environment_variables.append(
                        EnvironmentVariable(
                            name=env_var_data.get('name', ''),
                            value=env_var_data.get('value', ''),
                            value_type=env_var_data.get('value_type', 'string')
                        )
                    )
            
            return environment_variables
            
        except Exception as e:
            logging.error(f"获取环境变量失败: {e}")
            return []
    
    def get_workflow_nodes_by_workflow_id(self, workflow_id: str) -> List[Dict[str, Any]]:
        """根据工作流ID获取节点信息"""
        if not self.config.is_database_enabled():
            return []
        
        db_config = self.config.get_database_config()
        nodes_table = db_config.get('tables', {}).get('workflow_nodes', 'workflow_nodes')
        
        query = f"""
            SELECT id, workflow_id, node_id, node_type, title, 
                   data, position_x, position_y
            FROM {nodes_table}
            WHERE workflow_id = %s
            ORDER BY node_id
        """
        
        try:
            results = self.execute_query(query, (workflow_id,))
            nodes = []
            
            for row in results:
                node_data = row.get('data', {})
                if isinstance(node_data, str):
                    node_data = json.loads(node_data)
                
                nodes.append({
                    'id': row['node_id'],
                    'type': row['node_type'],
                    'data': {
                        'type': row['node_type'],
                        'title': row.get('title', row['node_id']),
                        **node_data
                    },
                    'position': {
                        'x': row.get('position_x', 0),
                        'y': row.get('position_y', 0)
                    }
                })
            
            return nodes
        except Exception as e:
            logging.error(f"获取工作流节点失败: {e}")
            return []
    
    def get_workflow_edges_by_workflow_id(self, workflow_id: str) -> List[Dict[str, Any]]:
        """根据工作流ID获取边信息"""
        if not self.config.is_database_enabled():
            return []
        
        db_config = self.config.get_database_config()
        edges_table = db_config.get('tables', {}).get('workflow_edges', 'workflow_edges')
        
        query = f"""
            SELECT id, workflow_id, edge_id, source_node_id, target_node_id,
                   source_handle, target_handle, data
            FROM {edges_table}
            WHERE workflow_id = %s
            ORDER BY edge_id
        """
        
        try:
            results = self.execute_query(query, (workflow_id,))
            edges = []
            
            for row in results:
                edge_data = row.get('data', {})
                if isinstance(edge_data, str):
                    edge_data = json.loads(edge_data)
                
                edges.append({
                    'id': row['edge_id'],
                    'source': row['source_node_id'],
                    'target': row['target_node_id'],
                    'source_handle': row.get('source_handle', 'source'),
                    'target_handle': row.get('target_handle', 'target'),
                    **edge_data
                })
            
            return edges
        except Exception as e:
            logging.error(f"获取工作流边失败: {e}")
            return []
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        if not self.config.is_database_enabled():
            return False
        
        try:
            results = self.execute_query("SELECT 1 as test")
            return len(results) > 0 and results[0]['test'] == 1
        except Exception as e:
            logging.error(f"数据库连接测试失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.closeall()
            logging.info("数据库连接池已关闭")

    def _parse_json_field(self, json_field) -> dict:
        """解析JSON字段"""
        if json_field is None:
            return {}
        if isinstance(json_field, dict):
            return json_field
        if isinstance(json_field, str):
            try:
                return json.loads(json_field)
            except json.JSONDecodeError as e:
                logging.warning(f"JSON解析失败: {e}")
                return {}
        return {}

    def get_workflows_paginated(self, page: int = 1, page_size: int = 20, search: str = "") -> dict:
        """
        分页获取工作流列表
        :param page: 页码（从1开始）
        :param page_size: 每页数量
        :param search: 搜索关键词
        :return: 包含工作流列表和总数的字典
        """
        if not self.config.is_database_enabled():
            return {"workflows": [], "total": 0}
            
        try:
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 构建搜索条件
            search_condition = ""
            search_params = []
            if search:
                search_condition = "WHERE (a.name ILIKE %s OR wf.app_id::text ILIKE %s)"
                search_params = [f"%{search}%", f"%{search}%"]
            
            # 获取总数的查询 - 按app_id去重
            count_query = f"""
                SELECT COUNT(DISTINCT wf.app_id)
                FROM workflows wf
                LEFT JOIN apps a ON wf.app_id = a.id
                {search_condition}
            """
            
            # 获取分页数据的查询 - 每个app_id只取最新的工作流
            data_query = f"""
                SELECT DISTINCT ON (wf.app_id)
                    wf.id, wf.app_id, wf.version, wf.graph, wf.features, 
                    wf.environment_variables, wf.created_at,
                    a.name as app_name, a.description as app_description, a.mode as app_mode
                FROM workflows wf
                LEFT JOIN apps a ON wf.app_id = a.id
                {search_condition}
                ORDER BY wf.app_id, wf.created_at DESC
                LIMIT %s OFFSET %s
            """
            
            # 执行总数查询
            count_results = self.execute_query(count_query, search_params)
            total = count_results[0]['count'] if count_results else 0
            
            # 执行分页查询
            data_params = search_params + [page_size, offset]
            data_results = self.execute_query(data_query, data_params)
            
            workflows = []
            for workflow_data in data_results:
                try:
                    # 解析JSON字段
                    graph = self._parse_json_field(workflow_data['graph'])
                    features = self._parse_json_field(workflow_data['features'])
                    environment_variables_data = self._parse_json_field(workflow_data['environment_variables']) or []
                    
                    # 解析环境变量
                    env_vars = []
                    for env_var_data in environment_variables_data:
                        if isinstance(env_var_data, dict):
                            env_vars.append(EnvironmentVariable(
                                name=env_var_data.get('name', ''),
                                value=env_var_data.get('value', ''),
                                value_type=env_var_data.get('value_type', 'string')
                            ))
                    
                    # 构造工作流对象
                    workflow = Workflow(
                        id=workflow_data['id'],
                        app_id=workflow_data['app_id'],
                        version=workflow_data['version'],
                        graph=graph,
                        features=features,
                        environment_variables=env_vars,
                        app_name=workflow_data.get('app_name') or f"工作流 {workflow_data['app_id'][:8]}",
                        app_description=workflow_data.get('app_description') or '',
                        app_mode=workflow_data.get('app_mode') or 'workflow'
                    )
                    
                    workflows.append(workflow)
                    
                except Exception as e:
                    logging.error(f"解析工作流数据失败 (ID: {workflow_data.get('id', 'unknown')}): {e}")
                    continue
            
            return {
                "workflows": workflows,
                "total": total
            }
            
        except Exception as e:
            logging.error(f"分页获取工作流失败: {e}")
            return {"workflows": [], "total": 0}


# 全局数据库连接器实例
database_connector = DatabaseConnector() 