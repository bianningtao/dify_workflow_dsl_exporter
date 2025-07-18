import { useState, useCallback } from 'react';
import { ApiService } from '../services/api';
import { Workflow } from '../types';

export const useWorkflowExport = () => {
  const [exporting, setExporting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportWorkflow = useCallback(async (appId: string, includeSecret: boolean = false) => {
    if (exporting) return;
    
    setExporting(true);
    setError(null);
    
    try {
      const { data } = await ApiService.exportAppConfig(appId, includeSecret);
      
      // 创建下载链接
      const blob = new Blob([data], { type: 'application/yaml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `workflow-${appId}.yml`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setExporting(false);
    }
  }, [exporting]);

  const getWorkflowDraft = useCallback(async (appId: string): Promise<Workflow | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const workflow = await ApiService.getWorkflowDraft(appId);
      return workflow;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Get workflow failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    exportWorkflow,
    getWorkflowDraft,
    exporting,
    loading,
    error,
  };
}; 