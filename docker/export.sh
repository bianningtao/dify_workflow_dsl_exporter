#!/bin/bash
# Docker镜像导出脚本

set -e

EXPORT_DIR="${HOME}/dify-workflow-export"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "Docker 镜像导出工具"
echo "=========================================="

# 创建导出目录
echo "创建导出目录: ${EXPORT_DIR}"
mkdir -p "${EXPORT_DIR}"

# 导出应用镜像
echo ""
echo "[1/4] 导出应用镜像..."
docker save docker-app:latest | gzip > "${EXPORT_DIR}/dify-workflow-app.tar.gz"
echo "✓ 应用镜像已导出: dify-workflow-app.tar.gz"

# 导出MySQL镜像
echo ""
echo "[2/4] 导出MySQL镜像..."
docker save mysql:8.0 | gzip > "${EXPORT_DIR}/mysql-8.0.tar.gz"
echo "✓ MySQL镜像已导出: mysql-8.0.tar.gz"

# 复制部署文件
echo ""
echo "[3/4] 复制部署文件..."
rm -rf "${EXPORT_DIR}/docker"
cp -r "$(dirname "$0")" "${EXPORT_DIR}/"
cp "${EXPORT_DIR}/docker/env.example" "${EXPORT_DIR}/docker/.env"
echo "✓ 部署文件已复制"

# 创建部署说明
echo ""
echo "[4/4] 创建部署说明..."
cat > "${EXPORT_DIR}/DEPLOY.txt" << 'EOF'
==========================================
Dify Workflow DSL Exporter 部署说明
==========================================

1. 上传文件到目标服务器
   scp -r dify-workflow-export/ user@server:/path/to/destination/

2. 在目标服务器执行以下命令:

   # 导入镜像
   cd dify-workflow-export
   docker load < dify-workflow-app.tar.gz
   docker load < mysql-8.0.tar.gz

   # 配置环境变量
   cd docker
   vim .env  # 修改数据库密码和JWT密钥

   # 启动服务
   docker compose up -d

   # 查看状态
   docker compose ps
   docker compose logs -f

3. 访问应用
   浏览器打开: http://服务器IP
   默认账号: admin@example.com
   默认密码: admin123456 (首次登录后请立即修改)

4. 管理命令
   docker compose down      # 停止服务
   docker compose restart   # 重启服务
   docker compose logs -f   # 查看日志

==========================================
EOF
echo "✓ 部署说明已创建: DEPLOY.txt"

# 打包(可选)
echo ""
read -p "是否打包为tar.gz文件? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在打包..."
    cd "${HOME}"
    tar -czf "dify-workflow-export_${TIMESTAMP}.tar.gz" -C "${EXPORT_DIR}/.." "$(basename ${EXPORT_DIR})"
    echo "✓ 已打包: ${HOME}/dify-workflow-export_${TIMESTAMP}.tar.gz"
fi

# 显示文件大小
echo ""
echo "=========================================="
echo "导出完成!"
echo "=========================================="
echo "导出位置: ${EXPORT_DIR}"
echo ""
echo "文件列表:"
ls -lh "${EXPORT_DIR}" | grep -v "^d" | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "总大小: $(du -sh ${EXPORT_DIR} | awk '{print $1}')"
echo ""
echo "请查看 ${EXPORT_DIR}/DEPLOY.txt 了解部署步骤"
echo "=========================================="

