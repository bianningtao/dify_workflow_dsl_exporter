import { Workflow } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

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
} 