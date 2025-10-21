import axios from 'axios';
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
  DifyInstance,
  SystemConfig
} from '../types';

// 使用相对路径，在Docker中通过Nginx代理，在开发中直接访问后端
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5001/api';

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: true,  // 允许跨域请求携带凭证
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 自动添加token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    console.log('[API拦截器] Token:', token ? `${token.substring(0, 20)}...` : 'null');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('[API拦截器] 已添加 Authorization header');
    } else {
      console.warn('[API拦截器] 未找到 auth_token');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理401错误
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除token并跳转到登录页
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      
      // 如果不在登录页，则跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// 导出axios实例供其他地方使用
export default axiosInstance;

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
    const searchParams: Record<string, string> = {};
    
    if (params.page) {
      searchParams.page = params.page.toString();
    }
    if (params.page_size) {
      searchParams.page_size = params.page_size.toString();
    }
    if (params.search) {
      searchParams.search = params.search;
    }
    
    const response = await axiosInstance.get('/workflows', { params: searchParams });
    return response.data;
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
    const response = await axiosInstance.post('/workflows/import', request);
    return response.data;
  }

  static async confirmImport(importId: string, targetInstanceId: string): Promise<WorkflowImportResponse> {
    const response = await axiosInstance.post(`/workflows/import/${importId}/confirm`, {
      target_instance_id: targetInstanceId
    });
    return response.data;
  }

  static async batchImportWorkflows(request: BatchImportRequest): Promise<BatchImportResponse> {
    const response = await axiosInstance.post('/workflows/batch-import', request);
    return response.data;
  }

  static async getTargetInstances(): Promise<{ instances: DifyInstance[] }> {
    const response = await axiosInstance.get('/target-instances');
    return response.data;
  }

  static async testTargetInstance(instanceId: string): Promise<{ instance_id: string; status: string }> {
    const response = await axiosInstance.post(`/target-instances/${instanceId}/test`);
    return response.data;
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

  // 配置管理相关API
  static async getConfig(): Promise<{ success: boolean; data: SystemConfig }> {
    const response = await axiosInstance.get('/config');
    return response.data;
  }

  static async getConfigDefaults(): Promise<{ success: boolean; data: SystemConfig }> {
    const response = await axiosInstance.get('/config/defaults');
    return response.data;
  }

  static async updateConfig(config: SystemConfig): Promise<{ success: boolean; message: string }> {
    const response = await axiosInstance.put('/config', config);
    return response.data;
  }

  static async resetConfig(): Promise<{ success: boolean; message: string }> {
    const response = await axiosInstance.post('/config/reset');
    return response.data;
  }

  static async validateConfig(config: SystemConfig): Promise<{ success: boolean; valid: boolean; message?: string }> {
    const response = await axiosInstance.post('/config/validate', config);
    return response.data;
  }

  static async testConnection(config: SystemConfig): Promise<{ success: boolean; message: string; details?: any }> {
    const response = await axiosInstance.post('/config/test-connection', config);
    return response.data;
  }
} 