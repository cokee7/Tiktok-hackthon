"""
NLP处理工具模块
包含文本预处理、特征提取等功能
"""

import re
import string
from typing import List, Dict, Any

class NLPProcessor:
    """
    NLP文本处理器
    提供文本预处理、特征提取等功能
    """
    
    def __init__(self):
        # 停用词列表（简化版）
        self.stop_words = {
            'zh': ['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'],
            'en': ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should']
        }
        
        # 情感词典（简化版）
        self.sentiment_words = {
            'positive': {
                'zh': ['好', '棒', '优秀', '满意', '喜欢', '推荐', '美味', '舒适', '干净', '友好', '专业', '快速', '便宜', '值得'],
                'en': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'perfect', 'love', 'like', 'recommend', 'satisfied']
            },
            'negative': {
                'zh': ['差', '糟糕', '失望', '不好', '难吃', '脏', '吵', '贵', '慢', '态度差', '服务差', '质量差'],
                'en': ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor', 'worst', 'hate', 'dislike', 'expensive', 'slow', 'dirty']
            }
        }
    
    def preprocess_text(self, text: str) -> str:
        """
        文本预处理
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 预处理后的文本
        """
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（保留中文、英文、数字和基本标点）
        text = re.sub(r'[^\u4e00-\u9fff\w\s.,!?;:]', '', text)
        
        # 去除首尾空格
        text = text.strip()
        
        return text
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        提取关键词（简单版本）
        
        Args:
            text (str): 输入文本
            top_k (int): 返回前k个关键词
            
        Returns:
            List[str]: 关键词列表
        """
        # 预处理文本
        processed_text = self.preprocess_text(text)
        
        # 简单分词（按空格和标点分割）
        words = re.findall(r'\b\w+\b', processed_text)
        
        # 过滤停用词
        filtered_words = []
        for word in words:
            if len(word) > 1:  # 过滤单字符
                # 检查是否为停用词
                is_stopword = (
                    word in self.stop_words['zh'] or 
                    word in self.stop_words['en']
                )
                if not is_stopword:
                    filtered_words.append(word)
        
        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序并返回前k个
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_k]]
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        情感分析（简单版本）
        
        Args:
            text (str): 输入文本
            
        Returns:
            Dict[str, Any]: 情感分析结果
        """
        processed_text = self.preprocess_text(text)
        
        positive_count = 0
        negative_count = 0
        
        # 统计正面和负面词汇
        for lang in ['zh', 'en']:
            for word in self.sentiment_words['positive'][lang]:
                positive_count += processed_text.count(word)
            for word in self.sentiment_words['negative'][lang]:
                negative_count += processed_text.count(word)
        
        # 计算情感得分
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment_score = 0.0  # 中性
            sentiment_label = 'neutral'
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            if sentiment_score > 0.1:
                sentiment_label = 'positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
        
        return {
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'confidence': min(abs(sentiment_score) + 0.1, 1.0)
        }
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """
        提取文本特征
        
        Args:
            text (str): 输入文本
            
        Returns:
            Dict[str, Any]: 特征字典
        """
        processed_text = self.preprocess_text(text)
        
        # 基本统计特征
        char_count = len(text)
        word_count = len(processed_text.split())
        sentence_count = len(re.split(r'[.!?。！？]', text))
        
        # 语言检测（简单版本）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > english_chars:
            detected_language = 'zh'
        elif english_chars > 0:
            detected_language = 'en'
        else:
            detected_language = 'unknown'
        
        # 提取关键词
        keywords = self.extract_keywords(text, top_k=5)
        
        # 情感分析
        sentiment = self.analyze_sentiment(text)
        
        # 特殊模式检测
        has_url = bool(re.search(r'http[s]?://|www\.', text))
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        has_phone = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text))
        
        return {
            'text_length': char_count,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': char_count / max(word_count, 1),
            'detected_language': detected_language,
            'keywords': keywords,
            'sentiment': sentiment,
            'has_url': has_url,
            'has_email': has_email,
            'has_phone': has_phone,
            'chinese_char_ratio': chinese_chars / max(char_count, 1),
            'english_char_ratio': english_chars / max(char_count, 1)
        }

# 示例使用
if __name__ == "__main__":
    processor = NLPProcessor()
    
    # 测试文本
    test_texts = [
        "这家餐厅的服务很好，食物也很美味。环境很舒适，推荐大家来试试。",
        "The food was terrible and the service was awful. I would not recommend this place.",
        "访问我们的网站 www.example.com 获取更多优惠信息！"
    ]
    
    for text in test_texts:
        print(f"\n原文: {text}")
        features = processor.extract_features(text)
        print(f"特征: {features}")

