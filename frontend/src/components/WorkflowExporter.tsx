import React, { useState, useEffect } from 'react';
import { useWorkflowExport } from '../hooks/useWorkflowExport';
import { useBatchWorkflowExport } from '../hooks/useBatchWorkflowExport';
import { Workflow, WorkflowSummary, WorkflowImportResponse, BatchImportResponse } from '../types';
import ExportConfirmModal from './ExportConfirmModal';
import BatchExportModal from './BatchExportModal';
import WorkflowImporter from './WorkflowImporter';
import BatchImportModal from './BatchImportModal';
import SuccessModal from './SuccessModal';
import AppTypeTag from './AppTypeTag';
import AppTypeStats from './AppTypeStats';
import Pagination from './Pagination';

const WorkflowExporter: React.FC = () => {
  // 主菜单模式：export 或 import
  const [mainMode, setMainMode] = useState<'export' | 'import'>('export');
  // 子菜单模式：batch 或 single
  const [subMode, setSubMode] = useState<'batch' | 'single'>('batch');
  const [appId, setAppId] = useState('');
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [showSingleModal, setShowSingleModal] = useState(false);
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [showBatchImportModal, setShowBatchImportModal] = useState(false);
  
  // 成功弹窗状态
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successData, setSuccessData] = useState<{
    title: string;
    message: string;
    appId?: string;
    statistics?: {
      successCount: number;
      totalCount: number;
      failedCount: number;
    };
  } | null>(null);
  
  // 单个工作流导出相关
  const { exportWorkflow, getWorkflowDraft, exporting: singleExporting, loading: singleLoading, error: singleError } = useWorkflowExport();
  
  // 批量工作流导出相关
  const {
    workflows,
    pagination,
    stats,
    selectedWorkflows,
    loading: batchLoading,
    exporting: batchExporting,
    error: batchError,
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
  } = useBatchWorkflowExport();

  // 搜索输入状态
  const [searchInput, setSearchInput] = useState('');

  // 初始加载所有工作流
  useEffect(() => {
    getAllWorkflows();
  }, [getAllWorkflows]);

  // 单个工作流相关处理
  const handleGetWorkflow = async () => {
    if (!appId.trim()) return;
    
    const workflowData = await getWorkflowDraft(appId);
    setWorkflow(workflowData);
  };

  const handleSingleExport = async () => {
    if (!workflow) return;
    
    const secretVariables = workflow.environment_variables.filter(env => env.value_type === 'secret');
    
    if (secretVariables.length > 0) {
      setShowSingleModal(true);
    } else {
      await exportWorkflow(appId, false);
    }
  };

  const handleConfirmSingleExport = async (includeSecret: boolean) => {
    await exportWorkflow(appId, includeSecret);
    setShowSingleModal(false);
  };

  // 批量导出相关处理
  const handleBatchExport = () => {
    if (selectedWorkflows.size === 0) return;
    
    const selectedWorkflowsData = workflows.filter(w => selectedWorkflows.has(w.app_id));
    
    setShowBatchModal(true);
  };

  const handleConfirmBatchExport = async (includeSecret: boolean, exportFormat: 'zip' | 'individual') => {
    const response = await batchExportWorkflows(includeSecret, exportFormat);
    
    if (response && exportFormat === 'individual' && response.results) {
      downloadIndividualFiles(response.results);
    }
    
    setShowBatchModal(false);
  };

  // 搜索处理
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(searchInput);
  };

  const clearSearch = () => {
    setSearchInput('');
    handleSearch('');
  };

  const selectedWorkflowsData = workflows.filter(w => selectedWorkflows.has(w.app_id));
  const hasSecretVariables = selectedWorkflowsData.some(w => w.has_secret_variables);

  // 导入成功处理
  const handleImportSuccess = (result: WorkflowImportResponse | BatchImportResponse) => {
    // 刷新工作流列表
    refreshWorkflows();
    
    // 显示优雅的成功弹窗
    if ('results' in result) {
      // 批量导入结果
      setSuccessData({
        title: '批量导入完成！',
        message: `成功处理了您的工作流批量导入请求`,
        statistics: {
          successCount: result.success_count,
          totalCount: result.total_count,
          failedCount: result.failed_count
        }
      });
    } else {
      // 单个导入结果
      setSuccessData({
        title: '工作流导入成功！',
        message: '您的工作流已成功导入到目标实例',
        appId: result.app_id
      });
    }
    setShowSuccessModal(true);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8 text-center">工作流 DSL 管理器</h1>
      
      {/* 主菜单 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-center space-x-8">
          <button
            onClick={() => {
              setMainMode('export');
              setSubMode('batch');
            }}
            className={`px-8 py-3 rounded-lg font-medium text-lg transition-all duration-200 ${
              mainMode === 'export'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            📤 工作流导出
          </button>
          <button
            onClick={() => {
              setMainMode('import');
              setSubMode('single');
            }}
            className={`px-8 py-3 rounded-lg font-medium text-lg transition-all duration-200 ${
              mainMode === 'import'
                ? 'bg-green-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            📥 工作流导入
          </button>
        </div>
      </div>

      {mainMode === 'export' ? (
        // 导出页面
        <div className="space-y-6">
          {/* 导出子菜单 */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-center space-x-4">
              <span className="font-medium text-gray-700">导出方式:</span>
          <label className="flex items-center">
            <input
              type="radio"
                  name="exportMode"
              value="batch"
                  checked={subMode === 'batch'}
                  onChange={() => setSubMode('batch')}
              className="mr-2"
            />
                <span className="font-medium">批量导出</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
                  name="exportMode"
              value="single"
                  checked={subMode === 'single'}
                  onChange={() => setSubMode('single')}
              className="mr-2"
            />
                <span className="font-medium">单个导出</span>
          </label>
        </div>
      </div>

          {subMode === 'batch' ? (
        // 批量导出模式
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">工作流列表</h2>
              <div className="flex items-center space-x-4">
                {/* 搜索框 */}
                <form onSubmit={handleSearchSubmit} className="flex items-center space-x-2">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="搜索工作流名称或应用ID..."
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                    />
                    <svg
                      className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <button
                    type="submit"
                    disabled={batchLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    搜索
                  </button>
                  {searchKeyword && (
                    <button
                      type="button"
                      onClick={clearSearch}
                      className="px-3 py-2 text-gray-600 hover:text-gray-800"
                    >
                      清除
                    </button>
                  )}
                </form>
                
                <button
                  onClick={() => refreshWorkflows()}
                  disabled={batchLoading}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg disabled:bg-gray-100 disabled:text-gray-400"
                >
                  刷新列表
                </button>
              </div>
            </div>

            {/* 应用类型统计 */}
            <AppTypeStats stats={stats} total={pagination.total} className="mb-6" />

            {/* 搜索结果提示 */}
            {searchKeyword && (
              <div className="mb-4 p-3 bg-blue-50 border-l-4 border-blue-400 text-blue-700">
                <p>搜索关键词：<span className="font-semibold">"{searchKeyword}"</span>，找到 {pagination.total} 个结果</p>
              </div>
            )}

            {batchError && (
              <div className="text-red-600 text-sm mb-4">
                错误: {batchError}
              </div>
            )}

            {workflows.length > 0 ? (
              <div>
                {/* 批量操作按钮 */}
                <div className="flex justify-between items-center mb-4">
                  <div className="flex space-x-3">
                    {(() => {
                      // 计算当前页面的选择状态
                      const currentPageAppIds = workflows.map(w => w.app_id);
                      const selectedInCurrentPage = currentPageAppIds.filter(appId => selectedWorkflows.has(appId)).length;
                      const allCurrentPageSelected = currentPageAppIds.length > 0 && selectedInCurrentPage === currentPageAppIds.length;
                      const hasAnySelection = selectedWorkflows.size > 0;
                      
                      return (
                        <>
                          <button
                            onClick={selectAllWorkflows}
                            disabled={allCurrentPageSelected}
                            className={`px-3 py-2 text-sm rounded ${
                              allCurrentPageSelected 
                                ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                                : 'bg-gray-100 hover:bg-gray-200'
                            }`}
                          >
                            选择本页
                          </button>
                          
                          <button
                            onClick={deselectAllWorkflows}
                            disabled={selectedInCurrentPage === 0}
                            className={`px-3 py-2 text-sm rounded ${
                              selectedInCurrentPage === 0
                                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                : 'bg-gray-100 hover:bg-gray-200'
                            }`}
                          >
                            取消本页
                          </button>
                          
                          {hasAnySelection && (
                            <button
                              onClick={clearAllSelections}
                              className="px-3 py-2 text-sm bg-red-100 text-red-700 hover:bg-red-200 rounded"
                            >
                              清空所有 ({selectedWorkflows.size})
                            </button>
                          )}
                        </>
                      );
                    })()}
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className="text-sm text-gray-600">
                      {(() => {
                        const currentPageAppIds = workflows.map(w => w.app_id);
                        const selectedInCurrentPage = currentPageAppIds.filter(appId => selectedWorkflows.has(appId)).length;
                        return `本页 ${selectedInCurrentPage}/${currentPageAppIds.length}，总选择 ${selectedWorkflows.size} 个`;
                      })()}
                    </span>
                    <button
                      onClick={handleBatchExport}
                      disabled={selectedWorkflows.size === 0 || batchExporting}
                      className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                    >
                      {batchExporting ? '导出中...' : '批量导出'}
                    </button>
                  </div>
                </div>

                {/* 导出进度 */}
                {batchExporting && exportProgress.total > 0 && (
                  <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-blue-800">导出进度</span>
                      <span className="text-sm text-blue-600">
                        {exportProgress.current} / {exportProgress.total}
                      </span>
                    </div>
                    <div className="w-full bg-blue-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(exportProgress.current / exportProgress.total) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* 工作流列表 */}
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="max-h-96 overflow-y-auto">
                    {workflows.map((workflowSummary) => (
                      <div 
                        key={workflowSummary.app_id} 
                        className={`p-4 border-b last:border-b-0 hover:bg-gray-50 cursor-pointer transition-colors ${
                          selectedWorkflows.has(workflowSummary.app_id) ? 'bg-blue-50 border-blue-200' : ''
                        }`}
                        onClick={(e) => {
                          // 防止点击checkbox时重复触发
                          if (e.target instanceof HTMLInputElement && e.target.type === 'checkbox') {
                            return;
                          }
                          toggleWorkflowSelection(workflowSummary.app_id);
                        }}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <input
                              type="checkbox"
                              checked={selectedWorkflows.has(workflowSummary.app_id)}
                              onChange={(e) => {
                                e.stopPropagation();
                                toggleWorkflowSelection(workflowSummary.app_id);
                              }}
                              className="h-4 w-4 text-blue-600 rounded cursor-pointer"
                            />
                            <div className="min-w-0 flex-1">
                              <div className="font-medium text-gray-900 truncate">
                                {workflowSummary.app_name || workflowSummary.name}
                              </div>
                              <div className="text-sm text-gray-600">
                                应用ID: {workflowSummary.app_id} | 版本: {workflowSummary.version}
                              </div>
                              {workflowSummary.description && (
                                <div className="text-xs text-gray-500 truncate mt-1">
                                  {workflowSummary.description}
                                </div>
                              )}
                              <div className="text-xs text-gray-500 mt-1">
                                节点数: {workflowSummary.node_count} | 
                                最后修改: {new Date(workflowSummary.last_modified).toLocaleString()}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            {workflowSummary.has_secret_variables && (
                              <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                                敏感变量
                              </span>
                            )}
                            <AppTypeTag appMode={workflowSummary.app_mode || 'workflow'} />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 分页组件 */}
                <Pagination
                  pagination={pagination}
                  onPageChange={goToPage}
                  onPageSizeChange={changePageSize}
                  loading={batchLoading}
                />
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                {batchLoading ? '加载中...' : searchKeyword ? '没有找到匹配的工作流' : '暂无工作流数据'}
              </div>
            )}
        </div>
      ) : (
        // 单个导出模式
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            placeholder="请输入应用ID"
            value={appId}
            onChange={(e) => setAppId(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleGetWorkflow}
                disabled={singleLoading || !appId.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
                {singleLoading ? '加载中...' : '获取工作流'}
          </button>
        </div>
        
            {singleError && (
          <div className="text-red-600 text-sm mb-4">
                错误: {singleError}
          </div>
        )}
      </div>

      {workflow && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">工作流信息</h2>
            <button
                  onClick={handleSingleExport}
                  disabled={singleExporting}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
            >
                  {singleExporting ? '导出中...' : '导出 DSL'}
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">工作流ID</label>
              <div className="text-sm text-gray-600">{workflow.id}</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">应用ID</label>
              <div className="text-sm text-gray-600">{workflow.app_id}</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">版本</label>
              <div className="text-sm text-gray-600">{workflow.version}</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">节点数量</label>
              <div className="text-sm text-gray-600">{workflow.graph.nodes.length}</div>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">环境变量</h3>
            <div className="overflow-x-auto">
              <table className="w-full border border-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">名称</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">值</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">类型</th>
                  </tr>
                </thead>
                <tbody>
                  {workflow.environment_variables.map((env) => (
                    <tr key={env.name} className="border-t">
                      <td className="px-4 py-2 text-sm font-medium">{env.name}</td>
                      <td className="px-4 py-2 text-sm text-gray-600">
                        {env.value_type === 'secret' ? '***' : env.value}
                      </td>
                      <td className="px-4 py-2 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          env.value_type === 'secret' 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {env.value_type === 'secret' ? '敏感' : '普通'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-3">工作流节点</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {workflow.graph.nodes.map((node) => (
                <div key={node.id} className="border border-gray-200 rounded-lg p-3">
                  <div className="font-medium text-sm mb-1">{node.data.title || node.id}</div>
                  <div className="text-xs text-gray-600">{node.type}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
          )}
        </div>
          )}
        </div>
      ) : (
        // 导入页面
        <div className="space-y-6">
          {/* 导入子菜单 */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-center space-x-4">
              <span className="font-medium text-gray-700">导入方式:</span>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="importMode"
                  value="single"
                  checked={subMode === 'single'}
                  onChange={() => setSubMode('single')}
                  className="mr-2"
                />
                <span className="font-medium">单个导入</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="importMode"
                  value="batch"
                  checked={subMode === 'batch'}
                  onChange={() => setSubMode('batch')}
                  className="mr-2"
                />
                <span className="font-medium">批量导入</span>
              </label>
            </div>
          </div>

          {subMode === 'single' ? (
            // 单个导入模式 - 调整宽度与菜单栏一致
            <div className="bg-white rounded-lg shadow-md">
              <WorkflowImporter
                onImportSuccess={handleImportSuccess}
                onClose={() => setMainMode('export')}
                className="w-full"
              />
            </div>
          ) : (
            // 批量导入模式
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-center">
                <h2 className="text-xl font-semibold mb-4">批量工作流导入</h2>
                <p className="text-gray-600 mb-6">
                  选择多个YAML文件进行批量导入工作流
                </p>
                <button
                  onClick={() => setShowBatchImportModal(true)}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 text-lg font-medium"
                >
                  开始批量导入
                </button>
          </div>
            </div>
          )}
        </div>
      )}

      {/* 模态框 */}
      <ExportConfirmModal
        isOpen={showSingleModal}
        onClose={() => setShowSingleModal(false)}
        onConfirm={handleConfirmSingleExport}
        environmentVariables={workflow?.environment_variables || []}
      />

      <BatchExportModal
        isOpen={showBatchModal}
        onClose={() => setShowBatchModal(false)}
        onConfirm={handleConfirmBatchExport}
        selectedWorkflows={selectedWorkflowsData}
        hasSecretVariables={hasSecretVariables}
      />

      <BatchImportModal
        isOpen={showBatchImportModal}
        onClose={() => setShowBatchImportModal(false)}
        onImportSuccess={handleImportSuccess}
      />

      {/* 成功弹窗 */}
      <SuccessModal
        isOpen={showSuccessModal}
        onClose={() => {
          setShowSuccessModal(false);
          setSuccessData(null);
        }}
        title={successData?.title || ''}
        message={successData?.message || ''}
        appId={successData?.appId}
        statistics={successData?.statistics}
      />
    </div>
  );
};

export default WorkflowExporter; 