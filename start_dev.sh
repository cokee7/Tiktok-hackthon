#!/bin/bash

# Hackathon Review System - 开发环境启动脚本
# 用于快速启动所有服务

echo "🚀 启动 Hackathon Review System 开发环境..."

# 检查是否在项目根目录
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 停止可能已经运行的服务
echo "🛑 停止现有服务..."
pkill -f "php -S.*:8000" 2>/dev/null || true
pkill -f "python.*http.server.*3000" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

sleep 2

# 启动PHP后端服务
echo "🔧 启动PHP后端服务 (端口: 8000)..."
cd backend
php -S 0.0.0.0:8000 -t public/ > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ PHP后端服务启动成功"
else
    echo "❌ PHP后端服务启动失败，请检查日志: logs/backend.log"
    exit 1
fi

# 启动前端服务
echo "🎨 启动前端服务 (端口: 3000)..."
cd frontend
python3 -m http.server 3000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# 等待前端启动
sleep 2

# 检查前端是否启动成功
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 前端服务启动成功"
else
    echo "❌ 前端服务启动失败，请检查日志: logs/frontend.log"
fi

# 启动ML服务（可选）
echo "🤖 启动ML/NLP服务 (端口: 5000)..."
cd ml_service

# 检查Python依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  警告: Flask未安装，正在安装..."
    pip3 install Flask Flask-CORS
fi

python3 app.py > ../logs/ml_service.log 2>&1 &
ML_PID=$!
cd ..

# 等待ML服务启动
sleep 3

# 检查ML服务是否启动成功
if curl -s http://localhost:5000/ml-api/health > /dev/null; then
    echo "✅ ML/NLP服务启动成功"
else
    echo "⚠️  ML/NLP服务启动失败，将使用PHP后端的模拟数据"
fi

# 保存进程ID
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid
echo $ML_PID > logs/ml_service.pid

echo ""
echo "🎉 所有服务启动完成！"
echo ""
echo "📋 服务信息:"
echo "   前端应用:     http://localhost:3000"
echo "   PHP后端API:   http://localhost:8000"
echo "   ML服务API:    http://localhost:5000"
echo ""
echo "📝 日志文件:"
echo "   后端日志:     logs/backend.log"
echo "   前端日志:     logs/frontend.log"
echo "   ML服务日志:   logs/ml_service.log"
echo ""
echo "🛑 停止服务:"
echo "   运行: ./stop_dev.sh"
echo "   或手动: kill $BACKEND_PID $FRONTEND_PID $ML_PID"
echo ""
echo "🔍 测试API:"
echo "   curl http://localhost:8000/api/health"
echo "   curl http://localhost:5000/ml-api/health"
echo ""

# 等待用户输入以保持脚本运行
echo "按 Ctrl+C 停止所有服务，或运行 ./stop_dev.sh"

# 创建停止脚本
cat > stop_dev.sh << 'EOF'
#!/bin/bash

echo "🛑 停止 Hackathon Review System 服务..."

# 从PID文件读取进程ID并停止
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo "✅ PHP后端服务已停止"
    rm -f logs/backend.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    kill $FRONTEND_PID 2>/dev/null && echo "✅ 前端服务已停止"
    rm -f logs/frontend.pid
fi

if [ -f "logs/ml_service.pid" ]; then
    ML_PID=$(cat logs/ml_service.pid)
    kill $ML_PID 2>/dev/null && echo "✅ ML服务已停止"
    rm -f logs/ml_service.pid
fi

# 强制停止可能残留的进程
pkill -f "php -S.*:8000" 2>/dev/null || true
pkill -f "python.*http.server.*3000" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

echo "🎉 所有服务已停止"
EOF

chmod +x stop_dev.sh

# 等待中断信号
trap 'echo ""; echo "🛑 收到停止信号，正在关闭服务..."; ./stop_dev.sh; exit 0' INT

# 保持脚本运行
while true; do
    sleep 1
done

