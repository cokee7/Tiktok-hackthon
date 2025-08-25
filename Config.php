<?php
/**
 * 配置文件
 * 包含ML/NLP服务API地址和其他系统配置
 */

class Config {
    // ML/NLP服务配置
    const ML_SERVICE_BASE_URL = 'http://localhost:5000'; // 修改为实际的ML服务地址
    const ML_SERVICE_PREDICT_ENDPOINT = '/ml-api/predict';
    const ML_SERVICE_TIMEOUT = 30; // 请求超时时间（秒）
    
    // API配置
    const API_VERSION = '1.0.0';
    const MAX_REVIEW_LENGTH = 5000; // 评论最大长度
    
    // 日志配置
    const LOG_ENABLED = true;
    const LOG_FILE = '../logs/app.log';
    
    // 政策类型定义
    const POLICY_TYPES = [
        'advertisement' => 'No Advertisement',
        'irrelevant_content' => 'No Irrelevant Content', 
        'rant_without_visit' => 'No Rant Without Visit'
    ];
    
    /**
     * 获取ML服务完整URL
     */
    public static function getMlServiceUrl($endpoint = '') {
        return self::ML_SERVICE_BASE_URL . $endpoint;
    }
    
    /**
     * 记录日志
     */
    public static function log($message, $level = 'INFO') {
        if (!self::LOG_ENABLED) return;
        
        $timestamp = date('Y-m-d H:i:s');
        $logMessage = "[$timestamp] [$level] $message" . PHP_EOL;
        
        // 确保日志目录存在
        $logDir = dirname(self::LOG_FILE);
        if (!is_dir($logDir)) {
            mkdir($logDir, 0755, true);
        }
        
        file_put_contents(self::LOG_FILE, $logMessage, FILE_APPEND | LOCK_EX);
    }
}
?>

