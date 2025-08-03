import { 
  Workflow, 
  WorkflowListResponse, 
  WorkflowListParams, 
  BatchExportRequest, 
  BatchExportResponse,
  WorkflowImportRequest,
  WorkflowImportResponse,
  BatchImportRequest,
  BatchImportResponse,
  DifyInstance
} from '../types';

// 使用相对路径，在Docker中通过Nginx代理，在开发中直接访问后端
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5000/api';

export class ApiService {
  static async exportAppConfig(appId: string, includeSecret: boolean = false): Promise<{ data: string }> {
    const response = await fetch(`${API_BASE_URL}/apps/${appId}/export?include_secret=${includeSecret}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async getWorkflowDraft(appId: string): Promise<Workflow> {
    const response = await fetch(`${API_BASE_URL}/apps/${appId}/workflows/draft`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Get workflow draft failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async getAllWorkflows(params: WorkflowListParams = {}): Promise<WorkflowListResponse> {
    const searchParams = new URLSearchParams();
    
    if (params.page) {
      searchParams.append('page', params.page.toString());
    }
    if (params.page_size) {
      searchParams.append('page_size', params.page_size.toString());
    }
    if (params.search) {
      searchParams.append('search', params.search);
    }
    
    const url = `${API_BASE_URL}/workflows${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Get workflows failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async batchExportWorkflows(request: BatchExportRequest): Promise<BatchExportResponse> {
    const response = await fetch(`${API_BASE_URL}/workflows/batch-export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      throw new Error(`Batch export failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  static async refreshWorkflows(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/workflows/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Refresh failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  // 工作流导入相关API
  static async importWorkflow(request: WorkflowImportRequest): Promise<WorkflowImportResponse> {
    const response = await fetch(`${API_BASE_URL}/workflows/import`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Import failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async confirmImport(importId: string, targetInstanceId: string): Promise<WorkflowImportResponse> {
    const response = await fetch(`${API_BASE_URL}/workflows/import/${importId}/confirm`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ target_instance_id: targetInstanceId }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Confirm import failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async batchImportWorkflows(request: BatchImportRequest): Promise<BatchImportResponse> {
    const response = await fetch(`${API_BASE_URL}/workflows/batch-import`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Batch import failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async getTargetInstances(): Promise<{ instances: DifyInstance[] }> {
    const response = await fetch(`${API_BASE_URL}/target-instances`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Get target instances failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async testTargetInstance(instanceId: string): Promise<{ instance_id: string; status: string }> {
    const response = await fetch(`${API_BASE_URL}/target-instances/${instanceId}/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Test connection failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async validateWorkflowFile(yamlContent: string): Promise<{ valid: boolean; error?: string; app_info?: any }> {
    const response = await fetch(`${API_BASE_URL}/workflows/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ yaml_content: yamlContent }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Validation failed: ${response.statusText}`);
    }
    
    return response.json();
  }
} 