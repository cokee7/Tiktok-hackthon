# PHP 后端 API

这是Hackathon Review System的PHP后端API服务，负责处理前端请求并与ML/NLP服务进行交互。

## 目录结构

```
backend/
├── public/
│   └── index.php          # API入口文件
├── src/
│   ├── Config.php         # 配置文件
│   ├── Router.php         # 路由处理
│   └── ReviewService.php  # 评论服务业务逻辑
├── logs/                  # 日志文件目录（自动创建）
├── composer.json          # Composer配置
└── README.md             # 本文件
```

## 快速开始

### 1. 环境要求

- PHP 7.4 或更高版本
- 可选：Composer（用于依赖管理）

### 2. 启动开发服务器

```bash
# 进入backend目录
cd backend

# 使用PHP内置服务器启动（推荐用于开发）
php -S 0.0.0.0:8000 -t public/

# 或者使用Composer脚本
composer run serve
```

服务器将在 `http://localhost:8000` 启动。

### 3. 配置ML/NLP服务

编辑 `src/Config.php` 文件，修改ML服务的地址：

```php
const ML_SERVICE_BASE_URL = 'http://localhost:5000'; // 修改为实际的ML服务地址
```

## API 接口

### 1. 健康检查

- **URL**: `/api/health`
- **方法**: `GET`
- **响应**:
```json
{
    "status": "success",
    "message": "API服务运行正常",
    "timestamp": "2024-01-01 12:00:00"
}
```

### 2. 评论评估

- **URL**: `/api/evaluate-review`
- **方法**: `POST`
- **请求体**:
```json
{
    "review_text": "用户输入的评论文本",
    "location_metadata": {
        "location_id": "可选的地点ID",
        "location_name": "可选的地点名称"
    }
}
```

- **响应**:
```json
{
    "status": "success",
    "data": {
        "quality_score": 0.85,
        "relevancy_score": 0.92,
        "violations": [
            {
                "policy_type": "No Advertisement",
                "detected": false
            },
            {
                "policy_type": "No Irrelevant Content", 
                "detected": false
            },
            {
                "policy_type": "No Rant Without Visit",
                "detected": true
            }
        ],
        "summary": "评论可能存在未访问地点的抱怨"
    },
    "message": "评论评估成功",
    "timestamp": "2024-01-01 12:00:00"
}
```

## 功能特性

### 1. 模拟数据支持

当ML/NLP服务不可用时，系统会自动返回基于简单规则的模拟数据，确保前端开发不受阻。

### 2. 错误处理

- 完整的异常处理机制
- 详细的错误日志记录
- 友好的错误响应格式

### 3. CORS支持

已配置跨域资源共享，支持前端应用的API调用。

### 4. 日志记录

所有请求和错误都会记录到 `logs/app.log` 文件中。

## 开发指南

### 添加新的API端点

1. 在 `public/index.php` 中添加路由：
```php
$router->addRoute('POST', '/api/new-endpoint', function() {
    // 处理逻辑
    return ['status' => 'success', 'data' => []];
});
```

2. 如需复杂业务逻辑，在 `src/` 目录下创建新的服务类。

### 修改配置

编辑 `src/Config.php` 文件来修改：
- ML服务地址
- 超时设置
- 日志配置
- 其他系统参数

### 部署到生产环境

1. 使用Apache或Nginx作为Web服务器
2. 配置PHP-FPM
3. 设置适当的文件权限
4. 配置日志轮转

## 故障排除

### 1. CORS错误

确保 `public/index.php` 中的CORS头设置正确。

### 2. ML服务连接失败

检查 `src/Config.php` 中的ML服务地址配置，确保ML服务正在运行。

### 3. 权限问题

确保Web服务器对 `logs/` 目录有写入权限。

## 下一步开发

1. **实现ML/NLP服务**: 开发Python ML服务来替换模拟数据
2. **数据库集成**: 添加数据库支持来存储评估历史
3. **用户认证**: 实现API密钥或JWT认证
4. **缓存机制**: 添加Redis或文件缓存来提高性能
5. **API文档**: 使用Swagger生成完整的API文档

