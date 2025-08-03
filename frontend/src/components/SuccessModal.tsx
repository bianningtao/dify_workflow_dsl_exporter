import React from 'react';

interface SuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  message: string;
  appId?: string;
  statistics?: {
    successCount: number;
    totalCount: number;
    failedCount: number;
  };
}

const SuccessModal: React.FC<SuccessModalProps> = ({
  isOpen,
  onClose,
  title,
  message,
  appId,
  statistics
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        {/* 成功图标区域 */}
        <div className="bg-gradient-to-r from-green-400 to-emerald-500 p-6 text-white text-center">
          <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg 
              className="w-8 h-8 text-white" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={3} 
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h3 className="text-xl font-bold mb-2">{title}</h3>
          <p className="text-green-100">{message}</p>
        </div>

        {/* 详细信息区域 */}
        <div className="p-6 space-y-4">
          {/* 单个导入信息 */}
          {appId && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-600">应用ID</span>
                <div className="flex items-center space-x-2">
                  <code className="text-xs bg-gray-200 px-2 py-1 rounded font-mono">
                    {appId}
                  </code>
                  <button
                    onClick={() => navigator.clipboard.writeText(appId)}
                    className="text-gray-500 hover:text-gray-700 transition-colors"
                    title="复制应用ID"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 批量导入统计 */}
          {statistics && (
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-green-600">{statistics.successCount}</div>
                <div className="text-xs text-green-600">成功</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-blue-600">{statistics.totalCount}</div>
                <div className="text-xs text-blue-600">总计</div>
              </div>
              <div className="bg-red-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-red-600">{statistics.failedCount}</div>
                <div className="text-xs text-red-600">失败</div>
              </div>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
            >
              关闭
            </button>
            <button
              onClick={() => {
                window.location.reload();
              }}
              className="px-6 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all duration-200 font-medium shadow-lg"
            >
              刷新页面
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuccessModal;