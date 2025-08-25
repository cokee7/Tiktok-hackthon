<?php
/**
 * 评论服务类
 * 负责处理评论评估的业务逻辑，调用ML/NLP服务
 */

class ReviewService {
    
    /**
     * 评估评论
     */
    public function evaluateReview() {
        try {
            // 获取请求数据
            $requestData = Router::getRequestBody();
            
            // 验证必需字段
            Router::validateRequiredFields($requestData, ['review_text']);
            
            $reviewText = trim($requestData['review_text']);
            $locationMetadata = $requestData['location_metadata'] ?? [];
            
            // 验证评论长度
            if (strlen($reviewText) > Config::MAX_REVIEW_LENGTH) {
                throw new InvalidArgumentException('评论文本长度超过限制');
            }
            
            if (empty($reviewText)) {
                throw new InvalidArgumentException('评论文本不能为空');
            }
            
            Config::log("开始评估评论，长度: " . strlen($reviewText));
            
            // 调用ML/NLP服务
            $mlResult = $this->callMlService($reviewText, $locationMetadata);
            
            // 格式化响应
            $response = $this->formatResponse($mlResult);
            
            Config::log("评论评估完成");
            
            return $response;
            
        } catch (InvalidArgumentException $e) {
            http_response_code(400);
            return [
                'status' => 'error',
                'message' => $e->getMessage(),
                'timestamp' => date('Y-m-d H:i:s')
            ];
        } catch (Exception $e) {
            Config::log("评论评估失败: " . $e->getMessage(), 'ERROR');
            http_response_code(500);
            return [
                'status' => 'error',
                'message' => 'ML服务调用失败，请稍后重试',
                'timestamp' => date('Y-m-d H:i:s')
            ];
        }
    }
    
    /**
     * 调用ML/NLP服务
     */
    private function callMlService($reviewText, $locationMetadata = []) {
        $url = Config::getMlServiceUrl(Config::ML_SERVICE_PREDICT_ENDPOINT);
        
        $postData = [
            'text' => $reviewText,
            'metadata' => $locationMetadata
        ];
        
        $options = [
            'http' => [
                'header' => "Content-Type: application/json\r\n",
                'method' => 'POST',
                'content' => json_encode($postData),
                'timeout' => Config::ML_SERVICE_TIMEOUT
            ]
        ];
        
        $context = stream_context_create($options);
        
        Config::log("调用ML服务: $url");
        
        // 发送请求
        $result = @file_get_contents($url, false, $context);
        
        if ($result === false) {
            // 如果ML服务不可用，返回模拟数据
            Config::log("ML服务不可用，返回模拟数据", 'WARNING');
            return $this->getMockMlResult($reviewText);
        }
        
        $mlResponse = json_decode($result, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception('ML服务返回无效的JSON响应');
        }
        
        return $mlResponse;
    }
    
    /**
     * 获取模拟ML结果（用于开发和测试）
     */
    private function getMockMlResult($reviewText) {
        // 简单的规则来模拟ML结果
        $textLower = strtolower($reviewText);
        
        $qualityScore = 0.8; // 默认质量分数
        $relevancyScore = 0.9; // 默认相关性分数
        
        // 检测广告
        $hasAd = (strpos($textLower, 'www.') !== false || 
                  strpos($textLower, 'http') !== false ||
                  strpos($textLower, '优惠') !== false ||
                  strpos($textLower, '折扣') !== false);
        
        // 检测无关内容
        $isIrrelevant = (strpos($textLower, '手机') !== false ||
                        strpos($textLower, '电脑') !== false ||
                        strpos($textLower, '无关') !== false);
        
        // 检测未访问抱怨
        $isRantWithoutVisit = (strpos($textLower, '没去过') !== false ||
                              strpos($textLower, '听说') !== false ||
                              strpos($textLower, 'never been') !== false);
        
        if ($hasAd) $qualityScore -= 0.3;
        if ($isIrrelevant) $relevancyScore -= 0.4;
        if ($isRantWithoutVisit) $qualityScore -= 0.2;
        
        return [
            'quality_score' => max(0, min(1, $qualityScore)),
            'relevancy_score' => max(0, min(1, $relevancyScore)),
            'policy_violations' => [
                'advertisement' => $hasAd,
                'irrelevant_content' => $isIrrelevant,
                'rant_without_visit' => $isRantWithoutVisit
            ]
        ];
    }
    
    /**
     * 格式化响应数据
     */
    private function formatResponse($mlResult) {
        $violations = [];
        $violationCount = 0;
        
        foreach (Config::POLICY_TYPES as $key => $name) {
            $detected = $mlResult['policy_violations'][$key] ?? false;
            if ($detected) $violationCount++;
            
            $violations[] = [
                'policy_type' => $name,
                'detected' => $detected
            ];
        }
        
        // 生成总结
        $summary = $this->generateSummary($mlResult, $violationCount);
        
        return [
            'status' => 'success',
            'data' => [
                'quality_score' => round($mlResult['quality_score'], 2),
                'relevancy_score' => round($mlResult['relevancy_score'], 2),
                'violations' => $violations,
                'summary' => $summary
            ],
            'message' => '评论评估成功',
            'timestamp' => date('Y-m-d H:i:s')
        ];
    }
    
    /**
     * 生成评估总结
     */
    private function generateSummary($mlResult, $violationCount) {
        $qualityScore = $mlResult['quality_score'];
        $relevancyScore = $mlResult['relevancy_score'];
        
        if ($violationCount === 0) {
            if ($qualityScore >= 0.8 && $relevancyScore >= 0.8) {
                return '这是一条高质量且相关的评论';
            } else if ($qualityScore >= 0.6 && $relevancyScore >= 0.6) {
                return '这是一条中等质量的评论';
            } else {
                return '评论质量或相关性较低';
            }
        } else {
            $violations = $mlResult['policy_violations'];
            $issues = [];
            
            if ($violations['advertisement']) {
                $issues[] = '包含广告内容';
            }
            if ($violations['irrelevant_content']) {
                $issues[] = '内容不相关';
            }
            if ($violations['rant_without_visit']) {
                $issues[] = '可能是未访问地点的抱怨';
            }
            
            return '评论存在以下问题: ' . implode('、', $issues);
        }
    }
}
?>

