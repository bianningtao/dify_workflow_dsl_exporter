import React from 'react';

interface AppTypeTagProps {
  appMode: string;
  className?: string;
}

const AppTypeTag: React.FC<AppTypeTagProps> = ({ appMode, className = "" }) => {
  // 获取应用类型的配置信息
  const getAppTypeConfig = (mode: string) => {
    switch (mode) {
      case 'workflow':
        return {
          label: 'Workflow',
          icon: '⚡',
          bgColor: 'bg-purple-100',
          textColor: 'text-purple-800',
          borderColor: 'border-purple-200',
          description: '复杂任务自动化流程'
        };
      case 'advanced-chat':
        return {
          label: 'Chatflow',
          icon: '💬',
          bgColor: 'bg-blue-100',
          textColor: 'text-blue-800',
          borderColor: 'border-blue-200',
          description: '支持记忆的多轮对话'
        };
      case 'agent-chat':
        return {
          label: 'Agent',
          icon: '🤖',
          bgColor: 'bg-green-100',
          textColor: 'text-green-800',
          borderColor: 'border-green-200',
          description: '具备推理与工具调用的智能助手'
        };
      case 'completion':
        return {
          label: '文本生成',
          icon: '📝',
          bgColor: 'bg-orange-100',
          textColor: 'text-orange-800',
          borderColor: 'border-orange-200',
          description: '单次文本输入输出'
        };
      case 'chat':
        return {
          label: '聊天助手',
          icon: '💭',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
          borderColor: 'border-gray-200',
          description: '基础对话应用'
        };
      default:
        return {
          label: '未知类型',
          icon: '❓',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-600',
          borderColor: 'border-gray-200',
          description: '未识别的应用类型'
        };
    }
  };

  const config = getAppTypeConfig(appMode);

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${config.bgColor} ${config.textColor} ${config.borderColor} ${className}`}
      title={config.description}
    >
      <span className="mr-1" aria-label="类型图标">{config.icon}</span>
      {config.label}
    </span>
  );
};

export default AppTypeTag; 