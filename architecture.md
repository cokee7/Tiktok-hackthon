# 项目架构设计

## 1. 概述

本项目旨在为Hackathon提供一个基于PHP和JavaScript的Web应用代码框架，用于评估Google地点评论的质量和相关性。整个系统将采用前后端分离的架构，并通过RESTful API进行通信。ML/NLP模型将作为独立的后端服务，通过API与PHP后端进行交互。

## 2. 技术栈

- **前端**: HTML5, CSS3, JavaScript (原生JS或轻量级框架如jQuery)
- **后端**: PHP (推荐使用PHP 7.4+)
- **ML/NLP服务**: Python (HuggingFace Transformers, scikit-learn, TensorFlow/PyTorch等)
- **API通信**: RESTful API (JSON格式)

## 3. 架构图

```mermaid
graph TD
    A[用户浏览器] -->|HTTP/HTTPS| B(前端 Web 应用)
    B -->|RESTful API (JSON)| C(PHP 后端)
    C -->|RESTful API (JSON)| D(ML/NLP 服务)
    D -->|数据处理/模型推理| E[ML/NLP 模型/数据]
    E --> D
    D --> C
    C --> B
```

## 4. 模块划分与职责

### 4.1 前端 Web 应用 (JavaScript/HTML/CSS)

- **职责**: 提供用户界面，接收用户输入（如评论文本），展示ML/NLP服务的评估结果。
- **主要功能**: 
    - 评论输入表单。
    - 结果展示区域（显示评论质量、相关性、违反政策等信息）。
    - 与PHP后端进行异步通信（AJAX/Fetch API）。
- **文件结构建议**:
    ```
    ./frontend/
    ├── index.html          # 主页面
    ├── css/
    │   └── style.css       # 样式文件
    └── js/
        └── main.js         # 主要JavaScript逻辑，处理UI交互和API请求
    ```

### 4.2 PHP 后端

- **职责**: 作为前端和ML/NLP服务之间的桥梁，处理前端请求，调用ML/NLP服务，并将结果返回给前端。可以包含简单的路由和请求验证逻辑。
- **主要功能**: 
    - 接收前端的评论提交请求。
    - 将评论数据转发给ML/NLP服务。
    - 接收ML/NLP服务的处理结果。
    - 将结果格式化后返回给前端。
    - 错误处理和日志记录。
- **文件结构建议**:
    ```
    ./backend/
    ├── public/
    │   └── index.php       # 入口文件，处理所有请求
    ├── src/
    │   ├── Config.php      # 配置文件（ML/NLP服务API地址等）
    │   ├── Router.php      # 简单的路由处理
    │   └── ReviewService.php # 业务逻辑，负责调用ML/NLP服务
    └── composer.json       # (可选) 如果使用Composer管理依赖
    ```

### 4.3 ML/NLP 服务 (Python)

- **职责**: 实现评论质量和相关性评估的核心逻辑，包括数据预处理、特征工程、模型推理和政策执行。
- **主要功能**: 
    - 接收来自PHP后端的评论文本。
    - 对文本进行NLP处理（情感分析、主题建模、关键词提取等）。
    - 结合元数据特征（如果提供）。
    - 使用训练好的ML/NLP模型进行分类和相关性评分。
    - 根据预定义政策判断评论是否违规。
    - 返回评估结果（JSON格式）。
- **文件结构建议**:
    ```
    ./ml_service/
    ├── app.py              # Flask/FastAPI应用入口，提供API接口
    ├── models/             # 存放ML/NLP模型文件
    │   └── ...
    ├── utils/              # 工具函数，如数据预处理、特征提取
    │   └── nlp_processor.py
    └── requirements.txt    # Python依赖
    ```

## 5. API 接口设计 (示例)

### 5.1 前端 -> PHP 后端

- **Endpoint**: `/api/evaluate-review`
- **Method**: `POST`
- **Request Body (JSON)**:
    ```json
    {
        "review_text": "用户输入的评论文本",
        "location_metadata": { /* 可选：地点元数据 */ }
    }
    ```
- **Response Body (JSON)**:
    ```json
    {
        "status": "success",
        "data": {
            "quality_score": 0.85,          # 质量评分
            "relevancy_score": 0.92,        # 相关性评分
            "violations": [                # 违反政策列表
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
        "message": "评论评估成功"
    }
    ```

### 5.2 PHP 后端 -> ML/NLP 服务

- **Endpoint**: `/ml-api/predict` (ML/NLP服务内部API)
- **Method**: `POST`
- **Request Body (JSON)**:
    ```json
    {
        "text": "用户输入的评论文本",
        "metadata": { /* 可选：地点元数据 */ }
    }
    ```
- **Response Body (JSON)**:
    ```json
    {
        "quality_score": 0.85,
        "relevancy_score": 0.92,
        "policy_violations": {
            "advertisement": false,
            "irrelevant_content": false,
            "rant_without_visit": true
        }
    }
    ```

## 6. 开发流程建议

1.  **ML/NLP服务开发**: 优先开发和测试ML/NLP服务，确保其能独立接收评论并返回评估结果。
2.  **PHP后端开发**: 开发PHP后端，实现与ML/NLP服务的集成，并提供前端所需的API接口。
3.  **前端开发**: 开发前端界面，通过AJAX/Fetch API与PHP后端进行交互，展示结果。
4.  **集成测试**: 确保前后端以及ML/NLP服务之间的通信顺畅，功能完整。

## 7. 部署建议

- **开发环境**: 可以使用PHP内置Web服务器或Apache/Nginx配合PHP-FPM，ML/NLP服务可以使用Flask/FastAPI自带的开发服务器。
- **生产环境**: 建议使用Nginx/Apache作为反向代理，PHP-FPM处理PHP请求，Gunicorn/uWSGI配合Nginx处理Python ML/NLP服务。

