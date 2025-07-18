#!/bin/bash
###
 # @Author: bianningtao ab2961513324@163.com
 # @Date: 2025-07-18 20:34:49
 # @LastEditors: bianningtao ab2961513324@163.com
 # @LastEditTime: 2025-07-18 22:15:34
 # @FilePath: /workflow-dsl-exporter/start.sh
 # @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
### 

echo "启动工作流DSL导出器..."

# 清理并重新创建后端虚拟环境
echo "正在清理并重新创建后端虚拟环境..."
cd backend

# 删除现有的虚拟环境
if [ -d "venv" ]; then
    echo "删除现有虚拟环境..."
    rm -rf venv
fi

# 尝试使用系统默认Python创建虚拟环境
echo "创建新的虚拟环境..."
if command -v python3 &> /dev/null; then
    python3 -m venv venv
elif command -v python &> /dev/null; then
    python -m venv venv
else
    echo "错误：未找到Python解释器"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 更新pip
echo "更新pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 启动后端服务
echo "正在启动后端服务..."
python app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 启动前端服务
echo "正在启动前端服务..."
cd ../frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!

echo "后端服务运行在: http://localhost:5000"
echo "前端服务运行在: http://localhost:3000"
echo "按 Ctrl+C 停止所有服务"

# 等待中断信号
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
wait 