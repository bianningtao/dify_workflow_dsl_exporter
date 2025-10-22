# ============================================
# 多阶段构建 Dockerfile
# 阶段1: 构建前端
# 阶段2: 构建最终镜像（包含前端构建产物和后端）
# ============================================

# ==================== 阶段 1: 构建前端 ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖（包括开发依赖，因为构建需要）
RUN npm ci

# 复制前端源代码
COPY frontend/ ./

# 构建前端（生成静态文件到 dist 目录）
RUN npm run build

# ==================== 阶段 2: 最终镜像 ====================
FROM python:3.11-slim-bookworm

# 设置工作目录
WORKDIR /app

# 更换为阿里云镜像源以提高下载速度和稳定性
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || \
    (echo "deb https://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
     echo "deb https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
     echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list)

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    default-mysql-client \
    pkg-config \
    nginx \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt ./backend/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r backend/requirements.txt && \
    pip install --no-cache-dir gunicorn

# 复制后端代码
COPY backend/ ./backend/

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 复制 nginx 配置
COPY docker/nginx.conf /etc/nginx/sites-available/default

# 创建日志目录
RUN mkdir -p /app/logs /app/backend/logs

# 复制启动脚本
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 暴露端口（nginx 前端端口）
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# 启动脚本
ENTRYPOINT ["/entrypoint.sh"]

