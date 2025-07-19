# 工作流 DSL 导出器

这是一个从 Dify 系统批量导出工作流 DSL 配置的独立工具。该项目提供了完整的前后端解决方案，支持单个和批量导出工作流配置为 DSL 格式，包含现代化的 Web 界面和灵活的数据源配置。

## ✨ 功能特性

- 🚀 **批量导出**: 支持选择多个工作流进行批量导出
- 📦 **ZIP打包**: 自动将多个DSL文件打包成ZIP格式下载
- 🔒 **敏感信息处理**: 智能检测并选择是否包含敏感环境变量
- 🎨 **现代化界面**: 提供直观美观的 Web 界面
- ⚡ **实时预览**: 展示工作流结构、节点数量和环境变量
- 🔄 **多数据源支持**: 支持数据库连接、API调用、手动导入三种数据源
- ⚙️ **灵活配置**: 通过配置文件和环境变量灵活配置系统行为
- 📊 **进度显示**: 批量导出时显示实时进度和状态
- 🛡️ **错误容错**: 即使部分工作流导出失败，其他工作流仍可正常导出

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
│   │   ├── config_service.py          # 配置服务
│   │   ├── database_connector.py      # 数据库连接器
│   │   ├── api_connector.py           # API连接器
│   │   └── manual_import_service.py   # 手动导入服务
│   └── controllers/            # API 控制器
│       ├── app_controller.py          # 应用控制器
│       └── workflow_controller.py     # 工作流控制器
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/         # React 组件
│   │   │   ├── WorkflowExporter.tsx      # 主导出组件
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

- Python 3.8+
- Node.js 16+
- npm 或 yarn
- PostgreSQL（如果使用数据库模式）

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

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

### 方法二：手动启动

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

## ⚙️ 配置系统

本项目支持三种数据源模式，可以通过配置文件灵活切换：

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
  
  # 或者API Key认证
  # auth:
  #   type: 'api_key'
  #   api_key: 'your_api_key'
  #   api_key_header: 'X-API-Key'
  
  # API端点配置
  endpoints:
    apps: '/api/apps/{app_id}'
    workflows: '/api/apps/{app_id}/workflows/draft'
    environment_variables: '/api/apps/{app_id}/env-variables'
    workflows_list: '/api/workflows'  # 工作流列表端点
  
  # 请求配置
  timeout: 30
  retry_count: 3
  retry_delay: 1
```

### 3. 手动导入模式

手动上传工作流数据文件。

#### 适用场景
- 无法直接访问Dify系统
- 需要离线处理工作流数据
- 用于测试或演示目的

#### 配置步骤

```yaml
data_source: 'manual'
manual:
  storage_type: 'file'
  file_storage:
    data_dir: './data'              # 数据存储目录
    supported_formats: ['json', 'yaml', 'yml']
    auto_backup: true               # 自动备份
    backup_dir: './data/backups'    # 备份目录
```

#### 数据文件格式

在`./data`目录下创建文件，文件名格式：`{app_id}.{format}`

```yaml
# data/your-app-id.yaml
version: '1.0'
kind: app
app:
  name: 您的工作流应用
  mode: workflow
  icon: 🚀
  description: 应用描述
workflow:
  version: '1.0'
  graph:
    nodes:
      - id: start
        type: start
        data:
          type: start
          title: 开始
    edges: []
  features: {}
  environment_variables:
    - name: API_KEY
      value: your_api_key
      value_type: secret
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

### 🎯 批量导出模式（默认）

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

### 📝 单个导出模式

1. **切换模式**
   - 选择"单个导出模式"单选按钮

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

**Happy Exporting! 🚀** 