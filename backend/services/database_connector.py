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
        """根据应用ID获取工作流信息"""
        if not self.config.is_database_enabled():
            return None
        
        db_config = self.config.get_database_config()
        workflow_table = db_config.get('tables', {}).get('workflows', 'workflows')
        
        query = f"""
            SELECT id, app_id, version, graph, features, 
                   created_at, updated_at
            FROM {workflow_table}
            WHERE app_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """
        
        try:
            results = self.execute_query(query, (app_id,))
            if not results:
                logging.warning(f"未找到应用ID为 {app_id} 的工作流")
                return None
            
            workflow_data = results[0]
            
            # 解析JSON字段
            graph = workflow_data.get('graph', {})
            if isinstance(graph, str):
                graph = json.loads(graph)
            
            features = workflow_data.get('features', {})
            if isinstance(features, str):
                features = json.loads(features)
            
            # 获取环境变量
            environment_variables = self.get_environment_variables_by_app_id(app_id)
            
            return Workflow(
                id=workflow_data['id'],
                app_id=workflow_data['app_id'],
                version=workflow_data.get('version', '1.0'),
                graph=graph,
                features=features,
                environment_variables=environment_variables
            )
        except Exception as e:
            logging.error(f"获取工作流信息失败: {e}")
            return None
    
    def get_environment_variables_by_app_id(self, app_id: str) -> List[EnvironmentVariable]:
        """根据应用ID获取环境变量"""
        if not self.config.is_database_enabled():
            return []
        
        db_config = self.config.get_database_config()
        env_table = db_config.get('tables', {}).get('app_environment_variables', 'app_environment_variables')
        
        query = f"""
            SELECT name, value, value_type, is_secret
            FROM {env_table}
            WHERE app_id = %s
            ORDER BY name
        """
        
        try:
            results = self.execute_query(query, (app_id,))
            environment_variables = []
            
            for row in results:
                # 确定变量类型
                value_type = row.get('value_type', 'string')
                if row.get('is_secret', False):
                    value_type = 'secret'
                
                environment_variables.append(
                    EnvironmentVariable(
                        name=row['name'],
                        value=row['value'],
                        value_type=value_type
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


# 全局数据库连接器实例
database_connector = DatabaseConnector() 