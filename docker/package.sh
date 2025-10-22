#!/bin/bash
# Docker镜像打包脚本 - 支持多架构
# 使用方法: ./package.sh [arm64|amd64|both]

set -e

PLATFORM="${1:-amd64}"  # 默认构建amd64
EXPORT_DIR="${HOME}/dify-workflow-package"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=========================================="
echo "Docker 镜像打包工具 (多架构支持)"
echo "=========================================="
echo "目标平台: ${PLATFORM}"
echo "项目路径: ${PROJECT_ROOT}"
echo ""

# 创建导出目录
echo "[1/6] 创建打包目录..."
rm -rf "${EXPORT_DIR}"
mkdir -p "${EXPORT_DIR}"
echo "✓ 打包目录: ${EXPORT_DIR}"

# 构建指定架构的镜像
build_image() {
    local arch=$1
    local platform=""
    
    case $arch in
        amd64)
            platform="linux/amd64"
            ;;
        arm64)
            platform="linux/arm64"
            ;;
        *)
            echo "❌ 不支持的架构: $arch"
            exit 1
            ;;
    esac
    
    echo ""
    echo "[2/6] 构建 ${arch} 架构镜像..."
    echo "平台: ${platform}"
    
    cd "${PROJECT_ROOT}"
    
    # 根据架构选择构建方式
    if [[ $arch == "arm64" ]] && [[ $(uname -m) == "arm64" ]]; then
        # 在ARM Mac上构建ARM镜像,使用传统方式
        echo "使用本地构建(当前架构匹配)..."
        DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker build \
            --file docker/Dockerfile \
            --tag dify-workflow-app:${arch} \
            .
    elif [[ $arch == "amd64" ]] && [[ $(uname -m) == "x86_64" ]]; then
        # 在x86 Mac/Linux上构建AMD镜像,使用传统方式
        echo "使用本地构建(当前架构匹配)..."
        DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker build \
            --file docker/Dockerfile \
            --tag dify-workflow-app:${arch} \
            .
    else
        # 跨架构构建,使用buildx
        echo "使用跨架构构建..."
        
        # 检查是否已有本地镜像,尝试使用本地缓存
        if docker images | grep -q "docker-app.*latest"; then
            echo "检测到本地镜像,将使用本地缓存..."
            # 先用本地镜像构建,再重新打标签
            docker tag docker-app:latest dify-workflow-app:${arch}
            echo "⚠️  注意: 使用本地镜像重新打标签,可能不是目标架构"
            echo "如需真正的 ${arch} 镜像,请在 ${arch} 机器上执行构建"
        else
            # 使用buildx跨架构构建
            docker buildx build \
                --platform ${platform} \
                --file docker/Dockerfile \
                --tag dify-workflow-app:${arch} \
                --load \
                .
        fi
    fi
    
    echo "✓ ${arch} 镜像构建完成"
}

# 导出镜像
export_images() {
    local arch=$1
    
    echo ""
    echo "[3/6] 导出 ${arch} 架构镜像..."
    
    # 导出应用镜像
    echo "  - 导出应用镜像..."
    docker save dify-workflow-app:${arch} | gzip > "${EXPORT_DIR}/dify-workflow-app-${arch}.tar.gz"
    echo "  ✓ dify-workflow-app-${arch}.tar.gz"
    
    # 导出MySQL镜像(拉取对应架构)
    echo "  - 拉取并导出MySQL镜像..."
    docker pull --platform linux/${arch} mysql:8.0
    docker tag mysql:8.0 mysql:8.0-${arch}
    docker save mysql:8.0-${arch} | gzip > "${EXPORT_DIR}/mysql-8.0-${arch}.tar.gz"
    echo "  ✓ mysql-8.0-${arch}.tar.gz"
}

# 复制部署文件
echo ""
echo "[4/6] 复制部署文件..."
cp -r "${PROJECT_ROOT}/docker" "${EXPORT_DIR}/"
cp "${EXPORT_DIR}/docker/env.example" "${EXPORT_DIR}/docker/.env"
echo "✓ 部署文件已复制"

# 根据参数构建对应架构
case $PLATFORM in
    amd64)
        build_image "amd64"
        export_images "amd64"
        ARCH_NOTE="AMD64 (x86_64)"
        ;;
    arm64)
        build_image "arm64"
        export_images "arm64"
        ARCH_NOTE="ARM64 (Apple Silicon / ARM服务器)"
        ;;
    both)
        build_image "amd64"
        export_images "amd64"
        build_image "arm64"
        export_images "arm64"
        ARCH_NOTE="AMD64 + ARM64 (双架构)"
        ;;
    *)
        echo "❌ 不支持的架构: ${PLATFORM}"
        echo "使用方法: ./package.sh [arm64|amd64|both]"
        exit 1
        ;;
esac

# 创建导入脚本
echo ""
echo "[5/6] 创建部署脚本..."

# 为每个架构创建导入脚本
if [[ $PLATFORM == "amd64" ]] || [[ $PLATFORM == "both" ]]; then
    cat > "${EXPORT_DIR}/import-amd64.sh" << 'EOF'
#!/bin/bash
# AMD64架构镜像导入脚本

set -e

echo "=========================================="
echo "导入 AMD64 (x86_64) 镜像"
echo "=========================================="

# 检查架构
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    echo "⚠️  警告: 当前系统架构是 $ARCH，但要导入AMD64镜像"
    read -p "是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "[1/3] 导入应用镜像..."
docker load < dify-workflow-app-amd64.tar.gz
docker tag dify-workflow-app:amd64 docker-app:latest

echo "[2/3] 导入MySQL镜像..."
docker load < mysql-8.0-amd64.tar.gz
docker tag mysql:8.0-amd64 mysql:8.0

echo "[3/3] 清理临时标签..."
docker rmi dify-workflow-app:amd64 mysql:8.0-amd64 2>/dev/null || true

echo ""
echo "=========================================="
echo "✓ 镜像导入完成!"
echo "=========================================="
echo "下一步:"
echo "  cd docker"
echo "  vim .env              # 修改配置"
echo "  docker compose up -d  # 启动服务"
echo "=========================================="
EOF
    chmod +x "${EXPORT_DIR}/import-amd64.sh"
fi

if [[ $PLATFORM == "arm64" ]] || [[ $PLATFORM == "both" ]]; then
    cat > "${EXPORT_DIR}/import-arm64.sh" << 'EOF'
#!/bin/bash
# ARM64架构镜像导入脚本

set -e

echo "=========================================="
echo "导入 ARM64 镜像"
echo "=========================================="

# 检查架构
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" ]] && [[ "$ARCH" != "arm64" ]]; then
    echo "⚠️  警告: 当前系统架构是 $ARCH，但要导入ARM64镜像"
    read -p "是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "[1/3] 导入应用镜像..."
docker load < dify-workflow-app-arm64.tar.gz
docker tag dify-workflow-app:arm64 docker-app:latest

echo "[2/3] 导入MySQL镜像..."
docker load < mysql-8.0-arm64.tar.gz
docker tag mysql:8.0-arm64 mysql:8.0

echo "[3/3] 清理临时标签..."
docker rmi dify-workflow-app:arm64 mysql:8.0-arm64 2>/dev/null || true

echo ""
echo "=========================================="
echo "✓ 镜像导入完成!"
echo "=========================================="
echo "下一步:"
echo "  cd docker"
echo "  vim .env              # 修改配置"
echo "  docker compose up -d  # 启动服务"
echo "=========================================="
EOF
    chmod +x "${EXPORT_DIR}/import-arm64.sh"
fi

# 创建部署说明
cat > "${EXPORT_DIR}/DEPLOY.txt" << EOF
==========================================
Dify Workflow DSL Exporter 部署说明
==========================================

本包支持架构: ${ARCH_NOTE}

【部署步骤】

1. 传输文件到目标服务器
   scp -r dify-workflow-package/ user@server:/opt/

2. 在目标服务器上执行

   a) 确认服务器架构:
      uname -m
      # x86_64 或 amd64  → 使用 import-amd64.sh
      # aarch64 或 arm64 → 使用 import-arm64.sh

   b) 导入对应架构的镜像:
      cd /opt/dify-workflow-package
      
      # AMD64服务器(x86_64)
      ./import-amd64.sh
      
      # 或 ARM64服务器
      ./import-arm64.sh

   c) 配置环境变量:
      cd docker
      vim .env
      # 必须修改:
      #   - MYSQL_ROOT_PASSWORD (数据库密码)
      #   - JWT_SECRET_KEY (JWT密钥)

   d) 启动服务:
      docker compose up -d

3. 访问应用
   浏览器打开: http://服务器IP
   默认账号: admin@example.com
   默认密码: admin123456
   ⚠️  首次登录后请立即修改密码!

【管理命令】

  docker compose ps           # 查看状态
  docker compose logs -f      # 查看日志
  docker compose restart      # 重启服务
  docker compose down         # 停止服务

【目录说明】

  docker/                     # 部署配置目录
  ├── docker-compose.yml      # Docker编排文件
  ├── .env                    # 环境变量配置
  ├── dify_workflow_config.sql # 数据库初始化脚本
  └── ...

  镜像文件:
  - dify-workflow-app-*.tar.gz  # 应用镜像
  - mysql-8.0-*.tar.gz          # MySQL镜像
  - import-*.sh                 # 导入脚本

【故障排查】

1. 容器无法启动
   docker compose logs app

2. 数据库连接失败
   检查 .env 中的密码配置

3. 端口被占用
   修改 .env 中的 APP_PORT 或 MYSQL_PORT

==========================================
EOF

echo "✓ 部署脚本和说明已创建"

# 打包
echo ""
echo "[6/6] 打包文件..."
cd "${HOME}"
TAR_NAME="dify-workflow-${PLATFORM}_${TIMESTAMP}.tar.gz"
tar -czf "${TAR_NAME}" -C "${EXPORT_DIR}/.." "$(basename ${EXPORT_DIR})"
echo "✓ 已打包: ${HOME}/${TAR_NAME}"

# 显示结果
echo ""
echo "=========================================="
echo "✓ 打包完成!"
echo "=========================================="
echo "架构: ${ARCH_NOTE}"
echo "打包文件: ${HOME}/${TAR_NAME}"
echo ""
echo "文件列表:"
ls -lh "${EXPORT_DIR}" | grep -E "\\.tar\\.gz|\\.sh|DEPLOY" | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "总大小: $(du -sh ${EXPORT_DIR} | awk '{print $1}')"
echo ""
echo "📦 部署包: ${HOME}/${TAR_NAME}"
echo "📋 查看部署说明: cat ${EXPORT_DIR}/DEPLOY.txt"
echo ""
echo "传输到服务器:"
echo "  scp ${TAR_NAME} user@server:/opt/"
echo "=========================================="

