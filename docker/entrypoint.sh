#!/bin/bash
set -e

echo "=========================================="
echo "Dify Workflow DSL Exporter 启动中..."
echo "=========================================="

# 等待 MySQL 就绪
echo "等待 MySQL 数据库就绪..."
until mysqladmin ping -h"${CONFIG_DB_HOST}" -P"${CONFIG_DB_PORT}" -u"${CONFIG_DB_USERNAME}" -p"${CONFIG_DB_PASSWORD}" --silent; do
    echo "MySQL 未就绪，等待中..."
    sleep 2
done
echo "✓ MySQL 已就绪"

# 数据库已通过docker-entrypoint-initdb.d中的SQL文件初始化
echo "✓ 数据库已通过SQL文件初始化"
cd /app/backend

# 启动 nginx
echo "启动 Nginx..."
nginx -g 'daemon on;'
echo "✓ Nginx 已启动"

# 启动后端服务 (使用 gunicorn 生产环境服务器)
echo "启动后端服务..."
echo "监听端口: ${FLASK_PORT:-5001}"
echo "Workers: ${GUNICORN_WORKERS:-4}"

# 切换到backend目录并设置Python路径
export PYTHONPATH=/app/backend:$PYTHONPATH

exec gunicorn \
    --chdir /app/backend \
    --bind 0.0.0.0:${FLASK_PORT:-5001} \
    --workers ${GUNICORN_WORKERS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level ${LOG_LEVEL:-info} \
    --worker-class sync \
    "app:app"

