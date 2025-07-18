import React, { useState } from 'react';
import { EnvironmentVariable } from '../types';

interface ExportConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (includeSecret: boolean) => void;
  environmentVariables: EnvironmentVariable[];
}

const ExportConfirmModal: React.FC<ExportConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  environmentVariables,
}) => {
  const [includeSecret, setIncludeSecret] = useState(false);

  const secretVariables = environmentVariables.filter(env => env.value_type === 'secret');

  const handleConfirm = () => {
    onConfirm(includeSecret);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">导出工作流 DSL</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        {secretVariables.length > 0 && (
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-3">
              检测到以下环境变量包含敏感信息：
            </p>
            <div className="bg-gray-50 rounded border p-3">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b">
                    <th className="text-left pb-1">名称</th>
                    <th className="text-left pb-1">值</th>
                  </tr>
                </thead>
                <tbody>
                  {secretVariables.map((env) => (
                    <tr key={env.name}>
                      <td className="py-1 pr-2 font-medium">{env.name}</td>
                      <td className="py-1 text-gray-600">{env.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div className="flex items-center mb-4">
          <input
            type="checkbox"
            id="includeSecret"
            checked={includeSecret}
            onChange={(e) => setIncludeSecret(e.target.checked)}
            className="mr-2"
          />
          <label htmlFor="includeSecret" className="text-sm">
            导出时包含敏感信息
          </label>
        </div>

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {includeSecret ? '导出包含敏感信息的 DSL' : '导出 DSL'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportConfirmModal; 