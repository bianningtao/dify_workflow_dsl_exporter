import React, { useState, useRef, useCallback } from 'react';
import { BatchImportRequest, BatchImportResponse, WorkflowImportFile } from '../types';
import { ApiService } from '../services/api';
import TargetInstanceSelector from './TargetInstanceSelector';

interface BatchImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportSuccess?: (result: BatchImportResponse) => void;
}

interface FileWithValidation extends WorkflowImportFile {
  file: File;
  validation?: { valid: boolean; error?: string; app_info?: any };
  isValidating?: boolean;
}

const BatchImportModal: React.FC<BatchImportModalProps> = ({
  isOpen,
  onClose,
  onImportSuccess
}) => {
  const [files, setFiles] = useState<FileWithValidation[]>([]);
  const [targetInstanceId, setTargetInstanceId] = useState(''); // 确保初始为空
  const [importOptions, setImportOptions] = useState({
    overwrite_existing: false,
    ignore_errors: false,
    create_new_on_conflict: true
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<BatchImportResponse | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = async (file: File): Promise<{ valid: boolean; error?: string; app_info?: any }> => {
    try {
      const content = await file.text();
      return await ApiService.validateWorkflowFile(content);
    } catch (err) {
      return {
        valid: false,
        error: err instanceof Error ? err.message : '文件验证失败'
      };
    }
  };

  const handleFilesSelect = useCallback(async (selectedFiles: FileList) => {
    const yamlFiles = Array.from(selectedFiles).filter(file =>
      file.name.endsWith('.yaml') || file.name.endsWith('.yml')
    );

    if (yamlFiles.length === 0) {
      setError('请选择YAML格式的工作流文件');
      return;
    }

    setError(null);
    
    const newFiles: FileWithValidation[] = [];
    
    for (const file of yamlFiles) {
      try {
        const content = await file.text();
        const fileWithValidation: FileWithValidation = {
          file,
          filename: file.name,
          content,
          name: '',
          description: '',
          isValidating: true
        };
        newFiles.push(fileWithValidation);
      } catch (err) {
        console.error(`读取文件 ${file.name} 失败:`, err);
      }
    }
    
    setFiles(prev => [...prev, ...newFiles]);

    // 异步验证文件
    for (let i = 0; i < newFiles.length; i++) {
      const fileIndex = files.length + i;
      const validation = await validateFile(newFiles[i].file);
      
      setFiles(prev => prev.map((f, index) => {
        if (index === fileIndex) {
          return {
            ...f,
            isValidating: false,
            validation,
            name: validation.app_info?.name || f.filename.replace(/\.(yaml|yml)$/, ''),
            description: validation.app_info?.description || ''
          };
        }
        return f;
      }));
    }
  }, [files.length]);

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      handleFilesSelect(droppedFiles);
    }
  }, [handleFilesSelect]);

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const updateFileName = (index: number, name: string) => {
    setFiles(prev => prev.map((f, i) => i === index ? { ...f, name } : f));
  };

  const updateFileDescription = (index: number, description: string) => {
    setFiles(prev => prev.map((f, i) => i === index ? { ...f, description } : f));
  };

  const handleBatchImport = async () => {
    if (!targetInstanceId) {
      setError('请选择目标Dify实例');
      return;
    }

    if (files.length === 0) {
      setError('请至少选择一个工作流文件');
      return;
    }

    const validFiles = files.filter(f => f.validation?.valid);
    if (validFiles.length === 0) {
      setError('没有有效的工作流文件可以导入');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setImportResult(null);

      const request: BatchImportRequest = {
        target_instance_id: targetInstanceId,
        files: validFiles.map(f => ({
          filename: f.filename,
          content: f.content,
          name: f.name,
          description: f.description
        })),
        import_options: importOptions
      };

      const result = await ApiService.batchImportWorkflows(request);
      setImportResult(result);
      setIsCompleted(true);
      
      if (result.success_count > 0) {
        onImportSuccess?.(result);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : '批量导入失败');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFiles([]);
    setError(null);
    setImportResult(null);
    setIsCompleted(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">批量工作流导入</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 text-xl"
            >
              ×
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {!isCompleted ? (
            <div className="space-y-6">
              {/* 目标实例选择 */}
              <TargetInstanceSelector
                selectedInstanceId={targetInstanceId}
                onInstanceChange={setTargetInstanceId}
                disabled={loading}
                showConnectionStatus={true}
                autoTestConnection={false}
              />

              {/* 导入选项 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  导入选项
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={importOptions.overwrite_existing}
                      onChange={(e) => setImportOptions(prev => ({
                        ...prev,
                        overwrite_existing: e.target.checked
                      }))}
                      disabled={loading}
                      className="mr-2"
                    />
                    <span className="text-sm">覆盖同名应用</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={importOptions.ignore_errors}
                      onChange={(e) => setImportOptions(prev => ({
                        ...prev,
                        ignore_errors: e.target.checked
                      }))}
                      disabled={loading}
                      className="mr-2"
                    />
                    <span className="text-sm">忽略错误继续导入</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={importOptions.create_new_on_conflict}
                      onChange={(e) => setImportOptions(prev => ({
                        ...prev,
                        create_new_on_conflict: e.target.checked
                      }))}
                      disabled={loading}
                      className="mr-2"
                    />
                    <span className="text-sm">冲突时创建新应用</span>
                  </label>
                </div>
              </div>

              {/* 文件上传区域 */}
              <div>
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
                    multiple
                    onChange={(e) => {
                      if (e.target.files) {
                        handleFilesSelect(e.target.files);
                      }
                    }}
                    disabled={loading}
                    className="hidden"
                  />
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
                      支持选择多个 .yaml 和 .yml 文件
                    </div>
                  </div>
                </div>
              </div>

              {/* 文件列表 */}
              {files.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    待导入文件 ({files.length} 个)
                  </label>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className={`border rounded-lg p-3 ${
                          file.validation?.valid === false
                            ? 'border-red-300 bg-red-50'
                            : file.validation?.valid === true
                            ? 'border-green-300 bg-green-50'
                            : 'border-gray-300 bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 space-y-2">
                            <div className="flex items-center space-x-2">
                              <span className="font-medium text-sm">{file.filename}</span>
                              {file.isValidating && (
                                <span className="text-yellow-500 animate-spin text-xs">⟳</span>
                              )}
                              {file.validation?.valid === true && (
                                <span className="text-green-500 text-xs">✓ 有效</span>
                              )}
                              {file.validation?.valid === false && (
                                <span className="text-red-500 text-xs">✗ 无效</span>
                              )}
                            </div>
                            
                            {file.validation?.valid === false && (
                              <div className="text-xs text-red-600">
                                {file.validation.error}
                              </div>
                            )}
                            
                            {file.validation?.valid === true && (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                <div>
                                  <label className="block text-xs text-gray-500 mb-1">应用名称</label>
                                  <input
                                    type="text"
                                    value={file.name}
                                    onChange={(e) => updateFileName(index, e.target.value)}
                                    disabled={loading}
                                    className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
                                  />
                                </div>
                                <div className="md:col-span-1">
                                  <label className="block text-xs text-gray-500 mb-1">应用描述</label>
                                  <input
                                    type="text"
                                    value={file.description}
                                    onChange={(e) => updateFileDescription(index, e.target.value)}
                                    disabled={loading}
                                    className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
                                  />
                                </div>
                              </div>
                            )}
                          </div>
                          
                          <button
                            onClick={() => removeFile(index)}
                            disabled={loading}
                            className="ml-2 text-red-500 hover:text-red-700 disabled:opacity-50"
                          >
                            ✗
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 错误消息 */}
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <div className="flex items-center text-red-700">
                    <span className="mr-2">⚠</span>
                    <span>{error}</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* 导入结果 */
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900 mb-2">批量导入完成</h3>
                {importResult && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-blue-50 p-3 rounded-lg text-center">
                      <div className="text-2xl font-bold text-blue-600">{importResult.total_count}</div>
                      <div className="text-sm text-blue-600">总数</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg text-center">
                      <div className="text-2xl font-bold text-green-600">{importResult.success_count}</div>
                      <div className="text-sm text-green-600">成功</div>
                    </div>
                    <div className="bg-yellow-50 p-3 rounded-lg text-center">
                      <div className="text-2xl font-bold text-yellow-600">{importResult.warning_count}</div>
                      <div className="text-sm text-yellow-600">警告</div>
                    </div>
                    <div className="bg-red-50 p-3 rounded-lg text-center">
                      <div className="text-2xl font-bold text-red-600">{importResult.failed_count}</div>
                      <div className="text-sm text-red-600">失败</div>
                    </div>
                  </div>
                )}
              </div>

              {/* 详细结果 */}
              {importResult && (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {importResult.results.map((result, index) => (
                    <div
                      key={index}
                      className={`border rounded-lg p-3 ${
                        result.success
                          ? 'border-green-300 bg-green-50'
                          : 'border-red-300 bg-red-50'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-sm">{result.filename}</span>
                            {result.success ? (
                              <span className="text-green-500 text-xs">✓ 成功</span>
                            ) : (
                              <span className="text-red-500 text-xs">✗ 失败</span>
                            )}
                          </div>
                          
                          {result.app_name && (
                            <div className="text-xs text-gray-600">应用名称: {result.app_name}</div>
                          )}
                          
                          {result.status && (
                            <div className="text-xs text-gray-600">状态: {result.status}</div>
                          )}
                          
                          {result.error && (
                            <div className="text-xs text-red-600 mt-1">错误: {result.error}</div>
                          )}
                          
                          {result.warnings && result.warnings.length > 0 && (
                            <div className="text-xs text-yellow-600 mt-1">
                              警告: {result.warnings.join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="p-6 border-t bg-gray-50">
          <div className="flex justify-between items-center">
            {!isCompleted ? (
              <>
                <button
                  onClick={reset}
                  disabled={loading}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  重置
                </button>
                
                <div className="flex space-x-3">
                  <button
                    onClick={handleClose}
                    disabled={loading}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    取消
                  </button>
                  
                  <button
                    onClick={handleBatchImport}
                    disabled={loading || !targetInstanceId || files.length === 0 || files.every(f => f.validation?.valid === false)}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {loading && <span className="animate-spin">⟳</span>}
                    <span>{loading ? '导入中...' : '开始批量导入'}</span>
                  </button>
                </div>
              </>
            ) : (
              <div className="flex justify-end space-x-3 w-full">
                <button
                  onClick={reset}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  重新导入
                </button>
                
                <button
                  onClick={handleClose}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  完成
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BatchImportModal;