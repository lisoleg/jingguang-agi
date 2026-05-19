/**
 * 陈天桥认知测试 - 模式选择 & API集成
 * 独立JS文件 - 方案A
 * 
 * 功能：
 * 1. 支持快速模式(12题)和完整模式(300题)
 * 2. 从API动态加载题目
 * 3. 不同模式的结果可视化
 */

// ========== 配置 ==========
const CHEN_API_URL = '/api/cognition/test';

// ========== 扩展 CHEN_TEST 对象 ==========

// 等待原 CHEN_TEST 初始化完成后扩展
document.addEventListener('DOMContentLoaded', function() {
    console.log('[陈天桥测试] 加载 chen_test_mode.js');
    
    // 延迟执行，确保原 index_agi12.html 中的 CHEN_TEST 已定义
    setTimeout(initChenTestMode, 500);
});

function initChenTestMode() {
    if (typeof CHEN_TEST === 'undefined') {
        console.error('[陈天桥测试] CHEN_TEST 对象未找到，将在1秒后重试');
        setTimeout(initChenTestMode, 1000);
        return;
    }
    
    console.log('[陈天桥测试] 开始扩展 CHEN_TEST 对象');
    
    // ===== 1. 添加模式配置 =====
    CHEN_TEST.modeConfig = {
        'quick': {
            name: '快速模式',
            questions: 12,
            time: '约5分钟',
            desc: '快速评估五大认知维度',
            showRadar: true,
            showDetails: false
        },
        'full': {
            name: '完整模式',
            questions: 300,
            time: '约2小时',
            desc: '深度认知评估，科学量化的能力画像',
            showRadar: true,
            showDetails: true
        }
    };
    
    // ===== 2. 重写 renderStart() - 显示模式信息 =====
    CHEN_TEST.renderStart = function() {
        const config = this.modeConfig[this.mode];
        const container = document.getElementById('chen-container');
        if (!container) return;
        
        container.innerHTML = `
            <div style="text-align:center;padding:16px 0">
                <div style="font-size:32px;margin-bottom:8px">🧠</div>
                <div style="font-size:13px;color:var(--txt1);margin-bottom:6px;font-weight:700" id="chen-test-title">
                    ${config.name} - 陈天桥认知测试
                </div>
                <div style="font-size:11px;color:var(--txt2);margin-bottom:4px" id="chen-test-subtitle">
                    ${config.desc}
                </div>
                <div style="font-size:10px;color:var(--txt3);margin-bottom:12px;line-height:1.6">
                    <span style="display:inline-block;background:var(--bg3);padding:2px 8px;border-radius:8px;margin:2px">
                        ${config.questions} 道题
                    </span>
                    <span style="display:inline-block;background:var(--bg3);padding:2px 8px;border-radius:8px;margin:2px">
                        ${config.time}
                    </span>
                </div>
                <div style="font-size:9px;color:var(--txt3);margin-bottom:14px;line-height:1.5">
                    自我意识 · 因果推理 · 抽象思维 · 时间感知 · 价值判断
                </div>
                <button class="chen-btn chen-btn-start" 
                        onclick="CHEN_TEST.startTest()" 
                        style="padding:8px 28px;font-size:12px" 
                        id="chen-start-btn">
                    🚀 开始${config.name}
                </button>
                <div style="font-size:9px;color:var(--txt3);margin-top:10px">
                    ${this.mode === 'full' ? '⚠️ 完整模式需要较长时间，建议确保网络稳定' : ''}
                </div>
            </div>
        `;
        
        // 更新顶部标题
        const titleEl = document.getElementById('chen-test-title');
        const subtitleEl = document.getElementById('chen-test-subtitle');
        const descEl = document.getElementById('chen-test-desc');
        if (titleEl) titleEl.textContent = config.name;
        if (subtitleEl) subtitleEl.textContent = config.desc;
        if (descEl) descEl.textContent = `${config.questions}题 · ${config.time}`;
    };
    
    // ===== 3. 开始测试 - 从API加载题目 =====
    CHEN_TEST.startTest = async function() {
        console.log(`[陈天桥测试] 开始${this.modeConfig[this.mode].name}`);
        
        const config = this.modeConfig[this.mode];
        const numQuestions = config.questions;
        
        // 显示加载状态
        const container = document.getElementById('chen-container');
        container.innerHTML = `
            <div style="text-align:center;padding:30px 0">
                <div style="font-size:32px;margin-bottom:12px;animation:pulse 1.5s infinite">⏳</div>
                <div style="font-size:12px;color:var(--txt1);margin-bottom:8px;font-weight:600">
                    正在生成测试题目...
                </div>
                <div style="font-size:10px;color:var(--txt2);margin-bottom:4px">
                    模式：${config.name}
                </div>
                <div style="font-size:10px;color:var(--txt3);margin-bottom:12px">
                    题目数量：${numQuestions} 道
                </div>
                <div style="font-size:9px;color:var(--txt3)">
                    AI正在根据五大认知维度生成个性化题目
                </div>
            </div>
        `;
        
        try {
            // 调用API获取题目
            const response = await fetch(CHEN_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: this.mode,
                    num_questions: numQuestions
                })
            });
            
            if (!response.ok) {
                throw new Error(`API返回错误: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'API返回失败');
            }
            
            // 保存题目和测试ID
            this.questions = data.questions || [];
            this.testId = data.test_id || null;
            
            console.log(`[陈天桥测试] 成功加载 ${this.questions.length} 道题`);
            
            if (this.questions.length === 0) {
                throw new Error('API返回的题目数量为0');
            }
            
            // 重置状态
            this.currentIdx = 0;
            this.answers = {};
            this.results = null;
            this.inTest = true;
            this.startTime = Date.now();
            this.elapsedTime = 0;
            this.answeredCount = 0;
            
            // 开始计时
            this.startTimer();
            
            // 渲染第一题
            this.renderQuestion();
            
            // 更新状态
            const statusEl = document.getElementById('chen-status');
            if (statusEl) {
                statusEl.textContent = `进行中 (${this.mode === 'quick' ? '快速' : '完整'})`;
                statusEl.className = 'chen-test-badge chen-status-active';
            }
            
        } catch (error) {
            console.error('[陈天桥测试] 加载题目失败:', error);
            container.innerHTML = `
                <div style="text-align:center;padding:20px 0">
                    <div style="font-size:32px;margin-bottom:8px">⚠️</div>
                    <div style="font-size:12px;color:#ff6b6b;margin-bottom:8px;font-weight:600">
                        加载题目失败
                    </div>
                    <div style="font-size:10px;color:var(--txt2);margin-bottom:12px">
                        ${error.message}
                    </div>
                    <button class="chen-btn chen-btn-start" 
                            onclick="CHEN_TEST.renderStart()"
                            style="padding:6px 20px;font-size:11px">
                        🔄 重新尝试
                    </button>
                </div>
            `;
        }
    };
    
    // ===== 4. 渲染题目 =====
    CHEN_TEST.renderQuestion = function() {
        const container = document.getElementById('chen-container');
        if (!container) return;
        
        if (this.currentIdx >= this.questions.length) {
            this.finishTest();
            return;
        }
        
        const q = this.questions[this.currentIdx];
        const progress = ((this.currentIdx + 1) / this.questions.length * 100).toFixed(1);
        const isFullMode = this.mode === 'full';
        
        let html = `
            <div class="chen-question-container">
                <!-- 进度条 -->
                <div class="chen-progress-bar">
                    <div class="chen-progress-fill" style="width:${progress}%"></div>
                </div>
                
                <!-- 题目信息 -->
                <div class="chen-question-header">
                    <span class="chen-question-num">第 ${this.currentIdx + 1}/${this.questions.length} 题</span>
                    <span class="chen-question-dim">${this.getDimensionName(q.dimension)}</span>
                    ${isFullMode ? `<span class="chen-question-diff">难度: ${'⭐'.repeat(q.difficulty || 1)}</span>` : ''}
                </div>
                
                <!-- 题目内容 -->
                <div class="chen-question-text">${q.question}</div>
        `;
        
        // 选项
        if (q.options && q.options.length > 0) {
            html += `<div class="chen-options">`;
            q.options.forEach((opt, idx) => {
                const optLetter = String.fromCharCode(65 + idx); // A, B, C, D...
                const isSelected = this.answers[this.currentIdx] === idx;
                html += `
                    <div class="chen-option ${isSelected ? 'selected' : ''}" 
                         onclick="CHEN_TEST.selectOption(${idx})">
                        <span class="chen-opt-letter">${optLetter}</span>
                        <span class="chen-opt-text">${opt}</span>
                    </div>
                `;
            });
            html += `</div>`;
        }
        
        // 完整模式显示额外信息
        if (isFullMode && q.hint) {
            html += `
                <div style="font-size:9px;color:var(--txt3);margin-top:8px;padding:6px;background:var(--bg3);border-radius:6px">
                    💡 提示：${q.hint}
                </div>
            `;
        }
        
        // 导航按钮
        html += `
                <div class="chen-nav-buttons">
                    <button class="chen-btn chen-btn-prev" 
                            onclick="CHEN_TEST.prevQuestion()"
                            ${this.currentIdx === 0 ? 'disabled' : ''}>
                        ← 上一题
                    </button>
                    <button class="chen-btn chen-btn-next" 
                            onclick="CHEN_TEST.nextQuestion()">
                        ${this.currentIdx === this.questions.length - 1 ? '📝 提交测试' : '下一题 →'}
                    </button>
                </div>
                
                <!-- 答题进度 -->
                <div style="font-size:9px;color:var(--txt3);text-align:center;margin-top:8px">
                    已答 ${Object.keys(this.answers).length}/${this.questions.length} 题
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // 更新计时器显示
        this.updateTimerDisplay();
    };
    
    // ===== 5. 选择选项 =====
    CHEN_TEST.selectOption = function(idx) {
        this.answers[this.currentIdx] = idx;
        this.answeredCount = Object.keys(this.answers).length;
        
        // 更新UI
        document.querySelectorAll('.chen-option').forEach((opt, i) => {
            opt.classList.toggle('selected', i === idx);
        });
    };
    
    // ===== 6. 上一题 =====
    CHEN_TEST.prevQuestion = function() {
        if (this.currentIdx > 0) {
            this.currentIdx--;
            this.renderQuestion();
        }
    };
    
    // ===== 7. 下一题 =====
    CHEN_TEST.nextQuestion = function() {
        if (this.currentIdx < this.questions.length - 1) {
            this.currentIdx++;
            this.renderQuestion();
        } else {
            // 最后一题，确认提交
            this.confirmSubmit();
        }
    };
    
    // ===== 8. 确认提交 =====
    CHEN_TEST.confirmSubmit = function() {
        const answered = Object.keys(this.answers).length;
        const total = this.questions.length;
        
        if (answered < total) {
            const confirmMsg = `您还有 ${total - answered} 道题未回答，确定要提交吗？`;
            if (!confirm(confirmMsg)) return;
        }
        
        this.finishTest();
    };
    
    // ===== 9. 完成测试 - 计算结果 =====
    CHEN_TEST.finishTest = async function() {
        console.log('[陈天桥测试] 测试完成，计算结果');
        
        this.inTest = false;
        this.stopTimer();
        
        const container = document.getElementById('chen-container');
        container.innerHTML = `
            <div style="text-align:center;padding:30px 0">
                <div style="font-size:32px;margin-bottom:12px;animation:pulse 1.5s infinite">📊</div>
                <div style="font-size:12px;color:var(--txt1);margin-bottom:8px;font-weight:600">
                    正在计算测试结果...
                </div>
                <div style="font-size:10px;color:var(--txt3)">
                    分析五大认知维度
                </div>
            </div>
        `;
        
        // 计算各维度得分
        const dimensionScores = {
            self_awareness: { correct: 0, total: 0 },
            causal_reasoning: { correct: 0, total: 0 },
            abstract_thinking: { correct: 0, total: 0 },
            time_perception: { correct: 0, total: 0 },
            value_judgment: { correct: 0, total: 0 }
        };
        
        this.questions.forEach((q, idx) => {
            const dim = q.dimension;
            if (dimensionScores[dim]) {
                dimensionScores[dim].total++;
                if (this.answers[idx] === q.correct_answer) {
                    dimensionScores[dim].correct++;
                }
            }
        });
        
        // 保存结果
        this.results = {
            mode: this.mode,
            totalQuestions: this.questions.length,
            answeredQuestions: Object.keys(this.answers).length,
            dimensionScores: dimensionScores,
            timeSpent: this.elapsedTime,
            answers: this.answers,
            testId: this.testId
        };
        
        // 延迟显示结果（让用户感觉在计算）
        setTimeout(() => {
            this.renderResults();
        }, 1000);
        
        // 更新状态
        const statusEl = document.getElementById('chen-status');
        if (statusEl) {
            statusEl.textContent = '已完成';
            statusEl.className = 'chen-test-badge chen-status-done';
        }
    };
    
    // ===== 10. 渲染结果 - 快速模式（简单输出）=====
    CHEN_TEST.renderQuickResults = function() {
        const r = this.results;
        const ds = r.dimensionScores;
        
        // 计算总分
        let totalCorrect = 0;
        let totalQuestions = 0;
        Object.values(ds).forEach(d => {
            totalCorrect += d.correct;
            totalQuestions += d.total;
        });
        const totalPercent = Math.round(totalCorrect / totalQuestions * 100);
        
        let html = `
            <div class="chen-result-container">
                <div style="text-align:center;margin-bottom:16px">
                    <div style="font-size:36px;margin-bottom:8px">🎯</div>
                    <div style="font-size:14px;color:var(--txt1);font-weight:700;margin-bottom:4px">
                        测试完成！
                    </div>
                    <div style="font-size:11px;color:var(--txt2);margin-bottom:12px">
                        快速模式 · ${r.answeredQuestions}/${r.totalQuestions} 题已答
                    </div>
                </div>
                
                <!-- 总分 -->
                <div style="text-align:center;margin-bottom:16px">
                    <div style="font-size:32px;font-weight:800;color:var(--accent)">
                        ${totalPercent}
                    </div>
                    <div style="font-size:10px;color:var(--txt3)">综合得分</div>
                </div>
                
                <!-- 各维度得分 -->
                <div style="margin-bottom:12px">
        `;
        
        // 维度得分条
        const dimNames = {
            self_awareness: '自我意识',
            causal_reasoning: '因果推理',
            abstract_thinking: '抽象思维',
            time_perception: '时间感知',
            value_judgment: '价值判断'
        };
        
        for (const [key, name] of Object.entries(dimNames)) {
            const d = ds[key];
            const percent = d.total > 0 ? Math.round(d.correct / d.total * 100) : 0;
            html += `
                <div style="margin-bottom:8px">
                    <div style="display:flex;justify-content:space-between;font-size:10px;margin-bottom:2px">
                        <span style="color:var(--txt2)">${name}</span>
                        <span style="color:var(--accent);font-weight:600">${d.correct}/${d.total} (${percent}%)</span>
                    </div>
                    <div style="height:6px;background:var(--bg3);border-radius:3px;overflow:hidden">
                        <div style="height:100%;width:${percent}%;background:var(--accent);border-radius:3px;transition:width 0.5s"></div>
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
                
                <!-- 用时 -->
                <div style="font-size:9px;color:var(--txt3);text-align:center;margin-bottom:12px">
                    用时：${this.formatTime(r.timeSpent)}
                </div>
                
                <button class="chen-btn chen-btn-start" 
                        onclick="CHEN_TEST.renderStart()"
                        style="padding:6px 20px;font-size:11px;width:100%">
                    🔄 重新测试
                </button>
            </div>
        `;
        
        return html;
    };
    
    // ===== 11. 渲染结果 - 完整模式（详细输出）=====
    CHEN_TEST.renderFullResults = function() {
        const r = this.results;
        const ds = r.dimensionScores;
        
        // 计算总分和各维度百分制得分
        let totalCorrect = 0;
        let totalQuestions = 0;
        const dimPercents = {};
        
        Object.entries(ds).forEach(([key, d]) => {
            totalCorrect += d.correct;
            totalQuestions += d.total;
            dimPercents[key] = d.total > 0 ? Math.round(d.correct / d.total * 100) : 0;
        });
        
        const totalPercent = Math.round(totalCorrect / totalQuestions * 100);
        
        // 认知画像评级
        let profile = '';
        let profileColor = '';
        if (totalPercent >= 90) {
            profile = '🌟 卓越';
            profileColor = '#ffd700';
        } else if (totalPercent >= 75) {
            profile = '✨ 优秀';
            profileColor = '#00d4ff';
        } else if (totalPercent >= 60) {
            profile = '👍 良好';
            profileColor = '#50fa7b';
        } else if (totalPercent >= 40) {
            profile = '📈 中等';
            profileColor = '#ffb86c';
        } else {
            profile = '💪 待提升';
            profileColor = '#ff6b6b';
        }
        
        let html = `
            <div class="chen-result-container">
                <div style="text-align:center;margin-bottom:16px">
                    <div style="font-size:36px;margin-bottom:8px">🧠</div>
                    <div style="font-size:14px;color:var(--txt1);font-weight:700;margin-bottom:4px">
                        完整认知评估报告
                    </div>
                    <div style="font-size:11px;color:${profileColor};margin-bottom:12px;font-weight:600">
                        ${profile} (${totalPercent}分)
                    </div>
                </div>
                
                <!-- 雷达图 -->
                <div style="margin-bottom:16px;text-align:center">
                    <canvas id="chen-radar-chart" width="240" height="240"></canvas>
                </div>
                
                <!-- 各维度详细得分 -->
                <div style="margin-bottom:12px">
                    <div style="font-size:11px;color:var(--txt1);font-weight:600;margin-bottom:8px">
                        五大认知维度分析
                    </div>
        `;
        
        const dimNames = {
            self_awareness: { name: '自我意识', icon: '🪞' },
            causal_reasoning: { name: '因果推理', icon: '🔗' },
            abstract_thinking: { name: '抽象思维', icon: '🎨' },
            time_perception: { name: '时间感知', icon: '⏰' },
            value_judgment: { name: '价值判断', icon: '⚖️' }
        };
        
        for (const [key, info] of Object.entries(dimNames)) {
            const d = ds[key];
            const percent = dimPercents[key];
            const barColor = percent >= 80 ? '#50fa7b' : percent >= 60 ? '#00d4ff' : percent >= 40 ? '#ffb86c' : '#ff6b6b';
            
            html += `
                <div style="margin-bottom:10px;padding:8px;background:var(--bg3);border-radius:8px">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                        <span style="font-size:11px;color:var(--txt1)">
                            ${info.icon} ${info.name}
                        </span>
                        <span style="font-size:12px;color:${barColor};font-weight:700">
                            ${percent}分
                        </span>
                    </div>
                    <div style="height:8px;background:var(--bg2);border-radius:4px;overflow:hidden;margin-bottom:4px">
                        <div style="height:100%;width:${percent}%;background:${barColor};border-radius:4px;transition:width 0.8s"></div>
                    </div>
                    <div style="font-size:9px;color:var(--txt3)">
                        正确 ${d.correct}/${d.total} 题
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
                
                <!-- 统计信息 -->
                <div style="background:var(--bg3);border-radius:8px;padding:10px;margin-bottom:12px">
                    <div style="font-size:10px;color:var(--txt2);margin-bottom:6px;font-weight:600">
                        📊 测试统计
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:9px">
                        <div style="color:var(--txt3)">总题数</div>
                        <div style="color:var(--txt1);text-align:right">${r.totalQuestions}</div>
                        <div style="color:var(--txt3)">已答题</div>
                        <div style="color:var(--txt1);text-align:right">${r.answeredQuestions}</div>
                        <div style="color:var(--txt3)">正确题数</div>
                        <div style="color:var(--txt1);text-align:right">${totalCorrect}</div>
                        <div style="color:var(--txt3)">用时</div>
                        <div style="color:var(--txt1);text-align:right">${this.formatTime(r.timeSpent)}</div>
                    </div>
                </div>
                
                <!-- 建议 -->
                <div style="background:var(--bg3);border-radius:8px;padding:10px;margin-bottom:12px">
                    <div style="font-size:10px;color:var(--txt2);margin-bottom:6px;font-weight:600">
                        💡 提升建议
                    </div>
                    <div style="font-size:9px;color:var(--txt3);line-height:1.6">
                        ${this.generateAdvice(dimPercents)}
                    </div>
                </div>
                
                <button class="chen-btn chen-btn-start" 
                        onclick="CHEN_TEST.renderStart()"
                        style="padding:6px 20px;font-size:11px;width:100%">
                    🔄 重新测试
                </button>
            </div>
        `;
        
        return html;
    };
    
    // ===== 12. 渲染结果主函数 =====
    CHEN_TEST.renderResults = function() {
        const container = document.getElementById('chen-container');
        if (!container) return;
        
        let html = '';
        if (this.mode === 'quick') {
            html = this.renderQuickResults();
        } else {
            html = this.renderFullResults();
        }
        
        container.innerHTML = html;
        
        // 如果是完整模式，绘制雷达图
        if (this.mode === 'full') {
            setTimeout(() => {
                this.drawRadarChart();
            }, 100);
        }
    };
    
    // ===== 13. 绘制雷达图 =====
    CHEN_TEST.drawRadarChart = function() {
        const canvas = document.getElementById('chen-radar-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const ds = this.results.dimensionScores;
        
        const dimensions = [
            { key: 'self_awareness', label: '自我意识' },
            { key: 'causal_reasoning', label: '因果推理' },
            { key: 'abstract_thinking', label: '抽象思维' },
            { key: 'time_perception', label: '时间感知' },
            { key: 'value_judgment', label: '价值判断' }
        ];
        
        const scores = dimensions.map(d => {
            const dim = ds[d.key];
            return dim.total > 0 ? dim.correct / dim.total : 0;
        });
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const maxRadius = 100;
        
        // 清空画布
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 绘制网格
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;
        for (let i = 1; i <= 5; i++) {
            const r = maxRadius * i / 5;
            ctx.beginPath();
            for (let j = 0; j < 5; j++) {
                const angle = (Math.PI * 2 * j / 5) - Math.PI / 2;
                const x = centerX + r * Math.cos(angle);
                const y = centerY + r * Math.sin(angle);
                if (j === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.stroke();
        }
        
        // 绘制轴线
        for (let i = 0; i < 5; i++) {
            const angle = (Math.PI * 2 * i / 5) - Math.PI / 2;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(
                centerX + maxRadius * Math.cos(angle),
                centerY + maxRadius * Math.sin(angle)
            );
            ctx.stroke();
        }
        
        // 绘制数据区域
        ctx.fillStyle = 'rgba(0, 212, 255, 0.3)';
        ctx.strokeStyle = '#00d4ff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        scores.forEach((score, i) => {
            const angle = (Math.PI * 2 * i / 5) - Math.PI / 2;
            const r = score * maxRadius;
            const x = centerX + r * Math.cos(angle);
            const y = centerY + r * Math.sin(angle);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // 绘制数据点
        scores.forEach((score, i) => {
            const angle = (Math.PI * 2 * i / 5) - Math.PI / 2;
            const r = score * maxRadius;
            const x = centerX + r * Math.cos(angle);
            const y = centerY + r * Math.sin(angle);
            
            ctx.fillStyle = '#00d4ff';
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();
        });
        
        // 绘制标签
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--txt2') || '#9980e1';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        dimensions.forEach((d, i) => {
            const angle = (Math.PI * 2 * i / 5) - Math.PI / 2;
            const x = centerX + (maxRadius + 20) * Math.cos(angle);
            const y = centerY + (maxRadius + 20) * Math.sin(angle);
            ctx.fillText(d.label, x, y);
        });
    };
    
    // ===== 14. 辅助函数：获取维度中文名 =====
    CHEN_TEST.getDimensionName = function(dimKey) {
        const names = {
            'self_awareness': '🪞 自我意识',
            'causal_reasoning': '🔗 因果推理',
            'abstract_thinking': '🎨 抽象思维',
            'time_perception': '⏰ 时间感知',
            'value_judgment': '⚖️ 价值判断'
        };
        return names[dimKey] || dimKey;
    };
    
    // ===== 15. 辅助函数：格式化时间 =====
    CHEN_TEST.formatTime = function(ms) {
        const totalSeconds = Math.floor(ms / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        if (hours > 0) {
            return `${hours}时${minutes}分${seconds}秒`;
        } else {
            return `${minutes}分${seconds}秒`;
        }
    };
    
    // ===== 16. 辅助函数：生成提升建议 =====
    CHEN_TEST.generateAdvice = function(dimPercents) {
        const advice = [];
        
        if (dimPercents.self_awareness < 60) {
            advice.push('• 自我意识：尝试每日反思，记录情绪波动和触发因素');
        }
        if (dimPercents.causal_reasoning < 60) {
            advice.push('• 因果推理：多进行"如果-那么"的假设性思考训练');
        }
        if (dimPercents.abstract_thinking < 60) {
            advice.push('• 抽象思维：学习符号逻辑，尝试用概念图组织知识');
        }
        if (dimPercents.time_perception < 60) {
            advice.push('• 时间感知：练习时间估计，使用番茄工作法提升时间意识');
        }
        if (dimPercents.value_judgment < 60) {
            advice.push('• 价值判断：阅读伦理哲学，练习权衡利弊的决策方法');
        }
        
        if (advice.length === 0) {
            advice.push('• 各维度表现优秀！建议持续挑战更高难度的认知训练');
        }
        
        return advice.join('<br>');
    };
    
    // ===== 17. 重写 reset() =====
    CHEN_TEST.reset = function() {
        this.currentIdx = 0;
        this.answers = {};
        this.results = null;
        this.inTest = false;
        this.aiAutoMode = false;
        this.aiAnswering = false;
        this.paused = false;
        this.answeredCount = 0;
        this.elapsedTime = 0;
        this.stopTimer();
        this.questions = [];
        this.testId = null;
    };
    
    // ===== 18. 初始化模式标签事件（增强版）=====
    CHEN_TEST.bindEvents = function() {
        document.querySelectorAll('.chen-mode-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                if (this.inTest) {
                    if (!confirm('测试进行中，切换模式将丢失当前进度，确定继续吗？')) {
                        return;
                    }
                }
                document.querySelectorAll('.chen-mode-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.mode = tab.dataset.chenMode;
                this.reset();
                this.renderStart();
            });
        });
    };
    
    console.log('[陈天桥测试] CHEN_TEST 对象扩展完成 ✓');
    console.log('[陈天桥测试] 支持模式:', Object.keys(CHEN_TEST.modeConfig));
}

// ========== 添加CSS样式 ==========
const chenStyle = document.createElement('style');
chenStyle.textContent = `
    /* 模式标签 */
    .chen-test-mode-tabs {
        display: flex;
        gap: 6px;
        margin-bottom: 10px;
        padding: 0 4px;
    }
    
    .chen-mode-tab {
        flex: 1;
        text-align: center;
        padding: 6px 8px;
        font-size: 10px;
        border-radius: 8px;
        cursor: pointer;
        background: var(--bg3);
        color: var(--txt3);
        transition: all 0.3s;
        border: 1px solid transparent;
    }
    
    .chen-mode-tab:hover {
        background: var(--bg2);
        color: var(--txt2);
    }
    
    .chen-mode-tab.active {
        background: var(--accent);
        color: #000;
        font-weight: 700;
        border-color: var(--accent);
    }
    
    /* 进度条 */
    .chen-progress-bar {
        height: 4px;
        background: var(--bg3);
        border-radius: 2px;
        margin-bottom: 10px;
        overflow: hidden;
    }
    
    .chen-progress-fill {
        height: 100%;
        background: var(--accent);
        border-radius: 2px;
        transition: width 0.3s;
    }
    
    /* 题目头部 */
    .chen-question-header {
        display: flex;
        gap: 8px;
        margin-bottom: 10px;
        font-size: 9px;
        color: var(--txt3);
    }
    
    .chen-question-num {
        font-weight: 600;
        color: var(--accent);
    }
    
    .chen-question-dim {
        flex: 1;
    }
    
    .chen-question-diff {
        color: #ffb86c;
    }
    
    /* 题目文本 */
    .chen-question-text {
        font-size: 12px;
        color: var(--txt1);
        line-height: 1.6;
        margin-bottom: 12px;
        padding: 10px;
        background: var(--bg3);
        border-radius: 8px;
    }
    
    /* 选项 */
    .chen-options {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 14px;
    }
    
    .chen-option {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        padding: 8px 10px;
        background: var(--bg3);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
    }
    
    .chen-option:hover {
        background: var(--bg2);
        border-color: var(--accent);
    }
    
    .chen-option.selected {
        background: rgba(0, 212, 255, 0.15);
        border-color: var(--accent);
    }
    
    .chen-opt-letter {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: var(--bg2);
        font-size: 11px;
        font-weight: 700;
        color: var(--accent);
        flex-shrink: 0;
    }
    
    .chen-option.selected .chen-opt-letter {
        background: var(--accent);
        color: #000;
    }
    
    .chen-opt-text {
        font-size: 11px;
        color: var(--txt2);
        line-height: 1.5;
    }
    
    /* 导航按钮 */
    .chen-nav-buttons {
        display: flex;
        gap: 8px;
        margin-top: 12px;
    }
    
    .chen-btn-prev,
    .chen-btn-next {
        flex: 1;
        padding: 8px;
        border: none;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .chen-btn-prev {
        background: var(--bg3);
        color: var(--txt2);
    }
    
    .chen-btn-next {
        background: var(--accent);
        color: #000;
    }
    
    .chen-btn-prev:hover,
    .chen-btn-next:hover {
        opacity: 0.85;
    }
    
    .chen-btn-prev:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
    
    /* 状态标签 */
    .chen-status-active {
        background: rgba(0, 212, 255, 0.2) !important;
        color: #00d4ff !important;
    }
    
    .chen-status-done {
        background: rgba(80, 250, 123, 0.2) !important;
        color: #50fa7b !important;
    }
    
    /* 结果容器 */
    .chen-result-container {
        padding: 4px 0;
    }
    
    /* 动画 */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
`;
document.head.appendChild(chenStyle);

console.log('[陈天桥测试] chen_test_mode.js 加载完成 ✓');
