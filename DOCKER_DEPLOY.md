# Docker 部署指南

## 快速开始

### 1. 配置环境变量

```bash
cd docker
cp env.example .env
# 编辑 .env 文件，至少需要修改以下配置：
# - MYSQL_ROOT_PASSWORD（必须修改）
# - JWT_SECRET_KEY（建议修改）
```

### 2. 构建和启动

```bash
# 在项目根目录下执行
docker-compose -f docker/docker-compose.yml up -d
```

### 3. 访问应用

- 前端地址: `http://localhost` (默认80端口)
- 默认管理员账号: `admin@example.com`
- 默认密码: `admin123456` (首次登录后请立即修改)

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker/docker-compose.yml logs -f

# 查看应用日志
docker-compose -f docker/docker-compose.yml logs -f app

# 查看MySQL日志
docker-compose -f docker/docker-compose.yml logs -f mysql
```

### 5. 停止服务

```bash
docker-compose -f docker/docker-compose.yml down

# 同时删除数据卷（谨慎操作）
docker-compose -f docker/docker-compose.yml down -v
```

## 目录结构

```
docker/
├── Dockerfile              # 应用镜像构建文件
├── docker-compose.yml      # Docker Compose 编排文件
├── nginx.conf              # Nginx 配置
├── entrypoint.sh          # 容器启动脚本
├── mysql.cnf              # MySQL 配置
├── env.example            # 环境变量模板
├── .dockerignore          # Docker 忽略文件
└── dify_workflow_config.sql  # MySQL 初始化脚本
```

## 端口说明

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|---------|---------|------|
| App (Nginx) | 80 | 80 (可配置 APP_PORT) | 前端访问入口 |
| Backend | 5001 | - | 后端API (内部) |
| MySQL | 3306 | 3306 (可配置 MYSQL_PORT) | 数据库 |

## 数据持久化

- MySQL数据: `mysql_data` volume
- 应用日志: `app_logs` volume

## 健康检查

- App: `http://localhost/health`
- MySQL: 使用 `mysqladmin ping`

## 故障排查

### 应用无法启动
```bash
# 检查MySQL是否就绪
docker-compose -f docker/docker-compose.yml exec mysql mysqladmin ping

# 查看应用日志
docker-compose -f docker/docker-compose.yml logs app
```

### 数据库连接失败
- 检查 `.env` 文件中的数据库配置是否正确
- 确保MySQL服务健康: `docker-compose -f docker/docker-compose.yml ps`

## 生产环境建议

1. **修改默认密码**: 修改 `MYSQL_ROOT_PASSWORD` 和 `JWT_SECRET_KEY`
2. **调整Worker数量**: 根据服务器配置调整 `GUNICORN_WORKERS`
3. **启用HTTPS**: 在nginx前面加一层反向代理(如Traefik、Caddy)
4. **备份数据**: 定期备份 `mysql_data` volume
5. **监控日志**: 配置日志收集和监控系统

