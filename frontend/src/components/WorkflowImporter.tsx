import React, { useState, useRef, useCallback } from 'react';
import { WorkflowImportRequest, WorkflowImportResponse } from '../types';
import { ApiService } from '../services/api';
import TargetInstanceSelector from './TargetInstanceSelector';
import SuccessModal from './SuccessModal';

interface WorkflowImporterProps {
  onImportSuccess?: (result: WorkflowImportResponse) => void;
  onClose?: () => void;
  className?: string;
}

type ImportMode = 'file' | 'url';

const WorkflowImporter: React.FC<WorkflowImporterProps> = ({
  onImportSuccess,
  onClose,
  className = ''
}) => {
  const [mode, setMode] = useState<ImportMode>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [yamlUrl, setYamlUrl] = useState('');
  const [yamlContent, setYamlContent] = useState('');
  const [targetInstanceId, setTargetInstanceId] = useState(''); // 确保初始为空
  const [appName, setAppName] = useState('');
  const [appDescription, setAppDescription] = useState('');
  const [appIcon, setAppIcon] = useState('🤖');
  const [appIconBackground, setAppIconBackground] = useState('#FFEAD5');
  const [overwriteAppId, setOverwriteAppId] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [pendingImport, setPendingImport] = useState<WorkflowImportResponse | null>(null);
  
  // 成功弹窗状态
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successData, setSuccessData] = useState<{
    title: string;
    message: string;
    appId?: string;
  } | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback(async (file: File) => {
    setSelectedFile(file);
    setError(null);
    setValidationResult(null);
    
    if (file) {
      try {
        const content = await file.text();
        setYamlContent(content);
        
        // 验证文件格式
        const validation = await ApiService.validateWorkflowFile(content);
        setValidationResult(validation);
        
        if (validation.valid && validation.app_info) {
          setAppName(validation.app_info.name || '');
          setAppDescription(validation.app_info.description || '');
          setAppIcon(validation.app_info.icon || '🤖');
          setAppIconBackground(validation.app_info.icon_background || '#FFEAD5');
        }
        
      } catch (err) {
        setError(err instanceof Error ? err.message : '文件读取失败');
      }
    }
  }, []);

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const yamlFile = files.find(file => 
      file.name.endsWith('.yaml') || file.name.endsWith('.yml')
    );
    
    if (yamlFile) {
      handleFileSelect(yamlFile);
    } else {
      setError('请选择YAML格式的工作流文件');
    }
  }, [handleFileSelect]);

  const handleUrlValidation = async (url: string) => {
    if (!url) {
      setValidationResult(null);
      return;
    }
    
    try {
      setError(null);
      // 这里可以添加URL验证逻辑
      // 暂时只做基本的URL格式检查
      new URL(url);
    } catch (err) {
      setError('请输入有效的URL地址');
    }
  };

  const handleImport = async () => {
    if (!targetInstanceId) {
      setError('请选择目标Dify实例');
      return;
    }
    
    if (mode === 'file' && !selectedFile) {
      setError('请选择要导入的工作流文件');
      return;
    }
    
    if (mode === 'url' && !yamlUrl) {
      setError('请输入YAML文件的URL地址');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      setPendingImport(null);
      
      const request: WorkflowImportRequest = {
        mode: mode === 'file' ? 'yaml-content' : 'yaml-url',
        target_instance_id: targetInstanceId,
        name: appName || undefined,
        description: appDescription || undefined,
        icon_type: 'emoji',
        icon: appIcon || undefined,
        icon_background: appIconBackground || undefined,
        app_id: overwriteAppId || undefined
      };
      
      if (mode === 'file') {
        request.yaml_content = yamlContent;
      } else {
        request.yaml_url = yamlUrl;
      }
      
      const result = await ApiService.importWorkflow(request);
      
      if (result.status === 'pending') {
        setPendingImport(result);
        setSuccess('导入需要确认，请检查版本兼容性信息');
      } else if (result.status === 'completed') {
        // 显示优雅的成功弹窗
        setSuccessData({
          title: '工作流导入成功！',
          message: '您的工作流已成功导入到目标实例',
          appId: result.app_id
        });
        setShowSuccessModal(true);
        onImportSuccess?.(result);
      } else if (result.status === 'completed-with-warnings') {
        // 显示带警告的成功弹窗
        setSuccessData({
          title: '工作流导入成功！',
          message: '您的工作流已成功导入，但存在一些警告信息',
          appId: result.app_id
        });
        setShowSuccessModal(true);
        onImportSuccess?.(result);
      } else {
        setError(result.error || '导入失败');
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '导入失败');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!pendingImport || !targetInstanceId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const result = await ApiService.confirmImport(pendingImport.import_id, targetInstanceId);
      
      if (result.status === 'completed' || result.status === 'completed-with-warnings') {
        // 显示优雅的成功弹窗
        setSuccessData({
          title: '导入确认成功！',
          message: '您的工作流导入已确认并成功完成',
          appId: result.app_id
        });
        setShowSuccessModal(true);
        setPendingImport(null);
        onImportSuccess?.(result);
      } else {
        setError(result.error || '确认导入失败');
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '确认导入失败');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setSelectedFile(null);
    setYamlUrl('');
    setYamlContent('');
    setAppName('');
    setAppDescription('');
    setAppIcon('🤖');
    setAppIconBackground('#FFEAD5');
    setOverwriteAppId('');
    setError(null);
    setSuccess(null);
    setValidationResult(null);
    setPendingImport(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className={`w-full p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">工作流导入</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            ×
          </button>
        )}
      </div>

      {/* 目标实例选择 */}
      <TargetInstanceSelector
        selectedInstanceId={targetInstanceId}
        onInstanceChange={setTargetInstanceId}
        className="mb-6"
        disabled={loading}
        showConnectionStatus={true}
        autoTestConnection={false}
      />

      {/* 导入模式选择 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          导入方式
        </label>
        <div className="flex space-x-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="import-mode"
              value="file"
              checked={mode === 'file'}
              onChange={(e) => {
                setMode(e.target.value as ImportMode);
                setError(null);
              }}
              disabled={loading}
              className="mr-2"
            />
            文件上传
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="import-mode"
              value="url"
              checked={mode === 'url'}
              onChange={(e) => {
                setMode(e.target.value as ImportMode);
                setError(null);
              }}
              disabled={loading}
              className="mr-2"
            />
            URL导入
          </label>
        </div>
      </div>

      {/* 文件上传区域 */}
      {mode === 'file' && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            选择工作流文件
          </label>
          <div
            onDrop={handleFileDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".yaml,.yml"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileSelect(file);
              }}
              disabled={loading}
              className="hidden"
            />
            {selectedFile ? (
              <div className="space-y-2">
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-green-600">✓</span>
                  <span className="font-medium">{selectedFile.name}</span>
                </div>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  选择其他文件
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-gray-400 text-4xl">📁</div>
                <div>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    点击选择文件
                  </button>
                  <span className="text-gray-500"> 或拖拽文件到此处</span>
                </div>
                <div className="text-xs text-gray-400">
                  支持 .yaml 和 .yml 格式
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* URL输入区域 */}
      {mode === 'url' && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            YAML文件URL
          </label>
          <input
            type="url"
            value={yamlUrl}
            onChange={(e) => {
              setYamlUrl(e.target.value);
              handleUrlValidation(e.target.value);
            }}
            disabled={loading}
            placeholder="https://example.com/workflow.yaml"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
      )}

      {/* 文件验证结果 */}
      {validationResult && (
        <div className={`mb-6 p-4 rounded-md ${
          validationResult.valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          {validationResult.valid ? (
            <div className="space-y-2">
              <div className="flex items-center text-green-700">
                <span className="mr-2">✓</span>
                <span className="font-medium">文件格式验证通过</span>
              </div>
              {validationResult.app_info && (
                <div className="text-sm text-green-600 grid grid-cols-2 gap-2">
                  <div><strong>应用名称:</strong> {validationResult.app_info.name}</div>
                  <div><strong>应用模式:</strong> {validationResult.app_info.mode}</div>
                  <div><strong>描述:</strong> {validationResult.app_info.description || '无'}</div>
                  <div><strong>版本:</strong> {validationResult.app_info.version}</div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center text-red-700">
              <span className="mr-2">✗</span>
              <span>{validationResult.error}</span>
            </div>
          )}
        </div>
      )}

      {/* 应用信息配置 */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            应用名称 (可选)
          </label>
          <input
            type="text"
            value={appName}
            onChange={(e) => setAppName(e.target.value)}
            disabled={loading}
            placeholder="留空使用文件中的名称"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            覆盖应用ID (可选)
          </label>
          <input
            type="text"
            value={overwriteAppId}
            onChange={(e) => setOverwriteAppId(e.target.value)}
            disabled={loading}
            placeholder="留空创建新应用"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
        
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            应用描述 (可选)
          </label>
          <textarea
            value={appDescription}
            onChange={(e) => setAppDescription(e.target.value)}
            disabled={loading}
            placeholder="留空使用文件中的描述"
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            应用图标
          </label>
          <input
            type="text"
            value={appIcon}
            onChange={(e) => setAppIcon(e.target.value)}
            disabled={loading}
            placeholder="🤖"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            图标背景色
          </label>
          <input
            type="color"
            value={appIconBackground}
            onChange={(e) => setAppIconBackground(e.target.value)}
            disabled={loading}
            className="w-full h-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
      </div>

      {/* 错误和成功消息 */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center text-red-700">
            <span className="mr-2">⚠</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-center text-green-700">
            <span className="mr-2">✓</span>
            <span>{success}</span>
          </div>
        </div>
      )}

      {/* 待确认的导入信息 */}
      {pendingImport && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <div className="space-y-2">
            <div className="font-medium text-yellow-800">需要确认版本兼容性</div>
            <div className="text-sm text-yellow-700 space-y-1">
              <div>导入版本: {pendingImport.imported_dsl_version}</div>
              <div>系统版本: {pendingImport.current_dsl_version}</div>
              <div>应用模式: {pendingImport.app_mode}</div>
            </div>
            <div className="flex space-x-2 pt-2">
              <button
                onClick={handleConfirmImport}
                disabled={loading}
                className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '确认中...' : '确认导入'}
              </button>
              <button
                onClick={() => setPendingImport(null)}
                disabled={loading}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex justify-between items-center">
        <button
          onClick={reset}
          disabled={loading}
          className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          重置
        </button>
        
        <div className="flex space-x-3">
          {onClose && (
            <button
              onClick={onClose}
              disabled={loading}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              取消
            </button>
          )}
          
          <button
            onClick={handleImport}
            disabled={loading || !targetInstanceId || (mode === 'file' && !selectedFile) || (mode === 'url' && !yamlUrl)}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading && <span className="animate-spin">⟳</span>}
            <span>{loading ? '导入中...' : '开始导入'}</span>
          </button>
        </div>
      </div>

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
      />
    </div>
  );
};

export default WorkflowImporter;