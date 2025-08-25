/**
 * 主要JavaScript文件
 * 处理用户界面交互和API通信
 */

class ReviewAssessmentApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000'; // PHP后端API地址
        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        this.bindEvents();
        this.updateCharCounter();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 表单提交
        const reviewForm = document.getElementById('reviewForm');
        reviewForm.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // 字符计数器
        const reviewText = document.getElementById('reviewText');
        reviewText.addEventListener('input', () => this.updateCharCounter());

        // 重置按钮
        const resetBtn = document.getElementById('resetBtn');
        resetBtn.addEventListener('click', () => this.resetForm());

        // 导出按钮
        const exportBtn = document.getElementById('exportBtn');
        exportBtn.addEventListener('click', () => this.exportResults());

        // 模态框相关
        const aboutLink = document.getElementById('aboutLink');
        const aboutModal = document.getElementById('aboutModal');
        const closeAboutModal = document.getElementById('closeAboutModal');

        aboutLink.addEventListener('click', (e) => {
            e.preventDefault();
            aboutModal.style.display = 'flex';
        });

        closeAboutModal.addEventListener('click', () => {
            aboutModal.style.display = 'none';
        });

        // 点击模态框背景关闭
        aboutModal.addEventListener('click', (e) => {
            if (e.target === aboutModal) {
                aboutModal.style.display = 'none';
            }
        });

        // API文档和GitHub链接
        document.getElementById('apiDocsLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.showNotification('API文档功能开发中...', 'info');
        });

        document.getElementById('githubLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.showNotification('GitHub链接功能开发中...', 'info');
        });
    }

    /**
     * 更新字符计数器
     */
    updateCharCounter() {
        const reviewText = document.getElementById('reviewText');
        const charCount = document.getElementById('charCount');
        const currentLength = reviewText.value.length;
        
        charCount.textContent = currentLength;
        
        // 根据字符数量改变颜色
        if (currentLength > 4500) {
            charCount.style.color = '#e53e3e';
        } else if (currentLength > 4000) {
            charCount.style.color = '#dd6b20';
        } else {
            charCount.style.color = '#718096';
        }
    }

    /**
     * 处理表单提交
     */
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const reviewText = formData.get('reviewText').trim();
        const locationName = formData.get('locationName').trim();
        const locationId = formData.get('locationId').trim();

        // 验证输入
        if (!reviewText) {
            this.showNotification('请输入评论内容', 'error');
            return;
        }

        if (reviewText.length > 5000) {
            this.showNotification('评论内容超过最大长度限制', 'error');
            return;
        }

        // 准备请求数据
        const requestData = {
            review_text: reviewText,
            location_metadata: {}
        };

        if (locationName) {
            requestData.location_metadata.location_name = locationName;
        }

        if (locationId) {
            requestData.location_metadata.location_id = locationId;
        }

        // 显示加载状态
        this.showLoading(true);

        try {
            // 调用API
            const result = await this.callAPI('/api/evaluate-review', 'POST', requestData);
            
            if (result.status === 'success') {
                this.displayResults(result.data);
                this.showNotification('评估完成！', 'success');
            } else {
                throw new Error(result.message || '评估失败');
            }
        } catch (error) {
            console.error('API调用失败:', error);
            this.showNotification('评估失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 调用API
     */
    async callAPI(endpoint, method = 'GET', data = null) {
        const url = this.apiBaseUrl + endpoint;
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * 显示评估结果
     */
    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        
        // 显示评分
        this.displayScores(data.quality_score, data.relevancy_score);
        
        // 显示违规检测结果
        this.displayViolations(data.violations);
        
        // 显示总结
        this.displaySummary(data.summary);
        
        // 显示结果区域
        resultsSection.style.display = 'block';
        
        // 滚动到结果区域
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * 显示评分
     */
    displayScores(qualityScore, relevancyScore) {
        const qualityScoreEl = document.getElementById('qualityScore');
        const relevancyScoreEl = document.getElementById('relevancyScore');
        const qualityBar = document.getElementById('qualityBar');
        const relevancyBar = document.getElementById('relevancyBar');

        // 显示分数
        qualityScoreEl.textContent = (qualityScore * 100).toFixed(0) + '%';
        relevancyScoreEl.textContent = (relevancyScore * 100).toFixed(0) + '%';

        // 动画显示进度条
        setTimeout(() => {
            qualityBar.style.width = (qualityScore * 100) + '%';
            relevancyBar.style.width = (relevancyScore * 100) + '%';
        }, 300);

        // 根据分数调整颜色
        this.updateScoreColor(qualityBar, qualityScore);
        this.updateScoreColor(relevancyBar, relevancyScore);
    }

    /**
     * 更新分数颜色
     */
    updateScoreColor(element, score) {
        if (score >= 0.8) {
            element.style.background = 'linear-gradient(90deg, #48bb78, #38a169)';
        } else if (score >= 0.6) {
            element.style.background = 'linear-gradient(90deg, #ed8936, #dd6b20)';
        } else {
            element.style.background = 'linear-gradient(90deg, #e53e3e, #c53030)';
        }
    }

    /**
     * 显示违规检测结果
     */
    displayViolations(violations) {
        const violationsList = document.getElementById('violationsList');
        violationsList.innerHTML = '';

        violations.forEach(violation => {
            const violationItem = document.createElement('div');
            violationItem.className = `violation-item ${violation.detected ? 'detected' : 'safe'}`;
            
            violationItem.innerHTML = `
                <div class="violation-text">${violation.policy_type}</div>
                <div class="violation-status ${violation.detected ? 'detected' : 'safe'}">
                    <i class="fas ${violation.detected ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                    ${violation.detected ? '检测到违规' : '未检测到违规'}
                </div>
            `;
            
            violationsList.appendChild(violationItem);
        });
    }

    /**
     * 显示评估总结
     */
    displaySummary(summary) {
        const summaryText = document.getElementById('summaryText');
        summaryText.textContent = summary;
    }

    /**
     * 重置表单
     */
    resetForm() {
        const reviewForm = document.getElementById('reviewForm');
        const resultsSection = document.getElementById('resultsSection');
        
        reviewForm.reset();
        resultsSection.style.display = 'none';
        this.updateCharCounter();
        
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * 导出结果
     */
    exportResults() {
        const qualityScore = document.getElementById('qualityScore').textContent;
        const relevancyScore = document.getElementById('relevancyScore').textContent;
        const summary = document.getElementById('summaryText').textContent;
        const reviewText = document.getElementById('reviewText').value;
        
        // 获取违规检测结果
        const violations = [];
        document.querySelectorAll('.violation-item').forEach(item => {
            const policyType = item.querySelector('.violation-text').textContent;
            const detected = item.classList.contains('detected');
            violations.push(`${policyType}: ${detected ? '检测到违规' : '未检测到违规'}`);
        });

        // 生成报告内容
        const reportContent = `评论质量评估报告
生成时间: ${new Date().toLocaleString()}

原始评论:
${reviewText}

评估结果:
质量评分: ${qualityScore}
相关性评分: ${relevancyScore}

政策违规检测:
${violations.join('\n')}

评估总结:
${summary}

---
本报告由Review Quality Assessment System生成
`;

        // 创建并下载文件
        const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `review_assessment_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('评估报告已导出', 'success');
    }

    /**
     * 显示加载状态
     */
    showLoading(show) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        const submitBtn = document.getElementById('submitBtn');
        
        if (show) {
            loadingOverlay.style.display = 'flex';
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 评估中...';
        } else {
            loadingOverlay.style.display = 'none';
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-search"></i> 开始评估';
        }
    }

    /**
     * 显示通知消息
     */
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        // 添加样式
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1001;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
        `;

        // 添加到页面
        document.body.appendChild(notification);

        // 自动移除
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    /**
     * 获取通知图标
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * 获取通知颜色
     */
    getNotificationColor(type) {
        const colors = {
            success: '#48bb78',
            error: '#e53e3e',
            warning: '#ed8936',
            info: '#4299e1'
        };
        return colors[type] || colors.info;
    }
}

// 添加通知动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
`;
document.head.appendChild(style);

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new ReviewAssessmentApp();
});

