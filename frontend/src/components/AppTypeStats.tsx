import React from 'react';
import AppTypeTag from './AppTypeTag';

interface AppTypeStatsProps {
  stats: Record<string, number>;
  total: number;
  className?: string;
}

const AppTypeStats: React.FC<AppTypeStatsProps> = ({ stats, total, className = "" }) => {
  // 获取类型配置
  const getTypeConfig = (mode: string) => {
    switch (mode) {
      case 'workflow':
        return { label: 'Workflow', icon: '⚡' };
      case 'advanced-chat':
        return { label: 'Chatflow', icon: '💬' };
      case 'agent-chat':
        return { label: 'Agent', icon: '🤖' };
      case 'completion':
        return { label: '文本生成', icon: '📝' };
      case 'chat':
        return { label: '聊天助手', icon: '💭' };
      default:
        return { label: mode, icon: '❓' };
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-medium text-gray-900">应用类型统计</h3>
        <span className="text-sm text-gray-500">共 {total} 个应用</span>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {Object.entries(stats).map(([mode, count]) => {
          const config = getTypeConfig(mode);
          const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
          
          return (
            <div key={mode} className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="flex justify-center mb-2">
                <AppTypeTag appMode={mode} className="text-xs" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{count}</div>
              <div className="text-xs text-gray-500">{percentage}%</div>
            </div>
          );
        })}
      </div>
      
      {total === 0 && (
        <div className="text-center py-4 text-gray-500 text-sm">
          暂无应用数据
        </div>
      )}
    </div>
  );
};

export default AppTypeStats; 