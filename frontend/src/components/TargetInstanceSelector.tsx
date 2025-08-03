import React, { useEffect, useState } from 'react';
import { DifyInstance } from '../types';
import { ApiService } from '../services/api';

interface TargetInstanceSelectorProps {
  selectedInstanceId: string;
  onInstanceChange: (instanceId: string) => void;
  className?: string;
  disabled?: boolean;
  showConnectionStatus?: boolean;
  autoTestConnection?: boolean;
}

interface InstanceWithStatus extends DifyInstance {
  connectionStatus?: 'connected' | 'connecting' | 'failed' | 'unknown';
}

const TargetInstanceSelector: React.FC<TargetInstanceSelectorProps> = ({
  selectedInstanceId,
  onInstanceChange,
  className = '',
  disabled = false,
  showConnectionStatus = true,
  autoTestConnection = false
}) => {
  const [instances, setInstances] = useState<InstanceWithStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testingInstances, setTestingInstances] = useState<Set<string>>(new Set());
  const [selectedInstanceDetails, setSelectedInstanceDetails] = useState<InstanceWithStatus | null>(null);

  useEffect(() => {
    loadInstances();
  }, []);

  const loadInstances = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await ApiService.getTargetInstances();
      const instanceList = response.instances.map(instance => ({
        ...instance,
        connectionStatus: 'unknown' as const
      }));
      
      setInstances(instanceList);
      
      // 如果启用了自动连接测试，测试所有实例的连接
      if (autoTestConnection && showConnectionStatus) {
        testAllConnections(instanceList);
      }
      
      // 如果有选中的实例，更新其详情
      if (selectedInstanceId) {
        const selectedInstance = instanceList.find(i => i.id === selectedInstanceId);
        if (selectedInstance) {
          setSelectedInstanceDetails(selectedInstance);
          // 注意：这里不自动测试连接，等用户主动选择时再测试
        }
      }
      
    } catch (err) {
      console.error('加载目标实例失败:', err);
      setError(err instanceof Error ? err.message : '加载目标实例失败');
    } finally {
      setLoading(false);
    }
  };

  const testAllConnections = async (instanceList: InstanceWithStatus[]) => {
    const newTestingInstances = new Set<string>();
    
    for (const instance of instanceList) {
      newTestingInstances.add(instance.id);
    }
    
    setTestingInstances(newTestingInstances);
    
    // 并行测试所有实例的连接
    const testPromises = instanceList.map(async (instance) => {
      try {
        const result = await ApiService.testTargetInstance(instance.id);
        return {
          instanceId: instance.id,
          status: result.status as InstanceWithStatus['connectionStatus']
        };
      } catch (err) {
        console.error(`测试实例 ${instance.id} 连接失败:`, err);
        return {
          instanceId: instance.id,
          status: 'failed' as const
        };
      }
    });

    const results = await Promise.all(testPromises);
    
    setInstances(prev => prev.map(instance => {
      const result = results.find(r => r.instanceId === instance.id);
      return {
        ...instance,
        connectionStatus: result?.status || 'unknown'
      };
    }));
    
    setTestingInstances(new Set());
  };

  const testInstanceConnection = async (instanceId: string) => {
    setTestingInstances(prev => new Set(prev).add(instanceId));
    
    try {
      const result = await ApiService.testTargetInstance(instanceId);
      const status = result.status as InstanceWithStatus['connectionStatus'];
      
      // 更新实例状态
      setInstances(prev => prev.map(instance => 
        instance.id === instanceId 
          ? { ...instance, connectionStatus: status }
          : instance
      ));
      
      // 更新选中实例详情
      if (selectedInstanceDetails && selectedInstanceDetails.id === instanceId) {
        setSelectedInstanceDetails(prev => prev ? { ...prev, connectionStatus: status } : null);
      }
      
    } catch (err) {
      console.error(`测试实例 ${instanceId} 连接失败:`, err);
      const status = 'failed' as const;
      
      setInstances(prev => prev.map(instance => 
        instance.id === instanceId 
          ? { ...instance, connectionStatus: status }
          : instance
      ));
      
      if (selectedInstanceDetails && selectedInstanceDetails.id === instanceId) {
        setSelectedInstanceDetails(prev => prev ? { ...prev, connectionStatus: status } : null);
      }
    } finally {
      setTestingInstances(prev => {
        const newSet = new Set(prev);
        newSet.delete(instanceId);
        return newSet;
      });
    }
  };

  const handleInstanceChange = (instanceId: string) => {
    onInstanceChange(instanceId);
    
    if (!instanceId) {
      setSelectedInstanceDetails(null);
      return;
    }
    
    // 更新选中实例详情
    const selectedInstance = instances.find(i => i.id === instanceId);
    if (selectedInstance) {
      // 重置连接状态为unknown，等待测试
      const instanceWithUnknownStatus = { ...selectedInstance, connectionStatus: 'unknown' as const };
      setSelectedInstanceDetails(instanceWithUnknownStatus);
      
      // 自动进行连接测试（用户主动选择时）
      if (showConnectionStatus && !autoTestConnection) {
        testInstanceConnection(instanceId);
      }
    }
  };

  const getConnectionStatusIcon = (status: InstanceWithStatus['connectionStatus'], isLoading: boolean) => {
    if (isLoading) {
      return <span className="text-yellow-500 animate-spin">⟳</span>;
    }
    
    switch (status) {
      case 'connected':
        return <span className="text-green-500">●</span>;
      case 'failed':
      case 'authentication_failed':
      case 'connection_failed':
      case 'timeout':
        return <span className="text-red-500">●</span>;
      default:
        return <span className="text-gray-400">●</span>;
    }
  };

  const getConnectionStatusText = (status: InstanceWithStatus['connectionStatus']) => {
    switch (status) {
      case 'connected':
        return '已连接';
      case 'failed':
        return '连接失败';
      case 'authentication_failed':
        return '认证失败';
      case 'connection_failed':
        return '无法连接';
      case 'timeout':
        return '连接超时';
      default:
        return '未知状态';
    }
  };

  if (loading) {
    return (
      <div className={`${className}`}>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          目标Dify实例
        </label>
        <div className="animate-pulse bg-gray-200 h-10 rounded-md"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          目标Dify实例
        </label>
        <div className="border border-red-300 rounded-md p-3 bg-red-50">
          <div className="flex items-center">
            <span className="text-red-400 mr-2">⚠</span>
            <span className="text-red-700 text-sm">{error}</span>
          </div>
          <button
            onClick={loadInstances}
            className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  if (instances.length === 0) {
    return (
      <div className={`${className}`}>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          目标Dify实例
        </label>
        <div className="border border-yellow-300 rounded-md p-3 bg-yellow-50">
          <span className="text-yellow-700 text-sm">
            未配置目标实例，请在配置文件中添加target_instances配置
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        目标Dify实例
      </label>
      <select
        value={selectedInstanceId}
        onChange={(e) => handleInstanceChange(e.target.value)}
        disabled={disabled}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        <option value="">请选择目标实例</option>
        {instances.map((instance) => (
          <option key={instance.id} value={instance.id}>
            {instance.name} {instance.is_default ? '(默认)' : ''}
          </option>
        ))}
      </select>
      
      {showConnectionStatus && selectedInstanceDetails && (
        <div className="mt-3 p-3 bg-gray-50 rounded-md border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">选中实例详情</span>
            <button
              onClick={() => testInstanceConnection(selectedInstanceDetails.id)}
              disabled={testingInstances.has(selectedInstanceDetails.id)}
              className="text-xs text-blue-600 hover:text-blue-800 underline disabled:opacity-50"
            >
              {testingInstances.has(selectedInstanceDetails.id) ? '测试中...' : '重新测试连接'}
            </button>
          </div>
          
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">实例名称:</span>
              <span className="font-medium">{selectedInstanceDetails.name}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-600">实例地址:</span>
              <span className="text-gray-800 break-all">{selectedInstanceDetails.url}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-600">认证方式:</span>
              <span className="text-gray-800">{selectedInstanceDetails.auth_type}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-600">连接状态:</span>
              <div className="flex items-center space-x-1">
                {getConnectionStatusIcon(
                  selectedInstanceDetails.connectionStatus, 
                  testingInstances.has(selectedInstanceDetails.id)
                )}
                <span className={`text-xs ${
                  selectedInstanceDetails.connectionStatus === 'connected' 
                    ? 'text-green-600' 
                    : selectedInstanceDetails.connectionStatus === 'failed' 
                    ? 'text-red-600' 
                    : 'text-gray-500'
                }`}>
                  {testingInstances.has(selectedInstanceDetails.id) 
                    ? '测试中...' 
                    : getConnectionStatusText(selectedInstanceDetails.connectionStatus)
                  }
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="mt-2">
        <button
          onClick={loadInstances}
          disabled={loading}
          className="text-xs text-blue-600 hover:text-blue-800 underline disabled:opacity-50"
        >
          {loading ? '刷新中...' : '刷新实例列表'}
        </button>
      </div>
    </div>
  );
};

export default TargetInstanceSelector;