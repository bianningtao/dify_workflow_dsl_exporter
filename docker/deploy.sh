#!/bin/bash

# Docker部署脚本 - Workflow DSL Exporter v0.1.0

set -e

VERSION="v0.1.0"
IMAGE_NAME="workflow-dsl-exporter"
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"
CONTAINER_NAME="workflow-dsl-exporter"

echo "开始部署 Workflow DSL Exporter v0.1.0..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker 未运行或无法访问"
    exit 1
fi

# 检查镜像是否存在
if ! docker images | grep -q "${IMAGE_NAME}"; then
    echo "镜像不存在，正在构建..."
    ./docker/build.sh
fi

# 停止并删除现有容器
echo "停止现有容器..."
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

# 创建必要的目录
mkdir -p logs data

# 启动容器
echo "启动新容器..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p 80:80 \
    -p 5000:5000 \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/config.example.yaml:/app/backend/config.yaml:ro \
    --restart unless-stopped \
    ${FULL_IMAGE_NAME}

# 等待容器启动
echo "等待容器启动..."
sleep 10

# 检查容器状态
if docker ps | grep -q ${CONTAINER_NAME}; then
    echo "✅ 部署成功!"
    echo ""
    echo "应用信息:"
    echo "  容器名称: ${CONTAINER_NAME}"
    echo "  前端地址: http://localhost"
    echo "  后端API: http://localhost/api"
    echo "  健康检查: http://localhost/health"
    echo ""
    echo "查看日志: docker logs ${CONTAINER_NAME}"
    echo "停止服务: docker stop ${CONTAINER_NAME}"
    echo "重启服务: docker restart ${CONTAINER_NAME}"
else
    echo "❌ 部署失败!"
    echo "查看容器日志:"
    docker logs ${CONTAINER_NAME}
    exit 1
fi 