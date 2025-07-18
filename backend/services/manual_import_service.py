import json
import yaml
import logging
import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from .config_service import config
from models.app import App, Workflow, EnvironmentVariable, AppMode

class ManualImportService:
    """手动导入服务，用于管理手动上传的工作流数据"""
    
    def __init__(self):
        self.config = config
        self.data_dir = None
        self.backup_dir = None
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储配置"""
        if not self.config.is_manual_enabled():
            return
        
        manual_config = self.config.get_manual_config()
        
        if manual_config.get('storage_type') == 'file':
            file_config = manual_config.get('file_storage', {})
            self.data_dir = Path(file_config.get('data_dir', './data'))
            self.backup_dir = Path(file_config.get('backup_dir', './data/backups'))
            
            # 创建目录
            self.data_dir.mkdir(parents=True, exist_ok=True)
            if file_config.get('auto_backup', True):
                self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            logging.info(f"手动导入服务初始化成功，数据目录: {self.data_dir}")
    
    def import_workflow_data(self, app_id: str, workflow_data: Dict[str, Any], format_type: str = 'json') -> bool:
        """导入工作流数据"""
        if not self.config.is_manual_enabled():
            raise RuntimeError("手动导入功能未启用")
        
        try:
            # 验证数据格式
            self._validate_workflow_data(workflow_data)
            
            # 保存数据
            self._save_workflow_data(app_id, workflow_data, format_type)
            
            logging.info(f"工作流数据导入成功: {app_id}")
            return True
            
        except Exception as e:
            logging.error(f"工作流数据导入失败: {e}")
            return False
    
    def import_from_file(self, app_id: str, file_path: str) -> bool:
        """从文件导入工作流数据"""
        if not self.config.is_manual_enabled():
            raise RuntimeError("手动导入功能未启用")
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            # 根据文件扩展名确定格式
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    workflow_data = yaml.safe_load(f)
                format_type = 'yaml'
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                format_type = 'json'
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")
            
            return self.import_workflow_data(app_id, workflow_data, format_type)
            
        except Exception as e:
            logging.error(f"从文件导入失败: {e}")
            return False
    
    def _validate_workflow_data(self, workflow_data: Dict[str, Any]) -> None:
        """验证工作流数据格式"""
        required_fields = ['app', 'workflow']
        
        for field in required_fields:
            if field not in workflow_data:
                raise ValueError(f"缺少必需字段: {field}")
        
        app_data = workflow_data['app']
        workflow_config = workflow_data['workflow']
        
        # 验证应用数据
        if 'name' not in app_data:
            raise ValueError("应用数据缺少name字段")
        if 'mode' not in app_data:
            raise ValueError("应用数据缺少mode字段")
        
        # 验证工作流数据
        if 'graph' not in workflow_config:
            raise ValueError("工作流数据缺少graph字段")
        
        graph = workflow_config['graph']
        if 'nodes' not in graph:
            raise ValueError("工作流图缺少nodes字段")
        if 'edges' not in graph:
            raise ValueError("工作流图缺少edges字段")
    
    def _save_workflow_data(self, app_id: str, workflow_data: Dict[str, Any], format_type: str) -> None:
        """保存工作流数据到文件"""
        if not self.data_dir:
            raise RuntimeError("数据目录未初始化")
        
        # 备份现有数据
        existing_file = self.data_dir / f"{app_id}.{format_type}"
        if existing_file.exists():
            self._backup_existing_data(app_id, format_type)
        
        # 保存新数据
        if format_type == 'yaml':
            with open(existing_file, 'w', encoding='utf-8') as f:
                yaml.dump(workflow_data, f, allow_unicode=True, default_flow_style=False)
        else:
            with open(existing_file, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    
    def _backup_existing_data(self, app_id: str, format_type: str) -> None:
        """备份现有数据"""
        if not self.backup_dir:
            return
        
        existing_file = self.data_dir / f"{app_id}.{format_type}"
        if not existing_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{app_id}_{timestamp}.{format_type}"
        
        shutil.copy2(existing_file, backup_file)
        logging.info(f"已备份现有数据: {backup_file}")
    
    def get_app_by_id(self, app_id: str) -> Optional[App]:
        """根据应用ID获取应用信息"""
        if not self.config.is_manual_enabled():
            return None
        
        workflow_data = self._load_workflow_data(app_id)
        if not workflow_data:
            return None
        
        try:
            app_data = workflow_data['app']
            return App(
                id=app_id,
                name=app_data.get('name', f'工作流应用 {app_id[:8]}'),
                mode=app_data.get('mode', AppMode.WORKFLOW.value),
                icon=app_data.get('icon', '🤖'),
                icon_type=app_data.get('icon_type', 'emoji'),
                icon_background=app_data.get('icon_background', '#FFEAD5'),
                description=app_data.get('description', ''),
                use_icon_as_answer_icon=app_data.get('use_icon_as_answer_icon', False),
                tenant_id=app_data.get('tenant_id', '')
            )
        except Exception as e:
            logging.error(f"解析应用数据失败: {e}")
            return None
    
    def get_workflow_by_app_id(self, app_id: str) -> Optional[Workflow]:
        """根据应用ID获取工作流信息"""
        if not self.config.is_manual_enabled():
            return None
        
        workflow_data = self._load_workflow_data(app_id)
        if not workflow_data:
            return None
        
        try:
            workflow_config = workflow_data['workflow']
            
            # 解析环境变量
            environment_variables = []
            for env_var in workflow_config.get('environment_variables', []):
                environment_variables.append(
                    EnvironmentVariable(
                        name=env_var['name'],
                        value=env_var['value'],
                        value_type=env_var.get('value_type', 'string')
                    )
                )
            
            return Workflow(
                id=workflow_config.get('id', app_id),
                app_id=app_id,
                version=workflow_config.get('version', '1.0'),
                graph=workflow_config.get('graph', {}),
                features=workflow_config.get('features', {}),
                environment_variables=environment_variables
            )
        except Exception as e:
            logging.error(f"解析工作流数据失败: {e}")
            return None
    
    def _load_workflow_data(self, app_id: str) -> Optional[Dict[str, Any]]:
        """加载工作流数据"""
        if not self.data_dir:
            return None
        
        # 尝试不同的文件格式
        formats = ['json', 'yaml', 'yml']
        
        for fmt in formats:
            file_path = self.data_dir / f"{app_id}.{fmt}"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if fmt in ['yaml', 'yml']:
                            return yaml.safe_load(f)
                        else:
                            return json.load(f)
                except Exception as e:
                    logging.error(f"加载数据文件失败: {file_path} - {e}")
                    continue
        
        return None
    
    def get_available_apps(self) -> List[str]:
        """获取可用的应用ID列表"""
        if not self.config.is_manual_enabled() or not self.data_dir:
            return []
        
        app_ids = []
        for file_path in self.data_dir.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
                app_id = file_path.stem
                app_ids.append(app_id)
        
        return sorted(app_ids)
    
    def delete_app_data(self, app_id: str) -> bool:
        """删除应用数据"""
        if not self.config.is_manual_enabled() or not self.data_dir:
            return False
        
        try:
            # 备份数据
            self._backup_existing_data(app_id, 'json')
            self._backup_existing_data(app_id, 'yaml')
            self._backup_existing_data(app_id, 'yml')
            
            # 删除数据文件
            formats = ['json', 'yaml', 'yml']
            deleted = False
            
            for fmt in formats:
                file_path = self.data_dir / f"{app_id}.{fmt}"
                if file_path.exists():
                    file_path.unlink()
                    deleted = True
                    logging.info(f"已删除数据文件: {file_path}")
            
            return deleted
            
        except Exception as e:
            logging.error(f"删除应用数据失败: {e}")
            return False
    
    def update_app_data(self, app_id: str, workflow_data: Dict[str, Any]) -> bool:
        """更新应用数据"""
        return self.import_workflow_data(app_id, workflow_data)
    
    def export_app_data(self, app_id: str, format_type: str = 'yaml') -> Optional[str]:
        """导出应用数据"""
        workflow_data = self._load_workflow_data(app_id)
        if not workflow_data:
            return None
        
        try:
            if format_type == 'yaml':
                return yaml.dump(workflow_data, allow_unicode=True, default_flow_style=False)
            else:
                return json.dumps(workflow_data, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"导出应用数据失败: {e}")
            return None
    
    def get_app_stats(self) -> Dict[str, Any]:
        """获取应用统计信息"""
        if not self.config.is_manual_enabled() or not self.data_dir:
            return {}
        
        stats = {
            'total_apps': 0,
            'total_size': 0,
            'last_updated': None,
            'formats': {'json': 0, 'yaml': 0, 'yml': 0}
        }
        
        for file_path in self.data_dir.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
                stats['total_apps'] += 1
                stats['total_size'] += file_path.stat().st_size
                
                format_key = file_path.suffix.lower().lstrip('.')
                stats['formats'][format_key] += 1
                
                modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if not stats['last_updated'] or modified_time > stats['last_updated']:
                    stats['last_updated'] = modified_time
        
        return stats


# 全局手动导入服务实例
manual_import_service = ManualImportService() 