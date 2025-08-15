export interface App {
  id: string;
  name: string;
  mode: string;
  icon: string;
  icon_type: string;
  icon_background: string;
  description: string;
  use_icon_as_answer_icon: boolean;
}

export interface EnvironmentVariable {
  name: string;
  value: string;
  value_type: 'string' | 'secret';
}

export interface WorkflowNode {
  id: string;
  type: string;
  data: any;
  position: {
    x: number;
    y: number;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  source_handle: string;
  target_handle: string;
}

export interface Workflow {
  id: string;
  app_id: string;
  version: string;
  graph: {
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
  };
  features: any;
  environment_variables: EnvironmentVariable[];
}

export interface WorkflowSummary {
  id: string;
  app_id: string;
  app_name: string;
  version: string;
  name: string;
  node_count: number;
  has_secret_variables: boolean;
  last_modified: string;
  description?: string;
  app_mode?: string; // 应用模式类型
}

export interface PaginationInfo {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface WorkflowListResponse {
  workflows: WorkflowSummary[];
  pagination: PaginationInfo;
  stats?: Record<string, number>; // 添加全量应用类型统计
}

export interface WorkflowListParams {
  page?: number;
  page_size?: number;
  search?: string;
}

export interface BatchExportRequest {
  app_ids: string[];
  include_secret: boolean;
  export_format: 'zip' | 'individual';
}

export interface BatchExportResult {
  app_id: string;
  success: boolean;
  data?: string;
  filename?: string;
  error?: string;
}

export interface BatchExportResponse {
  export_format: 'zip' | 'individual';
  filename?: string;
  data?: string; // base64 encoded for zip format
  results: BatchExportResult[];
  success_count: number;
  total_count: number;
}

// 工作流导入相关类型定义
export interface DifyInstance {
  id: string;
  name: string;
  url: string;
  auth_type: 'bearer' | 'basic' | 'api_key';
  auth_config: {
    token?: string;
    username?: string;
    password?: string;
    api_key?: string;
    api_key_header?: string;
  };
  is_default?: boolean;
}

export interface WorkflowImportRequest {
  mode: 'yaml-content' | 'yaml-url';
  yaml_content?: string;
  yaml_url?: string;
  name?: string;
  description?: string;
  icon_type?: 'emoji' | 'link';
  icon?: string;
  icon_background?: string;
  app_id?: string;
  target_instance_id?: string; // 目标Dify实例ID
}

export interface WorkflowImportResponse {
  import_id: string;
  status: 'completed' | 'completed-with-warnings' | 'pending' | 'failed';
  app_id?: string;
  app_mode?: string;
  current_dsl_version?: string;
  imported_dsl_version?: string;
  error?: string;
  warnings?: string[];
  dependencies?: ImportDependency[];
}

export interface ImportDependency {
  type: 'tool' | 'model_provider' | 'rerank_model';
  value: any;
  current_identifier?: string;
  missing?: boolean;
}

export interface BatchImportRequest {
  files: WorkflowImportFile[];
  target_instance_id: string;
  import_options: {
    overwrite_existing: boolean;
    ignore_errors: boolean;
    create_new_on_conflict: boolean;
  };
}

export interface WorkflowImportFile {
  filename: string;
  content: string;
  name?: string;
  description?: string;
}

export interface BatchImportResult {
  filename: string;
  success: boolean;
  app_id?: string;
  app_name?: string;
  import_id?: string;
  status?: WorkflowImportResponse['status'];
  error?: string;
  warnings?: string[];
}

export interface BatchImportResponse {
  results: BatchImportResult[];
  success_count: number;
  total_count: number;
  failed_count: number;
  warning_count: number;
} 