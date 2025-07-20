# Docker 部署指南

## 概述

Workflow DSL Exporter v0.1.0 支持使用 Docker 进行容器化部署，提供完整的前后端一体化解决方案。

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+ (可选)
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

## 快速开始

### 方法一：使用构建脚本

```bash
# 构建镜像
./docker/build.sh

# 部署应用
./docker/deploy.sh
```

### 方法二：使用 Docker Compose

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方法三：手动构建和运行

```bash
# 构建镜像
docker build -t workflow-dsl-exporter:v0.1.0 .

# 运行容器
docker run -d \
  --name workflow-dsl-exporter \
  -p 80:80 \
  -p 5000:5000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.example.yaml:/app/backend/config.yaml:ro \
  --restart unless-stopped \
  workflow-dsl-exporter:v0.1.0
```

## 访问应用

部署成功后，可以通过以下地址访问：

- **前端界面**: http://localhost
- **后端API**: http://localhost/api
- **健康检查**: http://localhost/health

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| FLASK_ENV | production | Flask运行环境 |
| PYTHONPATH | /app/backend | Python模块路径 |

### 端口映射

| 容器端口 | 主机端口 | 说明 |
|----------|----------|------|
| 80 | 80 | HTTP服务 |
| 5000 | 5000 | Flask后端API |

### 数据卷

| 容器路径 | 主机路径 | 说明 |
|----------|----------|------|
| /app/logs | ./logs | 日志文件 |
| /app/data | ./data | 数据文件 |
| /app/backend/config.yaml | ./config.example.yaml | 配置文件 |

## 管理命令

### 查看容器状态
```bash
docker ps
```

### 查看日志
```bash
# 查看实时日志
docker logs -f workflow-dsl-exporter

# 查看最近100行日志
docker logs --tail 100 workflow-dsl-exporter
```

### 重启服务
```bash
docker restart workflow-dsl-exporter
```

### 停止服务
```bash
docker stop workflow-dsl-exporter
```

### 删除容器
```bash
docker rm workflow-dsl-exporter
```

### 进入容器
```bash
docker exec -it workflow-dsl-exporter /bin/bash
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :80
   lsof -i :5000
   
   # 修改端口映射
   docker run -p 8080:80 -p 5001:5000 ...
   ```

2. **权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x docker/*.sh
   ```

3. **构建失败**
   ```bash
   # 清理Docker缓存
   docker system prune -a
   
   # 重新构建
   docker build --no-cache -t workflow-dsl-exporter:v0.1.0 .
   ```

4. **容器启动失败**
   ```bash
   # 查看详细错误信息
   docker logs workflow-dsl-exporter
   
   # 检查配置文件
   cat config.example.yaml
   ```

### 日志位置

- 应用日志: `./logs/app.log`
- Nginx访问日志: 容器内 `/var/log/nginx/access.log`
- Nginx错误日志: 容器内 `/var/log/nginx/error.log`

## 版本信息

- **当前版本**: v0.1.0
- **构建日期**: $(date)
- **Docker基础镜像**: python:3.11-slim
- **Node.js版本**: 18-alpine

## 更新说明

### v0.1.0
- 初始Docker支持
- 多阶段构建优化
- Nginx反向代理配置
- 健康检查支持
- 自动化部署脚本 