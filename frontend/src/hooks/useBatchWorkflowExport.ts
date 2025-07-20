import { useState, useCallback } from 'react';
import { ApiService } from '../services/api';
import { WorkflowSummary, BatchExportRequest, BatchExportResponse, PaginationInfo, WorkflowListParams } from '../types';

export const useBatchWorkflowExport = () => {
  const [workflows, setWorkflows] = useState<WorkflowSummary[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  });
  const [stats, setStats] = useState<Record<string, number>>({});
  const [selectedWorkflows, setSelectedWorkflows] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [exportProgress, setExportProgress] = useState<{
    current: number;
    total: number;
    currentWorkflow?: string;
  }>({ current: 0, total: 0 });

  const getAllWorkflows = useCallback(async (params: WorkflowListParams = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.getAllWorkflows({
        page: params.page || pagination.page,
        page_size: params.page_size || pagination.page_size,
        search: params.search !== undefined ? params.search : searchKeyword,
        ...params
      });
      
      setWorkflows(response.workflows);
      setPagination(response.pagination);
      setStats(response.stats || {});
      
      // 获取当前页面的工作流ID
      const currentPageAppIds = new Set(response.workflows.map(w => w.app_id));
      
      // 只保留当前页面的选择，清除其他页面的选择
      setSelectedWorkflows(prev => {
        const newSelection = new Set();
        prev.forEach(appId => {
          if (currentPageAppIds.has(appId)) {
            newSelection.add(appId);
          }
        });
        return newSelection;
      });
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.page_size, searchKeyword]);

  const refreshWorkflows = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 先调用刷新接口清除缓存
      await ApiService.refreshWorkflows();
      
      // 然后重新获取数据
      const response = await ApiService.getAllWorkflows({
        page: 1, // 刷新后回到第一页
        page_size: pagination.page_size,
        search: searchKeyword,
      });
      
      setWorkflows(response.workflows);
      setPagination(response.pagination);
      setStats(response.stats || {});
      
      // 清除所有选择
      setSelectedWorkflows(new Set());
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [pagination.page_size, searchKeyword]);

  const goToPage = useCallback(async (page: number) => {
    if (page >= 1 && page <= pagination.total_pages) {
      try {
        // 先获取目标页面的数据，以便知道哪些选择需要保留
        const response = await ApiService.getAllWorkflows({ 
          page, 
          page_size: pagination.page_size,
          search: searchKeyword 
        });
        
        // 获取目标页面的工作流ID
        const targetPageAppIds = new Set(response.workflows.map(w => w.app_id));
        
        // 只保留目标页面的选择，清除其他页面的选择
        setSelectedWorkflows(prev => {
          const newSelection = new Set();
          prev.forEach(appId => {
            if (targetPageAppIds.has(appId)) {
              newSelection.add(appId);
            }
          });
          return newSelection;
        });
        
        // 更新工作流列表和分页信息
        setWorkflows(response.workflows);
        setPagination(response.pagination);
        
      } catch (err: any) {
        setError(err.message);
        // 如果出错，仍然尝试正常跳转页面
        getAllWorkflows({ page });
      }
    }
  }, [pagination.page_size, pagination.total_pages, searchKeyword, getAllWorkflows]);

  const changePageSize = useCallback(async (pageSize: number) => {
    try {
      // 获取新页面大小的第一页数据
      const response = await ApiService.getAllWorkflows({ 
        page: 1, 
        page_size: pageSize,
        search: searchKeyword 
      });
      
      // 获取新第一页的工作流ID
      const newPageAppIds = new Set(response.workflows.map(w => w.app_id));
      
      // 只保留新第一页的选择
      setSelectedWorkflows(prev => {
        const newSelection = new Set();
        prev.forEach(appId => {
          if (newPageAppIds.has(appId)) {
            newSelection.add(appId);
          }
        });
        return newSelection;
      });
      
      // 更新工作流列表和分页信息
      setWorkflows(response.workflows);
      setPagination(response.pagination);
      
    } catch (err: any) {
      setError(err.message);
      // 如果出错，仍然尝试正常操作
      getAllWorkflows({ page: 1, page_size: pageSize });
    }
  }, [searchKeyword, getAllWorkflows]);

  const handleSearch = useCallback(async (keyword: string) => {
    setSearchKeyword(keyword);
    
    try {
      // 搜索时获取第一页数据
      const response = await ApiService.getAllWorkflows({ 
        page: 1, 
        page_size: pagination.page_size,
        search: keyword 
      });
      
      // 获取搜索结果第一页的工作流ID
      const searchPageAppIds = new Set(response.workflows.map(w => w.app_id));
      
      // 只保留搜索结果第一页的选择
      setSelectedWorkflows(prev => {
        const newSelection = new Set();
        prev.forEach(appId => {
          if (searchPageAppIds.has(appId)) {
            newSelection.add(appId);
          }
        });
        return newSelection;
      });
      
      // 更新工作流列表和分页信息
      setWorkflows(response.workflows);
      setPagination(response.pagination);
      
    } catch (err: any) {
      setError(err.message);
      // 如果出错，仍然尝试正常搜索
      getAllWorkflows({ page: 1, search: keyword });
    }
  }, [pagination.page_size, getAllWorkflows]);

  const toggleWorkflowSelection = useCallback((appId: string) => {
    setSelectedWorkflows(prev => {
      const newSelection = new Set(prev);
      if (newSelection.has(appId)) {
        newSelection.delete(appId);
      } else {
        newSelection.add(appId);
      }
      return newSelection;
    });
  }, []);

  const selectAllWorkflows = useCallback(() => {
    // 只选择当前页面的所有工作流
    const currentPageAppIds = workflows.map(w => w.app_id);
    setSelectedWorkflows(prev => {
      const newSelection = new Set(prev);
      currentPageAppIds.forEach(appId => newSelection.add(appId));
      return newSelection;
    });
  }, [workflows]);

  const deselectAllWorkflows = useCallback(() => {
    // 只取消当前页面的选择
    const currentPageAppIds = new Set(workflows.map(w => w.app_id));
    setSelectedWorkflows(prev => {
      const newSelection = new Set();
      prev.forEach(appId => {
        if (!currentPageAppIds.has(appId)) {
          newSelection.add(appId);
        }
      });
      return newSelection;
    });
  }, [workflows]);

  const selectAllInCurrentPage = useCallback(() => {
    const currentPageAppIds = workflows.map(w => w.app_id);
    setSelectedWorkflows(prev => {
      const newSelection = new Set(prev);
      currentPageAppIds.forEach(appId => newSelection.add(appId));
      return newSelection;
    });
  }, [workflows]);

  const deselectAllInCurrentPage = useCallback(() => {
    const currentPageAppIds = new Set(workflows.map(w => w.app_id));
    setSelectedWorkflows(prev => {
      const newSelection = new Set();
      prev.forEach(appId => {
        if (!currentPageAppIds.has(appId)) {
          newSelection.add(appId);
        }
      });
      return newSelection;
    });
  }, [workflows]);

  const toggleAllInCurrentPage = useCallback(() => {
    const currentPageAppIds = workflows.map(w => w.app_id);
    const allCurrentPageSelected = currentPageAppIds.length > 0 && currentPageAppIds.every(appId => 
      selectedWorkflows.has(appId)
    );
    
    if (allCurrentPageSelected) {
      deselectAllInCurrentPage();
    } else {
      selectAllInCurrentPage();
    }
  }, [workflows, selectedWorkflows, selectAllInCurrentPage, deselectAllInCurrentPage]);

  const clearAllSelections = useCallback(() => {
    // 清除所有选择（包括其他页面的）
    setSelectedWorkflows(new Set());
  }, []);

  const batchExportWorkflows = useCallback(async (
    includeSecret: boolean = false,
    exportFormat: 'zip' | 'individual' = 'zip'
  ): Promise<BatchExportResponse | null> => {
    if (selectedWorkflows.size === 0) {
      setError('请选择至少一个工作流');
      return null;
    }

    setExporting(true);
    setError(null);
    setExportProgress({ current: 0, total: selectedWorkflows.size });

    try {
      const request: BatchExportRequest = {
        app_ids: Array.from(selectedWorkflows),
        include_secret: includeSecret,
        export_format: exportFormat
      };

      const response = await ApiService.batchExportWorkflows(request);
      
      // 处理ZIP文件下载
      if (response.export_format === 'zip' && response.data && response.filename) {
        downloadZipFile(response.data, response.filename);
      }

      setExportProgress({ current: response.success_count, total: response.total_count });
      
      return response;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setExporting(false);
    }
  }, [selectedWorkflows]);

  const downloadZipFile = useCallback((base64Data: string, filename: string) => {
    try {
      // 将base64转换为Blob
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/zip' });

      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(`文件下载失败: ${err.message}`);
    }
  }, []);

  const downloadIndividualFiles = useCallback((results: any[]) => {
    results.forEach(result => {
      if (result.success && result.data && result.filename) {
        const blob = new Blob([result.data], { type: 'application/x-yaml' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = result.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    });
  }, []);

  return {
    workflows,
    pagination,
    stats,
    selectedWorkflows,
    loading,
    exporting,
    error,
    searchKeyword,
    exportProgress,
    getAllWorkflows,
    refreshWorkflows,
    goToPage,
    changePageSize,
    handleSearch,
    toggleWorkflowSelection,
    selectAllWorkflows,
    deselectAllWorkflows,
    selectAllInCurrentPage,
    deselectAllInCurrentPage,
    toggleAllInCurrentPage,
    clearAllSelections,
    batchExportWorkflows,
    downloadIndividualFiles,
  };
}; 