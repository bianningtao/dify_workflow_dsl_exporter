# 工作流 DSL 导出器

这是一个提取自 Dify 项目的工作流 DSL 导出功能的独立项目。该项目提供了一个完整的前后端解决方案，用于导出工作流配置为 DSL 格式。

## 项目结构

```
workflow-dsl-exporter/
├── backend/                  # 后端服务
│   ├── app.py               # Flask 应用入口
│   ├── requirements.txt     # Python 依赖
│   ├── models/              # 数据模型
│   │   └── app.py          # 应用和工作流模型
│   ├── services/            # 业务逻辑服务
│   │   ├── app_dsl_service.py      # DSL 导出服务
│   │   └── workflow_service.py     # 工作流服务
│   └── controllers/         # API 控制器
│       ├── app_controller.py       # 应用控制器
│       └── workflow_controller.py  # 工作流控制器
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── components/      # React 组件
│   │   ├── hooks/          # 自定义 Hooks
│   │   ├── services/       # API 服务
│   │   └── types/          # TypeScript 类型定义
│   ├── package.json
│   └── vite.config.ts
├── start.sh                 # 启动脚本
└── README.md               # 项目文档
```

## 功能特性

- ✅ **工作流导出**: 将工作流配置导出为 YAML 格式的 DSL 文件
- ✅ **敏感信息处理**: 支持选择是否包含敏感信息（如 API 密钥）
- ✅ **可视化界面**: 提供直观的 Web 界面进行操作
- ✅ **实时预览**: 展示工作流结构和环境变量
- ✅ **错误处理**: 完善的错误处理和用户反馈
- ✅ **多数据源支持**: 支持数据库连接、API调用、手动导入三种数据源
- ✅ **灵活配置**: 通过配置文件和环境变量灵活配置系统行为
- ✅ **真实数据获取**: 从实际的Dify系统获取工作流数据，而非模拟数据

## 配置系统

本项目支持三种数据源模式，可以通过配置文件灵活切换：

### 1. 数据库连接模式（推荐）

直接连接到Dify的PostgreSQL数据库获取真实数据。

```yaml
# config.yaml
data_source: 'database'
database:
  type: 'postgresql'
  host: 'localhost'
  port: 5432
  database: 'dify'
  username: 'postgres'
  password: 'your_password'
```

### 2. API调用模式

通过Dify的API接口获取数据。

```yaml
# config.yaml
data_source: 'api'
api:
  base_url: 'http://localhost:5001'
  auth:
    type: 'bearer'
    token: 'your_api_token'
```

### 3. 手动导入模式

手动上传工作流数据文件。

```yaml
# config.yaml
data_source: 'manual'
manual:
  storage_type: 'file'
  file_storage:
    data_dir: './data'
```

### 配置文件设置

1. 复制配置文件模板：
```bash
cp config.example.yaml config.yaml
```

2. 根据您的实际情况修改 `config.yaml` 中的配置。

3. 也可以使用环境变量覆盖配置：
```bash
export DB_HOST=localhost
export DB_USER=postgres
export DB_PASSWORD=your_password
export DIFY_API_URL=http://localhost:5001
export DIFY_API_TOKEN=your_token
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn
- PostgreSQL（如果使用数据库模式）

### 方法一：使用启动脚本（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd workflow-dsl-exporter

# 配置系统
cp config.example.yaml config.yaml
# 编辑 config.yaml 配置文件

# 设置脚本权限
chmod +x start.sh

# 启动服务
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

### 访问应用

- 前端界面：http://localhost:3000
- 后端API：http://localhost:5000

## 使用说明

1. **输入应用ID**: 在输入框中输入要导出的应用ID
2. **获取工作流**: 点击"获取工作流"按钮加载工作流信息
3. **查看详情**: 查看工作流的节点结构和环境变量
4. **导出DSL**: 点击"导出DSL"按钮
5. **处理敏感信息**: 如果存在敏感环境变量，会弹出确认框选择是否包含
6. **下载文件**: 确认后会自动下载DSL文件

## API 接口

### 获取工作流草稿

```http
GET /api/apps/{app_id}/workflows/draft
```

### 导出应用DSL

```http
GET /api/apps/{app_id}/export?include_secret=false
```

参数：
- `include_secret`: 是否包含敏感信息（默认：false）

## 技术栈

### 后端

- **Flask**: Web 框架
- **Flask-RESTful**: RESTful API 支持
- **Flask-CORS**: 跨域支持
- **PyYAML**: YAML 处理
- **Pydantic**: 数据验证

### 前端

- **React**: 前端框架
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Tailwind CSS**: 样式框架

## 开发说明

### 后端开发

```bash
cd backend

# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器
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

## 自定义配置

### 后端配置

在 `backend/app.py` 中可以修改：
- 服务器端口（默认：5000）
- CORS 配置
- API 路由

### 前端配置

在 `frontend/src/services/api.ts` 中可以修改：
- API 基础URL
- 请求超时时间
- 错误处理策略

## 部署

### 生产环境部署

1. **后端部署**:
   ```bash
   cd backend
   pip install -r requirements.txt
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **前端部署**:
   ```bash
   cd frontend
   npm run build
   # 将 dist 目录部署到静态文件服务器
   ```

### Docker 部署

```bash
# 构建镜像
docker build -t workflow-dsl-exporter .

# 运行容器
docker run -p 3000:3000 -p 5000:5000 workflow-dsl-exporter
```

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查 Python 版本是否正确
   - 确认所有依赖已安装
   - 检查端口 5000 是否被占用

2. **前端启动失败**
   - 检查 Node.js 版本是否正确
   - 删除 node_modules 重新安装
   - 检查端口 3000 是否被占用

3. **API 请求失败**
   - 确认后端服务正在运行
   - 检查 CORS 配置
   - 查看浏览器控制台错误信息

### 调试模式

启用调试模式：

```bash
# 后端
export FLASK_DEBUG=1
python app.py

# 前端
npm run dev
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 基本的工作流导出功能
- Web 界面支持
- 敏感信息处理

## 联系方式

如有问题或建议，请提交 Issue 或联系开发者。 