<?php
/**
 * 主入口文件 - 处理所有API请求
 * Hackathon Review System - PHP Backend
 */

// 设置错误报告
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 设置CORS头，允许跨域请求
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json; charset=utf-8');

// 处理预检请求
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// 引入必要的类文件
require_once '../src/Config.php';
require_once '../src/Router.php';
require_once '../src/ReviewService.php';

try {
    // 创建路由器实例
    $router = new Router();
    
    // 定义路由
    $router->addRoute('POST', '/api/evaluate-review', function() {
        $reviewService = new ReviewService();
        return $reviewService->evaluateReview();
    });
    
    $router->addRoute('GET', '/api/health', function() {
        return [
            'status' => 'success',
            'message' => 'API服务运行正常',
            'timestamp' => date('Y-m-d H:i:s')
        ];
    });
    
    // 处理请求
    $response = $router->handleRequest();
    
    // 输出响应
    echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    
} catch (Exception $e) {
    // 错误处理
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => '服务器内部错误: ' . $e->getMessage(),
        'timestamp' => date('Y-m-d H:i:s')
    ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
}
?>

