import React from 'react';

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  type?: 'warning' | 'error' | 'info' | 'success';
  confirmText?: string;
  onConfirm: () => void;
  showCancel?: boolean;
  cancelText?: string;
  onCancel?: () => void;
}

const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  title,
  message,
  type = 'warning',
  confirmText = '确定',
  onConfirm,
  showCancel = false,
  cancelText = '取消',
  onCancel,
}) => {
  // console.log('ConfirmModal 渲染:', { isOpen, title, message, type });
  
  if (!isOpen) {
    // console.log('ConfirmModal: isOpen 为 false，不显示');
    return null;
  }
  
  // console.log('ConfirmModal: 正在显示弹窗');

  // 根据类型选择图标和颜色
  const getTypeConfig = () => {
    switch (type) {
      case 'warning':
        return {
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          iconColor: 'text-yellow-600',
          icon: (
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          ),
        };
      case 'error':
        return {
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          iconColor: 'text-red-600',
          icon: (
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
        };
      case 'success':
        return {
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          iconColor: 'text-green-600',
          icon: (
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
        };
      case 'info':
      default:
        return {
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          iconColor: 'text-blue-600',
          icon: (
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
        };
    }
  };

  const config = getTypeConfig();

  return (
    <div className="fixed inset-0 z-[9999] overflow-y-auto">
      {/* 背景遮罩 */}
      <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>

      {/* 弹窗内容 */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative transform overflow-hidden rounded-2xl bg-white shadow-2xl transition-all max-w-md w-full">
          {/* 顶部装饰条 */}
          <div className={`h-2 ${config.bgColor}`}></div>

          <div className="p-6">
            {/* 图标 */}
            <div className="flex justify-center mb-4">
              <div className={`${config.iconColor}`}>
                {config.icon}
              </div>
            </div>

            {/* 标题 */}
            <h3 className="text-2xl font-bold text-gray-900 text-center mb-4">
              {title}
            </h3>

            {/* 消息内容 */}
            <div className={`${config.bgColor} ${config.borderColor} border rounded-lg p-4 mb-6`}>
              <p className="text-gray-700 text-center whitespace-pre-line leading-relaxed">
                {message}
              </p>
            </div>

            {/* 按钮 */}
            <div className={`flex ${showCancel ? 'justify-between space-x-3' : 'justify-center'}`}>
              {showCancel && onCancel && (
                <button
                  onClick={onCancel}
                  className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  {cancelText}
                </button>
              )}
              <button
                onClick={onConfirm}
                className={`${showCancel ? 'flex-1' : 'w-full'} px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform`}
              >
                {confirmText}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;

