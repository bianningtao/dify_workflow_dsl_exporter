import React, { useState, useEffect } from 'react';
import { useWorkflowExport } from '../hooks/useWorkflowExport';
import { Workflow } from '../types';
import ExportConfirmModal from './ExportConfirmModal';

const WorkflowExporter: React.FC = () => {
  const [appId, setAppId] = useState('');
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [showModal, setShowModal] = useState(false);
  const { exportWorkflow, getWorkflowDraft, exporting, loading, error } = useWorkflowExport();

  const handleGetWorkflow = async () => {
    if (!appId.trim()) return;
    
    const workflowData = await getWorkflowDraft(appId);
    setWorkflow(workflowData);
  };

  const handleExport = async () => {
    if (!workflow) return;
    
    const secretVariables = workflow.environment_variables.filter(env => env.value_type === 'secret');
    
    if (secretVariables.length > 0) {
      setShowModal(true);
    } else {
      await exportWorkflow(appId, false);
    }
  };

  const handleConfirmExport = async (includeSecret: boolean) => {
    await exportWorkflow(appId, includeSecret);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8 text-center">工作流 DSL 导出器</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
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
            disabled={loading || !appId.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? '加载中...' : '获取工作流'}
          </button>
        </div>
        
        {error && (
          <div className="text-red-600 text-sm mb-4">
            错误: {error}
          </div>
        )}
      </div>

      {workflow && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">工作流信息</h2>
            <button
              onClick={handleExport}
              disabled={exporting}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
            >
              {exporting ? '导出中...' : '导出 DSL'}
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

      <ExportConfirmModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onConfirm={handleConfirmExport}
        environmentVariables={workflow?.environment_variables || []}
      />
    </div>
  );
};

export default WorkflowExporter; 