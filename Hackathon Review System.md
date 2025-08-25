# Hackathon Review System

基于机器学习和自然语言处理的Google地点评论质量与相关性评估系统。

## 项目概述

本项目是为Hackathon竞赛开发的评论质量评估系统，旨在通过ML/NLP技术自动评估Google地点评论的质量和相关性，并检测违反平台政策的内容。

### 主要功能

- **评论质量评估**: 检测垃圾信息、广告和低质量内容
- **相关性评估**: 判断评论内容是否与地点相关
- **政策违规检测**: 自动标记违反以下政策的评论：
  - 无广告内容
  - 无无关内容
  - 无未访问地点的抱怨

### 技术栈

- **前端**: HTML5, CSS3, JavaScript (原生)
- **后端**: PHP 8.1+
- **ML/NLP服务**: Python, Flask
- **通信**: RESTful API (JSON)

## 项目结构

```
hackathon-review-system/
├── README.md                 # 项目主文档
├── architecture.md           # 架构设计文档
├── test_results.md          # 测试结果报告
├── frontend/                # 前端Web应用
│   ├── index.html           # 主页面
│   ├── css/
│   │   └── style.css        # 样式文件
│   ├── js/
│   │   └── main.js          # 主要JavaScript逻辑
│   ├── assets/              # 静态资源
│   └── README.md            # 前端文档
├── backend/                 # PHP后端API
│   ├── public/
│   │   └── index.php        # API入口文件
│   ├── src/
│   │   ├── Config.php       # 配置文件
│   │   ├── Router.php       # 路由处理
│   │   └── ReviewService.php # 业务逻辑
│   ├── composer.json        # Composer配置
│   └── README.md            # 后端文档
└── ml_service/              # ML/NLP服务
    ├── app.py               # Flask API应用
    ├── requirements.txt     # Python依赖
    ├── models/              # ML模型文件
    ├── utils/
    │   └── nlp_processor.py # NLP处理工具
    └── README.md            # ML服务文档
```

## 快速开始

### 1. 环境要求

- **PHP**: 7.4+ (推荐 8.1+)
- **Python**: 3.8+ (用于ML服务)
- **Web服务器**: Apache/Nginx 或 PHP内置服务器
- **浏览器**: 现代浏览器 (Chrome 60+, Firefox 55+, Safari 12+, Edge 79+)

### 2. 安装和启动

#### 启动PHP后端

```bash
cd backend
php -S 0.0.0.0:8000 -t public/
```

#### 启动前端服务

```bash
cd frontend
python3 -m http.server 3000
# 或使用其他静态文件服务器
```

#### 启动ML服务（可选）

```bash
cd ml_service
pip install Flask Flask-CORS
python app.py
```

### 3. 访问应用

- **前端应用**: http://localhost:3000
- **PHP后端API**: http://localhost:8000
- **ML服务API**: http://localhost:5000

## 使用指南

### 1. 基本使用

1. 在浏览器中打开前端应用
2. 在"评论内容"文本框中输入要评估的评论
3. 可选：填写地点名称和地点ID
4. 点击"开始评估"按钮
5. 查看评估结果，包括质量评分、相关性评分和政策违规检测

### 2. API使用

#### 评论评估API

```bash
curl -X POST http://localhost:8000/api/evaluate-review \
  -H "Content-Type: application/json" \
  -d '{
    "review_text": "这家餐厅的服务很好，食物也很美味。",
    "location_metadata": {
      "location_name": "测试餐厅"
    }
  }'
```

#### 健康检查API

```bash
curl http://localhost:8000/api/health
```

## 开发指南

### 1. 前端开发

前端使用原生JavaScript开发，主要文件：

- `index.html`: 页面结构和布局
- `css/style.css`: 样式和响应式设计
- `js/main.js`: 交互逻辑和API通信

详细信息请参考 [frontend/README.md](frontend/README.md)

### 2. 后端开发

PHP后端提供RESTful API，主要组件：

- `Router.php`: 路由处理和请求分发
- `ReviewService.php`: 业务逻辑和ML服务调用
- `Config.php`: 配置管理和日志记录

详细信息请参考 [backend/README.md](backend/README.md)

### 3. ML服务开发

Python ML服务负责核心评估逻辑：

- `app.py`: Flask API应用
- `utils/nlp_processor.py`: NLP处理工具
- `models/`: ML模型文件存储

详细信息请参考 [ml_service/README.md](ml_service/README.md)

## 架构设计

系统采用前后端分离的微服务架构：

```
[前端Web应用] ←→ [PHP后端API] ←→ [ML/NLP服务]
```

- **前端**: 负责用户界面和交互
- **PHP后端**: 处理业务逻辑和API路由
- **ML服务**: 执行机器学习推理和NLP处理

详细架构说明请参考 [architecture.md](architecture.md)

## 测试

### 1. 功能测试

项目包含完整的集成测试，验证：

- 前后端API通信
- 用户界面交互
- 评估结果展示
- 错误处理机制

测试结果请参考 [test_results.md](test_results.md)

### 2. 手动测试

可以使用以下测试用例：

**正常评论**:
```
这家餐厅的服务很好，食物也很美味。环境很舒适，推荐大家来试试。
```

**包含广告的评论**:
```
这家店还不错，大家可以访问 www.example.com 获取更多优惠信息！
```

**无关内容评论**:
```
我最近买了一部新手机，这个地方太吵了，影响我使用手机。
```

## 部署

### 1. 开发环境部署

使用内置服务器快速启动：

```bash
# 启动所有服务
./start_dev.sh  # 如果有启动脚本

# 或手动启动各个服务
cd backend && php -S 0.0.0.0:8000 -t public/ &
cd frontend && python3 -m http.server 3000 &
cd ml_service && python app.py &
```

### 2. 生产环境部署

#### 使用Apache/Nginx

1. 配置Web服务器指向 `frontend/` 目录
2. 配置PHP-FPM处理 `backend/` 的请求
3. 使用Gunicorn部署ML服务

#### 使用Docker

```dockerfile
# 示例Dockerfile
FROM php:8.1-apache
COPY backend/ /var/www/html/
COPY frontend/ /var/www/html/frontend/
# ... 其他配置
```

### 3. 云服务部署

- **前端**: 可部署到GitHub Pages、Netlify、Vercel等
- **后端**: 可部署到AWS EC2、Google Cloud、Azure等
- **ML服务**: 推荐使用容器化部署到云平台

## 扩展开发

### 1. 添加新功能

#### 前端新功能
1. 在 `js/main.js` 中添加新的方法
2. 在 `index.html` 中添加相应的UI元素
3. 在 `css/style.css` 中添加样式

#### 后端新API
1. 在 `src/Router.php` 中添加新路由
2. 在相应的服务类中实现业务逻辑
3. 更新API文档

#### ML新模型
1. 在 `ml_service/models/` 中添加模型文件
2. 在 `app.py` 中集成新模型
3. 更新API接口

### 2. 性能优化

- **前端**: 代码压缩、图片优化、CDN加速
- **后端**: 数据库优化、缓存机制、负载均衡
- **ML服务**: 模型量化、批处理、GPU加速

### 3. 安全加固

- **输入验证**: 严格验证所有用户输入
- **API认证**: 添加API密钥或JWT认证
- **HTTPS**: 在生产环境中启用HTTPS
- **速率限制**: 防止API滥用

## 故障排除

### 1. 常见问题

**CORS错误**:
- 确保PHP后端正确设置CORS头
- 检查前端API地址配置

**API连接失败**:
- 确认各服务正在运行
- 检查端口配置和防火墙设置

**评估结果异常**:
- 检查ML服务日志
- 验证输入数据格式

### 2. 调试技巧

- 使用浏览器开发者工具查看网络请求
- 检查PHP和Python服务的日志文件
- 使用API测试工具（如Postman）验证接口

## 贡献指南

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/new-feature`)
3. 提交更改 (`git commit -am 'Add new feature'`)
4. 推送到分支 (`git push origin feature/new-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详情请参考LICENSE文件。

## 联系方式

- 项目维护者: Hackathon Team
- 邮箱: team@hackathon.example.com
- 项目地址: https://github.com/hackathon/review-system

## 致谢

感谢以下开源项目和资源：

- [HuggingFace Transformers](https://huggingface.co/transformers/)
- [Flask](https://flask.palletsprojects.com/)
- [Font Awesome](https://fontawesome.com/)
- Google Maps API文档和示例

---

**注意**: 这是一个Hackathon项目的代码框架，当前使用模拟数据进行演示。在实际部署中，需要集成真实的ML/NLP模型和完整的数据处理流程。

