import React, { useState, useEffect } from 'react';
import { SystemConfig, ApiConfig, DatabaseConfig, TargetInstance, AuthConfig } from '../types';
import { ApiService } from '../services/api';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveSuccess?: () => void; // 保存成功后的回调
}

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, onSaveSuccess }) => {
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'general' | 'api' | 'database' | 'instances'>('general');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; instanceId?: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadConfig();
    }
  }, [isOpen]);

  const loadConfig = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await ApiService.getConfig();
      setConfig(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;
    
    setSaving(true);
    setError(null);
    setSuccessMessage(null);
    
    try {
      // 先验证配置
      const validationResult = await ApiService.validateConfig(config);
      if (!validationResult.valid) {
        setError(validationResult.message || '配置验证失败');
        return;
      }

      // 保存配置
      const result = await ApiService.updateConfig(config);
      if (result.success) {
        setSuccessMessage('配置保存成功');
        
        // 调用成功回调并关闭弹窗
        if (onSaveSuccess) {
          onSaveSuccess();
        }
        
        // 延迟关闭以显示成功消息
        setTimeout(() => {
          setSuccessMessage(null);
          onClose();
        }, 1000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存配置失败');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm('确定要重置为默认配置吗？这将覆盖当前所有设置。')) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    
    try {
      const result = await ApiService.resetConfig();
      if (result.success) {
        setSuccessMessage('配置已重置为默认值');
        await loadConfig();
        setTimeout(() => {
          setSuccessMessage(null);
        }, 3000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '重置配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    if (!config) return;
    
    setTesting(true);
    setTestResult(null);
    setError(null);
    
    try {
      const result = await ApiService.testConnection(config);
      setTestResult({
        success: result.success,
        message: result.message
      });
      
      // 3秒后自动清除测试结果
      setTimeout(() => {
        setTestResult(null);
      }, 5000);
    } catch (err: any) {
      // 从错误响应中提取友好的错误消息
      const errorMessage = err.response?.data?.message || err.message || '测试连接失败';
      setTestResult({
        success: false,
        message: errorMessage
      });
    } finally {
      setTesting(false);
    }
  };

  const handleTestTargetInstance = async (instance: TargetInstance) => {
    setTesting(true);
    setTestResult(null);
    setError(null);
    
    try {
      // 构造测试配置
      const testConfig = {
        data_source: 'target_instance',
        target_instance: instance
      };
      
      const result = await ApiService.testConnection(testConfig as any);
      setTestResult({
        success: result.success,
        message: result.message,
        instanceId: instance.id
      });
      
      // 5秒后自动清除测试结果
      setTimeout(() => {
        setTestResult(null);
      }, 5000);
    } catch (err: any) {
      // 从错误响应中提取友好的错误消息
      const errorMessage = err.response?.data?.message || err.message || '测试连接失败';
      setTestResult({
        success: false,
        message: errorMessage,
        instanceId: instance.id
      });
    } finally {
      setTesting(false);
    }
  };

  const updateConfig = (path: string, value: any) => {
    if (!config) return;
    
    const keys = path.split('.');
    const newConfig = JSON.parse(JSON.stringify(config));
    let current: any = newConfig;
    
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
    setConfig(newConfig);
  };

  const addTargetInstance = () => {
    if (!config) return;
    
    const newInstance: TargetInstance = {
      id: `instance-${Date.now()}`,
      name: '新实例',
      url: 'http://localhost',
      auth: {
        type: 'bearer',
        token: ''
      },
      is_default: false
    };
    
    const newConfig = { ...config };
    if (!newConfig.target_instances) {
      newConfig.target_instances = [];
    }
    newConfig.target_instances.push(newInstance);
    setConfig(newConfig);
  };

  const removeTargetInstance = (index: number) => {
    if (!config || !config.target_instances) return;
    
    const newConfig = { ...config };
    newConfig.target_instances = [...config.target_instances];
    newConfig.target_instances.splice(index, 1);
    setConfig(newConfig);
  };

  const updateTargetInstance = (index: number, field: string, value: any) => {
    if (!config || !config.target_instances) return;
    
    const newConfig = { ...config };
    newConfig.target_instances = [...config.target_instances];
    const instance = { ...newConfig.target_instances[index] };
    
    if (field.startsWith('auth.')) {
      const authField = field.substring(5);
      instance.auth = { ...instance.auth, [authField]: value };
    } else {
      (instance as any)[field] = value;
    }
    
    newConfig.target_instances[index] = instance;
    setConfig(newConfig);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">系统设置</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 px-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('general')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'general'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              通用设置
            </button>
            {config?.data_source === 'api' && (
              <button
                onClick={() => setActiveTab('api')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'api'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                API配置
              </button>
            )}
            {config?.data_source === 'database' && (
              <button
                onClick={() => setActiveTab('database')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'database'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                数据库配置
              </button>
            )}
            <button
              onClick={() => setActiveTab('instances')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'instances'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              目标实例
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : config ? (
            <>
              {/* Messages */}
              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  {error}
                </div>
              )}
              {successMessage && (
                <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
                  {successMessage}
                </div>
              )}

              {/* General Settings */}
              {activeTab === 'general' && (
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      数据源类型
                    </label>
                    <select
                      value={config.data_source}
                      onChange={(e) => {
                        updateConfig('data_source', e.target.value);
                        // 切换数据源时自动切换到对应标签页
                        if (e.target.value === 'api') {
                          setActiveTab('api');
                        } else if (e.target.value === 'database') {
                          setActiveTab('database');
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="api">API配置</option>
                      <option value="database">数据库配置</option>
                    </select>
                    <p className="mt-1 text-xs text-gray-500">
                      选择后将自动切换到对应的配置标签页
                    </p>
                  </div>

                  <div className="border-t pt-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">API端点配置</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      以下是系统内置的API端点，通常不需要修改。如果您的Dify实例使用了自定义端点路径，可以在这里修改：
                    </p>
                    <div className="space-y-3 max-h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-gray-50">
                      {config.api?.endpoints && Object.entries(config.api.endpoints).map(([key, value]) => (
                        <div key={key} className="flex items-start space-x-3">
                          <div className="flex-shrink-0 w-48">
                            <label className="text-xs font-medium text-gray-600">{key}:</label>
                          </div>
                          <input
                            type="text"
                            value={value}
                            onChange={(e) => updateConfig(`api.endpoints.${key}`, e.target.value)}
                            className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                      ))}
                    </div>
                  </div>

                  {config.cache && (
                    <>
                      <div className="border-t pt-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">缓存配置</h3>
                        <div className="space-y-4">
                          <div>
                            <label className="flex items-center">
                              <input
                                type="checkbox"
                                checked={config.cache.enabled}
                                onChange={(e) => updateConfig('cache.enabled', e.target.checked)}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                              />
                              <span className="ml-2 text-sm font-medium text-gray-700">启用缓存</span>
                            </label>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              缓存过期时间(秒)
                            </label>
                            <input
                              type="number"
                              value={config.cache.ttl}
                              onChange={(e) => updateConfig('cache.ttl', parseInt(e.target.value))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          </div>
                        </div>
                      </div>
                    </>
                  )}

                  {config.logging && (
                    <div className="border-t pt-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">日志配置</h3>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          日志级别
                        </label>
                        <select
                          value={config.logging.level}
                          onChange={(e) => updateConfig('logging.level', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="DEBUG">DEBUG</option>
                          <option value="INFO">INFO</option>
                          <option value="WARNING">WARNING</option>
                          <option value="ERROR">ERROR</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* API Settings */}
              {activeTab === 'api' && config.api && (
                <div className="space-y-6">
                  {/* 测试结果提示 */}
                  {testResult && (
                    <div className={`p-4 rounded-lg ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                      <div className="flex items-center">
                        {testResult.success ? (
                          <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                        <span className={testResult.success ? 'text-green-700' : 'text-red-700'}>
                          {testResult.message}
                        </span>
                      </div>
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      API基础URL
                    </label>
                    <input
                      type="text"
                      value={config.api.base_url}
                      onChange={(e) => updateConfig('api.base_url', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://dify.example.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      认证类型
                    </label>
                    <select
                      value={config.api.auth.type}
                      onChange={(e) => updateConfig('api.auth.type', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="bearer">Bearer Token</option>
                      <option value="basic">基本认证</option>
                      <option value="api_key">API Key</option>
                    </select>
                  </div>

                  {config.api.auth.type === 'bearer' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Bearer Token
                      </label>
                      <input
                        type="password"
                        value={config.api.auth.token || ''}
                        onChange={(e) => updateConfig('api.auth.token', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="输入您的Console API Token"
                      />
                    </div>
                  )}

                  {config.api.auth.type === 'basic' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          用户名
                        </label>
                        <input
                          type="text"
                          value={config.api.auth.username || ''}
                          onChange={(e) => updateConfig('api.auth.username', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          密码
                        </label>
                        <input
                          type="password"
                          value={config.api.auth.password || ''}
                          onChange={(e) => updateConfig('api.auth.password', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </>
                  )}

                  {config.api.auth.type === 'api_key' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          API Key
                        </label>
                        <input
                          type="password"
                          value={config.api.auth.api_key || ''}
                          onChange={(e) => updateConfig('api.auth.api_key', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          API Key Header名称
                        </label>
                        <input
                          type="text"
                          value={config.api.auth.api_key_header || 'X-API-Key'}
                          onChange={(e) => updateConfig('api.auth.api_key_header', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </>
                  )}

                  {/* 测试连接按钮 */}
                  <div className="border-t pt-6">
                    <button
                      onClick={handleTestConnection}
                      disabled={testing}
                      className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      {testing ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          测试连接中...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          测试API连接
                        </>
                      )}
                    </button>
                    <p className="mt-2 text-xs text-gray-500 text-center">
                      点击测试按钮验证API配置是否正确
                    </p>
                  </div>
                </div>
              )}

              {/* Database Settings */}
              {activeTab === 'database' && config.database && (
                <div className="space-y-6">
                  {/* 测试结果提示 */}
                  {testResult && (
                    <div className={`p-4 rounded-lg ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                      <div className="flex items-center">
                        {testResult.success ? (
                          <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                        <span className={testResult.success ? 'text-green-700' : 'text-red-700'}>
                          {testResult.message}
                        </span>
                      </div>
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      数据库类型
                    </label>
                    <select
                      value={config.database.type}
                      onChange={(e) => updateConfig('database.type', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="postgresql">PostgreSQL</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        主机地址
                      </label>
                      <input
                        type="text"
                        value={config.database.host}
                        onChange={(e) => updateConfig('database.host', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        端口
                      </label>
                      <input
                        type="number"
                        value={config.database.port}
                        onChange={(e) => updateConfig('database.port', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      数据库名
                    </label>
                    <input
                      type="text"
                      value={config.database.database}
                      onChange={(e) => updateConfig('database.database', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        用户名
                      </label>
                      <input
                        type="text"
                        value={config.database.username}
                        onChange={(e) => updateConfig('database.username', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        密码
                      </label>
                      <input
                        type="password"
                        value={config.database.password}
                        onChange={(e) => updateConfig('database.password', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>

                  {/* 测试连接按钮 */}
                  <div className="border-t pt-6">
                    <button
                      onClick={handleTestConnection}
                      disabled={testing}
                      className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      {testing ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          测试连接中...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                          </svg>
                          测试数据库连接
                        </>
                      )}
                    </button>
                    <p className="mt-2 text-xs text-gray-500 text-center">
                      点击测试按钮验证数据库配置是否正确
                    </p>
                  </div>
                </div>
              )}

              {/* Target Instances Settings */}
              {activeTab === 'instances' && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900">目标Dify实例</h3>
                    <button
                      onClick={addTargetInstance}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                    >
                      + 添加实例
                    </button>
                  </div>

                  {config.target_instances && config.target_instances.length > 0 ? (
                    <div className="space-y-4">
                      {config.target_instances.map((instance, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-4">
                          <div className="flex justify-between items-start">
                            <h4 className="font-medium text-gray-900">实例 {index + 1}</h4>
                            <button
                              onClick={() => removeTargetInstance(index)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              删除
                            </button>
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                实例ID
                              </label>
                              <input
                                type="text"
                                value={instance.id}
                                onChange={(e) => updateTargetInstance(index, 'id', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                实例名称
                              </label>
                              <input
                                type="text"
                                value={instance.name}
                                onChange={(e) => updateTargetInstance(index, 'name', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                              />
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              URL
                            </label>
                            <input
                              type="text"
                              value={instance.url}
                              onChange={(e) => updateTargetInstance(index, 'url', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              认证类型
                            </label>
                            <select
                              value={instance.auth.type}
                              onChange={(e) => updateTargetInstance(index, 'auth.type', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            >
                              <option value="bearer">Bearer Token</option>
                              <option value="basic">基本认证</option>
                              <option value="api_key">API Key</option>
                            </select>
                          </div>

                          {instance.auth.type === 'bearer' && (
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Token
                              </label>
                              <input
                                type="password"
                                value={instance.auth.token || ''}
                                onChange={(e) => updateTargetInstance(index, 'auth.token', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                              />
                            </div>
                          )}

                          {instance.auth.type === 'basic' && (
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  用户名
                                </label>
                                <input
                                  type="text"
                                  value={instance.auth.username || ''}
                                  onChange={(e) => updateTargetInstance(index, 'auth.username', e.target.value)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  密码
                                </label>
                                <input
                                  type="password"
                                  value={instance.auth.password || ''}
                                  onChange={(e) => updateTargetInstance(index, 'auth.password', e.target.value)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                />
                              </div>
                            </div>
                          )}

                          {instance.auth.type === 'api_key' && (
                            <>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  API Key
                                </label>
                                <input
                                  type="password"
                                  value={instance.auth.api_key || ''}
                                  onChange={(e) => updateTargetInstance(index, 'auth.api_key', e.target.value)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  API Key Header
                                </label>
                                <input
                                  type="text"
                                  value={instance.auth.api_key_header || 'X-API-Key'}
                                  onChange={(e) => updateTargetInstance(index, 'auth.api_key_header', e.target.value)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                />
                              </div>
                            </>
                          )}

                          <div>
                            <label className="flex items-center">
                              <input
                                type="checkbox"
                                checked={instance.is_default || false}
                                onChange={(e) => updateTargetInstance(index, 'is_default', e.target.checked)}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                              />
                              <span className="ml-2 text-sm font-medium text-gray-700">设为默认实例</span>
                            </label>
                          </div>

                          {/* 测试连接按钮 */}
                          <div>
                            <button
                              onClick={() => handleTestTargetInstance(instance)}
                              disabled={testing}
                              className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                            >
                              {testing ? (
                                <>
                                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                  </svg>
                                  测试中...
                                </>
                              ) : (
                                '测试连接'
                              )}
                            </button>
                            {testResult && testResult.instanceId === instance.id && (
                              <div className={`mt-2 text-sm ${testResult.success ? 'text-green-600' : 'text-red-600'}`}>
                                {testResult.message}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      暂无目标实例配置，点击"添加实例"开始配置
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 text-gray-500">
              加载配置失败
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-6 flex justify-between">
          <button
            onClick={handleReset}
            disabled={saving || loading}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            重置为默认值
          </button>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              disabled={saving}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              取消
            </button>
            <button
              onClick={handleSave}
              disabled={saving || loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {saving && (
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              )}
              {saving ? '保存中...' : '保存配置'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;

