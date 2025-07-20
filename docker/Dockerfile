# 多阶段构建 Dockerfile
# 第一阶段：构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装前端依赖（包含开发依赖，因为构建需要）
RUN npm ci

# 复制前端源代码
COPY frontend/ ./

# 构建前端
RUN npm run build

# 第二阶段：构建后端
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt ./

# 安装Python依赖（使用国内镜像源）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt

# 复制后端源代码
COPY backend/ ./

# 第三阶段：最终镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONPATH=/app/backend
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && pip install --upgrade pip

# 创建应用目录
WORKDIR /app

# 从构建阶段复制文件
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /app/backend /app/backend

# 创建必要的目录
RUN mkdir -p /app/logs /app/data

# 复制nginx配置
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 复制启动脚本
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 80 5000

# 设置版本标签
LABEL version="v0.1.0"
LABEL description="Workflow DSL Exporter"

# 启动应用
CMD ["/app/start.sh"] 