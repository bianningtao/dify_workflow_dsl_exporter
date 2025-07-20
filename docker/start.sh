#!/bin/bash
###
 # @Author: bianningtao ab2961513324@163.com
 # @Date: 2025-07-20 17:58:23
 # @LastEditors: bianningtao ab2961513324@163.com
 # @LastEditTime: 2025-07-20 19:49:59
 # @FilePath: /workflow-dsl-exporter/docker/start.sh
 # @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
### 

# 启动脚本 - Workflow DSL Exporter v0.1.0

set -e

echo "Starting Workflow DSL Exporter v0.1.0..."

# 创建必要的目录
mkdir -p /app/logs /app/data

# 设置权限
chmod 755 /app/frontend/dist

# 启动nginx
echo "Starting nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

# 等待nginx启动
sleep 2

# 启动Flask应用
echo "Starting Flask backend..."
cd /app/backend
python app.py &
FLASK_PID=$!

# 等待Flask启动
sleep 4

echo "Application started successfully!"
echo "Frontend: http://localhost"
echo "Backend API: http://localhost/api"
echo "Health check: http://localhost/health"

# 等待任一进程退出
wait -n

# 如果任一进程退出，则终止所有进程
echo "Shutting down..."
kill $NGINX_PID $FLASK_PID 2>/dev/null || true
wait 