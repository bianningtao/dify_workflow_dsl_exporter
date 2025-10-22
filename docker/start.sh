#!/bin/bash
###
 # @Author: bianningtao ab2961513324@163.com
 # @Date: 2025-10-22 08:51:56
 # @LastEditors: bianningtao ab2961513324@163.com
 # @LastEditTime: 2025-10-22 08:52:00
 # @FilePath: /dify_workflow_dsl_exporter/docker/start.sh
 # @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
### 
COMPOSE_FILE="/Users/bianningtao/Desktop/JOTO.nosync/dify-export-workflow/dify_workflow_dsl_exporter/docker/docker-compose.yml"

echo "🧹 停止旧容器..."
docker compose -f "$COMPOSE_FILE" down

echo "🔨 构建镜像..."
DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker compose -f "$COMPOSE_FILE" build --quiet

echo "🚀 启动服务..."
docker compose -f "$COMPOSE_FILE" up -d

echo "⏳ 等待容器启动..."
sleep 8

echo "📋 当前容器状态:"
docker compose -f "$COMPOSE_FILE" ps