import { Workflow, WorkflowListResponse, WorkflowListParams, BatchExportRequest, BatchExportResponse } from '../types';

// 使用相对路径，在Docker中通过Nginx代理，在开发中直接访问后端
const API_BASE_URL = '/api';

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
} 