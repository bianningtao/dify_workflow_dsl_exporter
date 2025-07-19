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