#!/usr/bin/env python3
"""
ML/NLP服务 - Flask API
用于评论质量和相关性评估的机器学习服务
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模拟的ML模型类
class ReviewAssessmentModel:
    """
    评论评估模型类
    这里使用简单的规则来模拟ML模型的行为
    在实际实现中，这里应该加载训练好的ML/NLP模型
    """
    
    def __init__(self):
        self.quality_keywords = {
            'positive': ['好', '棒', '优秀', '推荐', '满意', '喜欢', '美味', '舒适'],
            'negative': ['差', '糟糕', '失望', '不好', '难吃', '脏', '吵'],
            'spam': ['www.', 'http', '优惠', '折扣', '广告', '推广'],
            'irrelevant': ['手机', '电脑', '汽车', '房子', '股票', '投资'],
            'rant_without_visit': ['没去过', '听说', '据说', 'never been', 'heard that']
        }
    
    def assess_review(self, text, metadata=None):
        """
        评估评论质量和相关性
        
        Args:
            text (str): 评论文本
            metadata (dict): 可选的元数据
            
        Returns:
            dict: 评估结果
        """
        text_lower = text.lower()
        
        # 计算质量评分
        quality_score = self._calculate_quality_score(text_lower)
        
        # 计算相关性评分
        relevancy_score = self._calculate_relevancy_score(text_lower)
        
        # 检测政策违规
        policy_violations = self._detect_policy_violations(text_lower)
        
        return {
            'quality_score': quality_score,
            'relevancy_score': relevancy_score,
            'policy_violations': policy_violations,
            'metadata': {
                'text_length': len(text),
                'processed_at': datetime.now().isoformat(),
                'model_version': '1.0.0'
            }
        }
    
    def _calculate_quality_score(self, text):
        """计算质量评分"""
        score = 0.7  # 基础分数
        
        # 正面词汇加分
        positive_count = sum(1 for word in self.quality_keywords['positive'] if word in text)
        score += positive_count * 0.05
        
        # 负面词汇减分
        negative_count = sum(1 for word in self.quality_keywords['negative'] if word in text)
        score -= negative_count * 0.1
        
        # 垃圾内容减分
        spam_count = sum(1 for word in self.quality_keywords['spam'] if word in text)
        score -= spam_count * 0.2
        
        # 长度因子
        if len(text) < 10:
            score -= 0.2
        elif len(text) > 100:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_relevancy_score(self, text):
        """计算相关性评分"""
        score = 0.8  # 基础分数
        
        # 无关内容减分
        irrelevant_count = sum(1 for word in self.quality_keywords['irrelevant'] if word in text)
        score -= irrelevant_count * 0.3
        
        return max(0.0, min(1.0, score))
    
    def _detect_policy_violations(self, text):
        """检测政策违规"""
        violations = {
            'advertisement': False,
            'irrelevant_content': False,
            'rant_without_visit': False
        }
        
        # 检测广告
        if any(word in text for word in self.quality_keywords['spam']):
            violations['advertisement'] = True
        
        # 检测无关内容
        if any(word in text for word in self.quality_keywords['irrelevant']):
            violations['irrelevant_content'] = True
        
        # 检测未访问抱怨
        if any(word in text for word in self.quality_keywords['rant_without_visit']):
            violations['rant_without_visit'] = True
        
        return violations

# 初始化模型
model = ReviewAssessmentModel()

@app.route('/ml-api/predict', methods=['POST'])
def predict():
    """
    评论评估API端点
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided'
            }), 400
        
        text = data.get('text', '').strip()
        metadata = data.get('metadata', {})
        
        if not text:
            return jsonify({
                'error': 'Text field is required'
            }), 400
        
        logger.info(f"Processing review: {text[:50]}...")
        
        # 调用模型进行评估
        result = model.assess_review(text, metadata)
        
        logger.info(f"Assessment completed: quality={result['quality_score']:.2f}, relevancy={result['relevancy_score']:.2f}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/ml-api/health', methods=['GET'])
def health():
    """
    健康检查端点
    """
    return jsonify({
        'status': 'healthy',
        'service': 'ML/NLP Review Assessment Service',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/ml-api/model-info', methods=['GET'])
def model_info():
    """
    模型信息端点
    """
    return jsonify({
        'model_name': 'Review Assessment Model',
        'model_version': '1.0.0',
        'model_type': 'Rule-based (Demo)',
        'supported_languages': ['zh-CN', 'en'],
        'features': [
            'Quality scoring',
            'Relevancy assessment', 
            'Policy violation detection'
        ],
        'policies': [
            'No Advertisement',
            'No Irrelevant Content',
            'No Rant Without Visit'
        ]
    })

if __name__ == '__main__':
    # 开发环境配置
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting ML/NLP service on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

