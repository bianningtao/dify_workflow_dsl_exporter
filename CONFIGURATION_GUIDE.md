<!--
 * @Author: bianningtao ab2961513324@163.com
 * @Date: 2025-10-20 12:12:35
 * @LastEditors: bianningtao ab2961513324@163.com
 * @LastEditTime: 2025-10-20 12:32:59
 * @FilePath: /dify_workflow_dsl_exporter/CONFIGURATION_GUIDE.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
# 配置指南

## 📋 概述

系统配置分为两部分：
1. **系统固定配置** - 存储在 `backend/config_db.yaml` 文件中
2. **用户业务配置** - 存储在 MySQL 数据库中（每个用户独立）

## 📂 配置文件位置

```
backend/
├── config_db.yaml          # 实际配置文件（需要创建）
└── config_db.yaml.example  # 配置文件模板
```

## 🚀 快速开始

### 1. 创建配置文件

```bash
cd backend
cp config_db.yaml.example config_db.yaml
```

### 2. 修改数据库连接

编辑 `config_db.yaml`，修改数据库连接信息：

```yaml
config_database:
  host: localhost
  port: 3306
  database: dify_workflow_config
  username: root
  password: your_password  # 修改为你的数据库密码
```

### 3. 生成安全的 JWT 密钥

⚠️ **重要**: 生产环境必须修改默认密钥！

```bash
# 生成随机密钥
python -c "import secrets; print(secrets.token_hex(32))"

# 输出示例: a1b2c3d4e5f6...
```

将生成的密钥填入配置文件：

```yaml
jwt:
  secret_key: "a1b2c3d4e5f6..."  # 替换为生成的密钥
```

### 4. 测试配置

```bash
cd backend
uv run python services/system_config_loader.py
```

如果看到配置信息输出，说明配置加载成功！

## 📝 配置详解

### 一、数据库配置 (`config_database`)

```yaml
config_database:
  type: mysql                # 数据库类型（目前仅支持MySQL）
  host: localhost            # 数据库主机
  port: 3306                 # 数据库端口
  database: dify_workflow_config  # 数据库名称
  username: root             # 用户名
  password: myroot           # 密码
  charset: utf8mb4           # 字符集
  
  # 连接池配置（通常无需修改）
  pool_size: 10              # 连接池大小
  max_overflow: 20           # 最大溢出连接数
  pool_timeout: 30           # 连接超时（秒）
```

### 二、JWT 认证配置 (`jwt`)

```yaml
jwt:
  # JWT 密钥 - 用于签名和验证 token
  # ⚠️ 生产环境必须修改为随机字符串
  secret_key: "your-secret-key-change-in-production"
  
  # Token 过期时间（天）
  # 默认 7 天，用户登录后 7 天内无需重新登录
  expires_days: 7
  
  # Token 签发者标识
  issuer: "dify-workflow-exporter"
  
  # 加密算法（推荐使用 HS256）
  algorithm: "HS256"
```

**安全建议**:
- 生产环境必须使用随机密钥
- 密钥长度建议至少 32 字节（64 个十六进制字符）
- 不要将密钥提交到版本控制系统
- 可以使用环境变量覆盖（更安全）

### 三、用户系统配置 (`user_system`)

```yaml
user_system:
  # 密码加密轮数（bcrypt rounds）
  # 值越大越安全，但加密和验证速度越慢
  # 推荐范围: 10-14
  password_hash_rounds: 12
  
  # 默认管理员配置
  default_admin:
    email: "admin@example.com"
    username: "系统管理员"
    password: "admin123456"  # ⚠️ 首次登录后请立即修改
  
  # 密码策略
  password_policy:
    min_length: 6              # 最小长度
    require_uppercase: false   # 是否需要大写字母
    require_lowercase: false   # 是否需要小写字母
    require_numbers: false     # 是否需要数字
    require_special_chars: false  # 是否需要特殊字符
```

**密码策略说明**:
- 当前默认策略较为宽松（仅要求 6 个字符）
- 生产环境建议启用更严格的策略：
  ```yaml
  password_policy:
    min_length: 8
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_special_chars: true
  ```

### 四、应用配置 (`application`)

```yaml
application:
  name: "Dify Workflow DSL 管理器"
  version: "2.0.0"
  
  flask:
    debug: false           # 生产环境必须为 false
    host: "0.0.0.0"       # 监听所有网卡
    port: 5001            # 后端端口
    
  cors:
    enabled: true
    origins:
      - "http://localhost:5173"   # 前端开发服务器
      - "http://localhost:3000"   # 备用端口
    methods:
      - "GET"
      - "POST"
      - "PUT"
      - "DELETE"
      - "OPTIONS"
    allow_headers:
      - "Content-Type"
      - "Authorization"
```

**CORS 配置说明**:
- 开发环境: 允许 localhost
- 生产环境: 修改 `origins` 为实际域名
  ```yaml
  origins:
    - "https://your-domain.com"
  ```

### 五、日志配置 (`logging`)

```yaml
logging:
  level: "INFO"  # DEBUG | INFO | WARNING | ERROR | CRITICAL
  
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  file:
    enabled: true
    path: "logs/app.log"
    max_bytes: 10485760      # 10MB
    backup_count: 5          # 保留 5 个历史文件
```

**日志级别选择**:
- `DEBUG`: 开发环境，输出所有调试信息
- `INFO`: 生产环境推荐，输出正常运行信息
- `WARNING`: 只输出警告和错误
- `ERROR`: 只输出错误

### 六、安全配置 (`security`)

```yaml
security:
  max_login_attempts: 5     # 最大登录失败次数（暂未实现）
  lockout_duration: 15      # 锁定时长（分钟）（暂未实现）
  session_timeout: 30       # 会话超时（分钟）（暂未实现）
```

⚠️ 这些功能暂未实现，为未来扩展预留。

## 🌍 环境变量配置

环境变量的优先级**高于**配置文件。

### 数据库配置

```bash
export CONFIG_DB_HOST=localhost
export CONFIG_DB_PORT=3306
export CONFIG_DB_DATABASE=dify_workflow_config
export CONFIG_DB_USERNAME=root
export CONFIG_DB_PASSWORD=your_password
```

### JWT 配置

```bash
export JWT_SECRET_KEY=your-secret-key
export JWT_EXPIRES_DAYS=7
```

### 应用配置

```bash
export FLASK_DEBUG=false
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5001
```

### 使用 .env 文件

创建 `backend/.env` 文件：

```bash
# 数据库配置
CONFIG_DB_HOST=localhost
CONFIG_DB_PORT=3306
CONFIG_DB_DATABASE=dify_workflow_config
CONFIG_DB_USERNAME=root
CONFIG_DB_PASSWORD=your_password

# JWT 配置
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRES_DAYS=7

# 应用配置
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
```

加载环境变量：

```bash
source backend/.env
uv run python app.py
```

## 🔐 生产环境安全配置

### 必做事项

1. **修改 JWT 密钥**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

2. **修改默认管理员密码**
- 首次登录后立即修改
- 或者在配置文件中修改 `user_system.default_admin.password`

3. **关闭 Debug 模式**
```yaml
flask:
  debug: false
```

4. **使用 HTTPS**
- 配置反向代理（Nginx/Apache）
- 强制使用 SSL/TLS

5. **限制 CORS 来源**
```yaml
cors:
  origins:
    - "https://your-domain.com"  # 只允许实际域名
```

6. **使用环境变量存储敏感信息**
- 不要在配置文件中硬编码密码
- 使用 `.env` 文件或系统环境变量

### 推荐事项

1. **增强密码策略**
```yaml
password_policy:
  min_length: 8
  require_uppercase: true
  require_lowercase: true
  require_numbers: true
  require_special_chars: true
```

2. **缩短 Token 有效期**
```yaml
jwt:
  expires_days: 1  # 1天更安全
```

3. **启用日志文件**
```yaml
logging:
  level: "WARNING"  # 生产环境减少日志量
  file:
    enabled: true
```

4. **定期备份数据库**

5. **监控系统日志**

## 🧪 配置测试

### 测试配置加载

```bash
cd backend
uv run python services/system_config_loader.py
```

输出示例：
```
============================================================
系统配置测试
============================================================

📦 JWT 配置:
  密钥: a1b2c3d4e5f6... (已截断)
  过期天数: 7 天
  签发者: dify-workflow-exporter
  算法: HS256

👤 用户系统配置:
  密码加密轮数: 12
  ...
```

### 安全检查

配置测试会自动检查安全问题：

```
⚠️  安全检查:
⚠️  JWT 密钥使用默认值，生产环境请务必修改！
⚠️  默认管理员密码未修改，请首次登录后立即修改！
```

如果看到警告，请及时修复。

## 📚 配置示例

### 开发环境配置

```yaml
jwt:
  secret_key: "dev-secret-key-not-for-production"
  expires_days: 30  # 开发环境可以更长

application:
  flask:
    debug: true  # 开发环境可以开启
    host: "127.0.0.1"
    port: 5001

logging:
  level: "DEBUG"  # 开发环境详细日志
```

### 生产环境配置

```yaml
jwt:
  secret_key: "a1b2c3d4e5f6...64位随机字符串"
  expires_days: 7

application:
  flask:
    debug: false
    host: "0.0.0.0"
    port: 5001
  
  cors:
    origins:
      - "https://workflow.example.com"

logging:
  level: "WARNING"
```

## 🔄 配置热更新

配置文件修改后需要重启服务才能生效：

```bash
# 停止服务
Ctrl+C

# 重新启动
cd backend
uv run python app.py
```

## 🐛 常见问题

### Q1: 配置文件不存在

**错误**: `FileNotFoundError: config_db.yaml not found`

**解决**:
```bash
cd backend
cp config_db.yaml.example config_db.yaml
```

### Q2: JWT 密钥警告

**警告**: `⚠️ JWT 密钥使用默认值`

**解决**:
```bash
# 生成新密钥
python -c "import secrets; print(secrets.token_hex(32))"

# 修改 config_db.yaml
jwt:
  secret_key: "新生成的密钥"
```

### Q3: 数据库连接失败

**错误**: `Can't connect to MySQL server`

**解决**:
1. 检查 MySQL 是否运行: `lsof -i :3306`
2. 检查配置文件中的用户名和密码
3. 测试连接: `mysql -u root -p`

### Q4: Token 过期太快

**问题**: 用户频繁需要重新登录

**解决**: 增加过期时间
```yaml
jwt:
  expires_days: 30  # 改为 30 天
```

## 📖 相关文档

- **DEPLOYMENT_COMPLETE.md** - 部署指南
- **TROUBLESHOOTING.md** - 故障排除
- **database_schema.sql** - 数据库表结构
- **system_config_loader.py** - 配置加载器源码

## 💡 最佳实践

1. **版本控制**
   - 将 `config_db.yaml` 添加到 `.gitignore`
   - 只提交 `config_db.yaml.example`

2. **环境隔离**
   - 开发、测试、生产使用不同的配置
   - 使用环境变量区分环境

3. **密钥管理**
   - 使用密钥管理服务（如 AWS Secrets Manager）
   - 定期轮换密钥

4. **配置审计**
   - 记录配置变更历史
   - 重要配置需要审批

5. **监控告警**
   - 监控配置加载失败
   - 监控 JWT 验证失败次数

---

**需要帮助？** 查看 TROUBLESHOOTING.md 或检查日志文件。

