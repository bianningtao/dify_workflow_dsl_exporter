#!/bin/bash

# Docker构建脚本 - Workflow DSL Exporter v0.1.0

set -e

VERSION="v0.1.0"
IMAGE_NAME="workflow-dsl-exporter"
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"

echo "开始构建 Docker 镜像..."
echo "版本: ${VERSION}"
echo "镜像名称: ${FULL_IMAGE_NAME}"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker 未运行或无法访问"
    exit 1
fi

# 构建镜像
echo "构建镜像中..."
docker build -t ${FULL_IMAGE_NAME} -f docker/Dockerfile .

# 检查构建结果
if [ $? -eq 0 ]; then
    echo "✅ 镜像构建成功!"
    echo "镜像标签:"
    docker images | grep ${IMAGE_NAME}
    
    echo ""
    echo "运行命令:"
    echo "  docker run -p 80:80 -p 5000:5000 ${FULL_IMAGE_NAME}"
    echo "  或使用 docker-compose:"
    echo "  docker-compose up -d"
else
    echo "❌ 镜像构建失败!"
    exit 1
fi 