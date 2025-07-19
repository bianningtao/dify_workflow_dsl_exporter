import React, { useState } from 'react';
import { WorkflowSummary } from '../types';
import AppTypeTag from './AppTypeTag';

interface BatchExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (includeSecret: boolean, exportFormat: 'zip' | 'individual') => void;
  selectedWorkflows: WorkflowSummary[];
  hasSecretVariables: boolean;
}

const BatchExportModal: React.FC<BatchExportModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  selectedWorkflows,
  hasSecretVariables
}) => {
  const [includeSecret, setIncludeSecret] = useState(false);
  const [exportFormat, setExportFormat] = useState<'zip' | 'individual'>('zip');

  const handleConfirm = () => {
    onConfirm(includeSecret, exportFormat);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">批量导出应用</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-medium mb-3">选中的应用 ({selectedWorkflows.length} 个)</h3>
          <div className="max-h-40 overflow-y-auto border border-gray-200 rounded-lg">
            {selectedWorkflows.map((workflow) => (
              <div key={workflow.app_id} className="p-3 border-b last:border-b-0 flex justify-between items-center">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="font-medium">{workflow.name}</div>
                    <AppTypeTag appMode={workflow.app_mode || 'workflow'} className="text-xs" />
                  </div>
                  <div className="text-sm text-gray-600">
                    应用ID: {workflow.app_id} | 节点数: {workflow.node_count}
                  </div>
                </div>
                {workflow.has_secret_variables && (
                  <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                    包含敏感变量
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="mb-6">
          <h4 className="text-md font-medium mb-3">导出格式</h4>
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="radio"
                name="exportFormat"
                value="zip"
                checked={exportFormat === 'zip'}
                onChange={(e) => setExportFormat(e.target.value as 'zip')}
                className="mr-2"
              />
              <span className="font-medium">ZIP压缩包</span>
              <span className="text-sm text-gray-600 ml-2">
                (推荐：将所有文件打包成一个ZIP文件下载)
              </span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="exportFormat"
                value="individual"
                checked={exportFormat === 'individual'}
                onChange={(e) => setExportFormat(e.target.value as 'individual')}
                className="mr-2"
              />
              <span className="font-medium">单独文件</span>
              <span className="text-sm text-gray-600 ml-2">
                (每个工作流单独下载一个文件)
              </span>
            </label>
          </div>
        </div>

        {hasSecretVariables && (
          <div className="mb-6">
            <h4 className="text-md font-medium mb-3">敏感信息处理</h4>
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    检测到敏感环境变量（如API密钥）。请选择是否在导出文件中包含这些信息。
                  </p>
                </div>
              </div>
            </div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeSecret}
                onChange={(e) => setIncludeSecret(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm">包含敏感环境变量（请确保在安全环境中使用）</span>
            </label>
          </div>
        )}

        <div className="flex justify-end space-x-4">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
          >
            取消
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            确认导出
          </button>
        </div>
      </div>
    </div>
  );
};

export default BatchExportModal; 