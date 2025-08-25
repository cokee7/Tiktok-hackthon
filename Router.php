<?php
/**
 * 简单的路由处理类
 * 处理HTTP请求路由和方法匹配
 */

class Router {
    private $routes = [];
    
    /**
     * 添加路由
     */
    public function addRoute($method, $path, $handler) {
        $this->routes[] = [
            'method' => strtoupper($method),
            'path' => $path,
            'handler' => $handler
        ];
    }
    
    /**
     * 处理请求
     */
    public function handleRequest() {
        $method = $_SERVER['REQUEST_METHOD'];
        $path = $this->getRequestPath();
        
        Config::log("处理请求: $method $path");
        
        // 查找匹配的路由
        foreach ($this->routes as $route) {
            if ($route['method'] === $method && $this->matchPath($route['path'], $path)) {
                try {
                    $response = call_user_func($route['handler']);
                    Config::log("请求处理成功: $method $path");
                    return $response;
                } catch (Exception $e) {
                    Config::log("请求处理失败: $method $path - " . $e->getMessage(), 'ERROR');
                    throw $e;
                }
            }
        }
        
        // 未找到匹配的路由
        http_response_code(404);
        Config::log("路由未找到: $method $path", 'WARNING');
        return [
            'status' => 'error',
            'message' => '请求的API端点不存在',
            'path' => $path,
            'method' => $method
        ];
    }
    
    /**
     * 获取请求路径
     */
    private function getRequestPath() {
        $path = $_SERVER['REQUEST_URI'];
        
        // 移除查询字符串
        if (($pos = strpos($path, '?')) !== false) {
            $path = substr($path, 0, $pos);
        }
        
        return $path;
    }
    
    /**
     * 匹配路径
     * 简单的精确匹配，可以扩展为支持参数的路径匹配
     */
    private function matchPath($routePath, $requestPath) {
        return $routePath === $requestPath;
    }
    
    /**
     * 获取请求体数据
     */
    public static function getRequestBody() {
        $input = file_get_contents('php://input');
        return json_decode($input, true);
    }
    
    /**
     * 验证必需的字段
     */
    public static function validateRequiredFields($data, $requiredFields) {
        $missing = [];
        
        foreach ($requiredFields as $field) {
            if (!isset($data[$field]) || empty($data[$field])) {
                $missing[] = $field;
            }
        }
        
        if (!empty($missing)) {
            throw new InvalidArgumentException('缺少必需字段: ' . implode(', ', $missing));
        }
    }
}
?>

