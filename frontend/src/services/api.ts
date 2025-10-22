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
    // 使用 axiosInstance 以自动添加 Authorization token
    const response = await axiosInstance.get(`/apps/${appId}/export`, {
      params: { include_secret: includeSecret }
    });
    return response.data;
  }
  
  static async getWorkflowDraft(appId: string): Promise<Workflow> {
    // 使用 axiosInstance 以自动添加 Authorization token
    const response = await axiosInstance.get<Workflow>(`/apps/${appId}/workflows/draft`);
    return response.data;
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
    // 使用 axiosInstance 以自动添加 Authorization token
    const response = await axiosInstance.post<BatchExportResponse>('/workflows/batch-export', request);
    return response.data;
  }
  
  static async refreshWorkflows(): Promise<{ success: boolean; message: string }> {
    // 使用 axiosInstance 以自动添加 Authorization token
    const response = await axiosInstance.post<{ success: boolean; message: string }>('/workflows/refresh');
    return response.data;
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
    // 使用 axiosInstance 以自动添加 Authorization token
    const response = await axiosInstance.post<{ valid: boolean; error?: string; app_info?: any }>(
      '/workflows/validate',
      { yaml_content: yamlContent }
    );
    return response.data;
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