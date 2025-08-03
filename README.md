# Dify 工作流 DSL 导入导出工具

这是一个功能完整的 Dify 工作流 DSL 导入导出工具。该项目提供了完整的前后端解决方案，支持工作流配置的双向操作：既可以从 Dify 系统批量导出工作流 DSL 配置，也可以将 DSL 文件导入到指定的 Dify 实例中，包含现代化的 Web 界面和灵活的数据源配置。

## ✨ 功能特性

### 📤 导出功能
- 🚀 **批量导出**: 支持选择多个工作流进行批量导出
- 📦 **ZIP打包**: 自动将多个DSL文件打包成ZIP格式下载
- 📊 **进度显示**: 批量导出时显示实时进度和状态
- 📝 **单个导出**: 支持输入应用ID进行单个工作流导出

### 📥 导入功能
- 🎯 **单个导入**: 支持上传单个DSL文件到指定Dify实例
- 📦 **批量导入**: 支持批量选择多个DSL文件进行导入
- 🎯 **目标实例选择**: 支持配置和选择多个目标Dify实例
- ✅ **导入确认**: 智能解析DSL内容，提供导入预览和确认功能
- 🔄 **实时状态**: 显示导入进度和实时状态更新

### 🎨 界面与体验
- 🎨 **现代化界面**: 提供直观美观的 Web 界面
- 🔀 **双模式切换**: 支持导出/导入模式快速切换
- 📋 **两级菜单**: 主模式（导入/导出）+ 子模式（单个/批量）
- ⚡ **实时预览**: 展示工作流结构、节点数量和环境变量
- 🎉 **优雅反馈**: 使用精美的成功弹窗替代简单提示

### 🔧 系统功能
- 🔒 **敏感信息处理**: 智能检测并选择是否包含敏感环境变量
- 🔄 **多数据源支持**: 支持数据库连接、API调用、手动导入三种数据源
- ⚙️ **灵活配置**: 通过配置文件和环境变量灵活配置系统行为
- 🛡️ **错误容错**: 即使部分工作流操作失败，其他操作仍可正常执行
- 🔗 **多实例支持**: 支持配置多个Dify实例，实现跨实例工作流迁移

## 🏗️ 项目结构

```
workflow-dsl-exporter/
├── backend/                     # 后端服务
│   ├── app.py                  # Flask 应用入口
│   ├── requirements.txt        # Python 依赖
│   ├── models/                 # 数据模型
│   │   └── app.py             # 应用和工作流模型
│   ├── services/               # 业务逻辑服务
│   │   ├── app_dsl_service.py         # DSL 导出服务
│   │   ├── workflow_service.py        # 工作流服务
│   │   ├── workflow_import_service.py # 工作流导入服务
│   │   ├── config_service.py          # 配置服务
│   │   ├── database_connector.py      # 数据库连接器
│   │   └── api_connector.py           # API连接器
│   └── controllers/            # API 控制器
│       ├── app_controller.py             # 应用控制器
│       ├── workflow_controller.py        # 工作流控制器
│       └── workflow_import_controller.py # 工作流导入控制器
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/         # React 组件
│   │   │   ├── WorkflowExporter.tsx      # 主导出导入组件
│   │   │   ├── WorkflowImporter.tsx      # 工作流导入组件
│   │   │   ├── BatchImportModal.tsx      # 批量导入模态框
│   │   │   ├── TargetInstanceSelector.tsx # 目标实例选择器
│   │   │   ├── SuccessModal.tsx          # 成功提示弹窗
│   │   │   ├── BatchExportModal.tsx      # 批量导出模态框
│   │   │   └── ExportConfirmModal.tsx    # 导出确认模态框
│   │   ├── hooks/              # 自定义 Hooks
│   │   │   ├── useWorkflowExport.ts      # 单个导出Hook
│   │   │   └── useBatchWorkflowExport.ts # 批量导出Hook
│   │   ├── services/           # API 服务
│   │   │   └── api.ts         # API调用服务
│   │   └── types/              # TypeScript 类型定义
│   │       └── index.ts       # 类型定义
│   ├── package.json
│   └── vite.config.ts
├── config.yaml                # 配置文件
├── config.example.yaml        # 配置文件模板
├── start.sh                   # 启动脚本
└── README.md                  # 项目文档
```

## 🔧 环境要求

- Python 3.12+
- Node.js 22+
- npm 或 yarn
- PostgreSQL（如果使用数据库模式）

## 🚀 快速开始

### 方法一：使用Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd workflow-dsl-exporter

# 2. 配置系统
cp config.example.yaml config.yaml
# 编辑 config.yaml 配置文件（见下方配置说明）

# 3. 使用Docker Compose启动
docker-compose up -d
```

### 方法二：使用启动脚本

```bash
# 1. 克隆项目
git clone <repository-url>
cd workflow-dsl-exporter

# 2. 配置系统
cp config.example.yaml config.yaml
# 编辑 config.yaml 配置文件（见下方配置说明）

# 3. 设置脚本权限并启动
chmod +x start.sh
./start.sh
```

### 方法三：手动启动

#### 启动后端服务

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install psycopg2-binary  # 如果使用数据库模式

# 启动服务
python app.py
```

#### 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 🌐 访问应用

- **前端界面**：http://localhost:3000
- **后端API**：http://localhost:5000

> 💡 **Docker Compose用户**：如果使用Docker Compose启动，应用将在 http://localhost:8080 访问

![alt text](<images/image copy.png>)
## ⚙️ 配置系统

本项目支持两种数据源模式，可以通过配置文件灵活切换：

### 1. 数据库连接模式（推荐）

直接连接到Dify的PostgreSQL数据库获取真实数据。

#### 适用场景
- 您有Dify数据库的直接访问权限
- 需要获取最完整和最新的工作流数据
- 对性能要求较高

#### 配置步骤

1. **获取Dify数据库连接信息**
   - 通常在Dify的`docker-compose.yml`或`.env`文件中
   - 或者询问系统管理员

2. **配置config.yaml**
```yaml
data_source: 'database'
database:
  type: 'postgresql'
  host: 'your_database_host'     # 数据库主机地址
  port: 5432                     # 数据库端口
  database: 'dify'               # 数据库名称
  username: 'your_username'      # 数据库用户名
  password: 'your_password'      # 数据库密码
  
  # 可选：连接池配置
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  
  # 可选：SSL配置
  ssl_mode: 'prefer'             # disable, allow, prefer, require
```

#### 注意事项
- 确保防火墙允许数据库连接
- 数据库用户需要有读取权限
- 支持从真实的Dify数据库获取所有工作流数据

### 2. API调用模式

通过Dify的API接口获取数据。

#### 适用场景
- 无法直接访问Dify数据库
- 需要通过API获取数据
- 数据安全性要求较高

#### 配置步骤

```yaml
data_source: 'api'
api:
  base_url: 'http://localhost:5001'  # Dify API地址
  
  # Bearer Token认证
  auth:
    type: 'bearer'
    token: 'your_api_token_here'
  
  # 或者基本认证
  # auth:
  #   type: 'basic'
  #   username: 'your_username'
  #   password: 'your_password'
  
  # 或者API Key认证
  # auth:
  #   type: 'api_key'
  #   api_key: 'your_api_key'
  #   api_key_header: 'X-API-Key'
  
  # API端点配置 - 完整的端点列表
  endpoints:
    # 应用相关端点
    apps_list: '/console/api/apps'
    app_detail: '/console/api/apps/{app_id}'
    app_export: '/console/api/apps/{app_id}/export'
    app_import: '/console/api/apps/imports'
    
    # 工作流相关端点
    workflow_draft: '/console/api/apps/{app_id}/workflows/draft'
    workflow_detail: '/console/api/workflows/{workflow_id}'
    
    # 环境变量端点
    environment_variables: '/console/api/apps/{app_id}/variables'
    
    # 导入相关端点
    import_status: '/console/api/apps/imports/{import_id}'
    import_confirm: '/console/api/apps/imports/{import_id}/confirm'
    check_dependencies: '/console/api/apps/imports/{import_id}/check-dependencies'
  
  # 请求配置
  timeout: 30
  retry_count: 3
  retry_delay: 1

# 目标Dify实例配置 (用于工作流导入)
target_instances:
  # 默认实例（本地或当前连接的Dify实例）
  - id: default
    name: 本地Dify实例
    url: https://your-dify-instance.com/
    auth:
      type: bearer  # bearer, basic, api_key
      token: 'your_console_api_token_here'
    is_default: true
    
  # 可以配置多个目标实例
  - id: production
    name: 生产环境Dify
    url: https://prod-dify.company.com/
    auth:
      type: bearer
      token: 'prod_console_api_token_here'
    is_default: false
```



### 🔐 环境变量配置

您可以使用环境变量覆盖配置文件中的设置：

```bash
# 数据库配置
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=dify
export DB_USER=postgres
export DB_PASSWORD=your_password

# API配置
export DIFY_API_URL=http://localhost:5001
export DIFY_API_TOKEN=your_api_token

# 其他配置
export LOG_LEVEL=DEBUG
```

## 📋 使用说明

系统提供两级菜单导航：
- **主模式选择**：工作流导出 / 工作流导入
- **子模式选择**：批量 / 单个

### 📤 工作流导出功能

#### 🎯 批量导出模式

1. **查看工作流列表**
   - 启动后自动加载所有工作流
   - 显示工作流名称、应用ID、节点数量等信息
   - 标识包含敏感变量的工作流

2. **选择工作流**
   - 点击工作流卡片选择单个工作流
   - 使用"全选"按钮选择所有工作流
   - 使用"取消全选"清除所有选择

3. **批量导出**
   - 点击"批量导出"按钮
   - 选择导出格式：
     - **ZIP压缩包**（推荐）：所有文件打包成一个ZIP文件
     - **单独文件**：每个工作流单独下载

4. **处理敏感信息**
   - 如果选中的工作流包含敏感环境变量
   - 系统会弹出确认对话框
   - 可以选择是否包含敏感信息

5. **下载文件**
   - ZIP格式：自动下载压缩包
   - 单独文件：逐个下载每个DSL文件

#### 📝 单个导出模式

1. **切换到单个模式**
   - 在导出页面选择"单个"子模式

2. **输入应用ID**
   - 在输入框中输入要导出的应用ID

3. **获取工作流**
   - 点击"获取工作流"按钮加载工作流信息

4. **查看详情**
   - 查看工作流的节点结构和环境变量

5. **导出DSL**
   - 点击"导出DSL"按钮
   - 如果存在敏感环境变量，会弹出确认框
   - 确认后自动下载DSL文件

### 📥 工作流导入功能

#### 📦 批量导入模式

1. **选择目标实例**
   - 从下拉菜单中选择要导入的目标Dify实例
   - 系统会显示实例的连接状态
   - 可以手动测试连接

2. **选择DSL文件**
   - 点击"选择文件"按钮或拖拽文件到上传区域
   - 支持选择多个YAML格式的DSL文件
   - 系统会验证文件格式和内容

3. **文件预览**
   - 查看已选择的文件列表
   - 显示每个文件的基本信息
   - 可以移除不需要的文件

4. **开始导入**
   - 点击"开始批量导入"按钮
   - 系统显示导入进度
   - 可以看到每个文件的导入状态

5. **导入确认**
   - 对于需要确认的导入，系统会弹出确认对话框
   - 显示导入预览信息
   - 确认后完成导入

6. **查看结果**
   - 导入完成后显示优雅的成功弹窗
   - 包含导入统计信息（成功/失败数量）
   - 可以复制应用ID到剪贴板

#### 🎯 单个导入模式

1. **选择目标实例**
   - 从下拉菜单中选择要导入的目标Dify实例
   - 确认实例连接状态正常

2. **上传DSL文件**
   - 点击上传区域或拖拽单个YAML文件
   - 系统自动验证文件格式

3. **文件解析**
   - 查看DSL文件的解析结果
   - 显示应用名称、工作流类型等信息
   - 检查是否有依赖冲突

4. **确认导入**
   - 点击"导入工作流"按钮
   - 系统解析DSL并显示预览
   - 确认导入信息无误后点击确认

5. **完成导入**
   - 导入成功后显示优雅的成功弹窗
   - 显示新创建应用的ID
   - 可以选择刷新页面或继续操作

## 🔌 API 接口

### 获取所有工作流列表

```http
GET /api/workflows
```

响应：
```json
{
  "workflows": [
    {
      "id": "workflow-uuid",
      "app_id": "app-uuid", 
      "version": "draft",
      "name": "工作流名称",
      "node_count": 5,
      "has_secret_variables": true,
      "last_modified": "2025-07-19T10:11:49.219021"
    }
  ],
  "total": 50
}
```

### 获取工作流草稿

```http
GET /api/apps/{app_id}/workflows/draft
```

### 导出单个应用DSL

```http
GET /api/apps/{app_id}/export?include_secret=false
```

### 批量导出工作流DSL

```http
POST /api/workflows/batch-export
Content-Type: application/json

{
  "app_ids": ["app-id-1", "app-id-2"],
  "include_secret": false,
  "export_format": "zip"
}
```

响应：
```json
{
  "export_format": "zip",
  "filename": "workflows-export-20250719_101149.zip",
  "data": "base64-encoded-zip-data",
  "results": [...],
  "success_count": 2,
  "total_count": 2
}
```

### 获取目标实例列表

```http
GET /api/import/target-instances
```

响应：
```json
{
  "instances": [
    {
      "id": "default",
      "name": "本地Dify实例",
      "url": "https://dify.asyncai.top/",
      "is_default": true,
      "status": "connected"
    }
  ]
}
```

### 测试实例连接

```http
POST /api/import/test-connection
Content-Type: application/json

{
  "instance_id": "default"
}
```

响应：
```json
{
  "success": true,
  "message": "连接成功",
  "instance_info": {
    "version": "0.6.0",
    "name": "Dify Instance"
  }
}
```

### 单个工作流导入

```http
POST /api/import/single
Content-Type: multipart/form-data

{
  "file": "workflow.yaml",
  "target_instance_id": "default"
}
```

响应：
```json
{
  "success": true,
  "import_id": "import-uuid",
  "message": "导入请求已提交",
  "requires_confirmation": true,
  "app_info": {
    "name": "工作流名称",
    "mode": "workflow"
  }
}
```

### 批量工作流导入

```http
POST /api/import/batch
Content-Type: multipart/form-data

{
  "files": ["workflow1.yaml", "workflow2.yaml"],
  "target_instance_id": "default"
}
```

响应：
```json
{
  "success": true,
  "results": [
    {
      "filename": "workflow1.yaml",
      "status": "success",
      "import_id": "import-uuid-1",
      "app_id": "app-uuid-1"
    },
    {
      "filename": "workflow2.yaml", 
      "status": "requires_confirmation",
      "import_id": "import-uuid-2",
      "message": "需要确认导入"
    }
  ],
  "success_count": 1,
  "total_count": 2
}
```

### 确认导入

```http
POST /api/import/confirm
Content-Type: application/json

{
  "import_id": "import-uuid",
  "target_instance_id": "default"
}
```

响应：
```json
{
  "success": true,
  "app_id": "app-uuid",
  "message": "导入成功",
  "app_info": {
    "name": "工作流名称",
    "id": "app-uuid"
  }
}
```

## 💻 技术栈

### 后端

- **Flask**: Web 框架
- **Flask-RESTful**: RESTful API 支持
- **Flask-CORS**: 跨域支持
- **PyYAML**: YAML 处理
- **Pydantic**: 数据验证
- **psycopg2**: PostgreSQL 连接器
- **requests**: HTTP 客户端

### 前端

- **React 18**: 前端框架
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Tailwind CSS**: 样式框架

## 🛠️ 开发说明

### 后端开发

```bash
cd backend

# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器（调试模式）
export FLASK_DEBUG=1
python app.py
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 🚢 部署

### 生产环境部署

1. **后端部署**:
   ```bash
   cd backend
   pip install -r requirements.txt
   gunicorn -w 4 -b 0.0.0.0:5000 app:create_app
   ```

2. **前端部署**:
   ```bash
   cd frontend
   npm run build
   # 将 dist 目录部署到静态文件服务器
   ```

### Docker 部署

```dockerfile
# Dockerfile 示例
FROM python:3.9-slim

# 安装后端依赖
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY backend/ .
COPY config.yaml ../

# 暴露端口
EXPOSE 5000

CMD ["python", "app.py"]
```

```bash
# 构建和运行
docker build -t workflow-dsl-exporter .
docker run -p 5000:5000 -v $(pwd)/config.yaml:/app/config.yaml workflow-dsl-exporter
```

## 🔧 故障排除

### 数据库连接问题

**连接被拒绝**
```bash
# 检查数据库状态
pg_isready -h your_host -p 5432

# 检查防火墙
telnet your_host 5432
```

**认证失败**
- 确认用户名和密码正确
- 检查PostgreSQL的`pg_hba.conf`配置

**表不存在**
- 确认连接到正确的Dify数据库
- 检查数据库schema

### API连接问题

**网络连接失败**
```bash
# 测试API连通性
curl -I http://your-dify-api/api/health
```

**认证失败**
- 检查API Token是否有效
- 确认Token格式正确（Bearer token）

### 前端问题

**页面显示demo数据**
- 检查后端是否正常启动
- 确认数据库连接配置正确
- 查看浏览器控制台错误

**批量导出按钮禁用**
- 确保至少选择了一个工作流
- 检查后端API是否响应正常

### 常见错误解决

1. **ImportError: No module named 'psycopg2'**
   ```bash
   pip install psycopg2-binary
   ```

2. **端口占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :5000
   lsof -i :3000
   
   # 杀死进程
   kill -9 <PID>
   ```

3. **权限错误**
   ```bash
   # 给启动脚本执行权限
   chmod +x start.sh
   ```

## 🔒 安全配置

### 高级配置选项

```yaml
# 安全配置
security:
  # 允许的IP地址（空表示允许所有）
  allowed_ips: []
  
  # API访问限制
  rate_limit:
    enabled: true
    requests_per_minute: 60

# 缓存配置
cache:
  enabled: true
  type: 'memory'    # memory, redis, file
  ttl: 300          # 缓存时间（秒）

# 日志配置
logging:
  level: 'INFO'     # DEBUG, INFO, WARNING, ERROR
  file: 'logs/app.log'
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### 最佳实践

1. **数据安全**
   - 不要在配置文件中直接写入敏感信息
   - 使用环境变量存储密码和Token
   - 定期更换API密钥

2. **性能优化**
   - 启用缓存减少重复请求
   - 合理设置数据库连接池大小
   - 监控系统资源使用

3. **备份策略**
   - 定期备份配置文件
   - 手动导入模式下启用自动备份
   - 保留导出文件的备份

## 📈 更新日志

### v3.0.0 (2025-08-03)
- 🎯 **新增工作流导入功能**：支持单个和批量工作流导入
- 🔗 **多实例支持**：可配置多个目标Dify实例进行跨实例迁移
- 🎨 **两级菜单设计**：主模式（导入/导出）+ 子模式（单个/批量）
- 🎉 **优雅用户体验**：使用精美的成功弹窗替代简单提示
- ⚙️ **灵活API配置**：支持可配置的API端点和认证方式
- 📋 **导入确认机制**：智能解析DSL并提供导入预览
- 🔄 **实时状态更新**：显示导入进度和连接状态
- 📊 **统计信息展示**：导入完成后显示详细的成功/失败统计

### v2.0.0 (2025-07-19)
- ✨ 新增批量导出功能
- 📦 支持ZIP文件打包下载
- 🎨 全新的双模式界面设计
- 🔄 支持真实Dify数据库连接
- ⚡ 实时进度显示和错误处理
- 🛡️ 增强的敏感信息处理

### v1.0.0 (2024-01-XX)
- 🎉 初始版本发布
- 📝 基本的工作流导出功能
- 🌐 Web 界面支持
- 🔒 敏感信息处理

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请：
- 提交 Issue
- 联系开发者
- 查看项目 Wiki

---

**Happy Importing & Exporting! 🚀📥📤** 