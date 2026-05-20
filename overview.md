# 关联追问功能 - 实现报告

## 功能概述
为太乙AGI系统添加"关联追问"功能，类似ChatGPT/元宝的体验：AI回答后自动推荐3个深化/关联的问题，点击即可继续对话。

## 修改文件

| 文件 | 修改内容 |
|------|----------|
| `app.py` | 新增 `_generate_related_questions()` 函数 + chat_v2/goal端点增加 `related_questions` 响应字段 |
| `static/index_agi12.html` | CSS样式 + `renderHistory()` 渲染关联问题 + `askRelated()` 点击处理 |

## 技术方案

### 后端
- **LLM生成（优先）**：调用 `taiyi_llm_enhancer` 的 `_call_llm()` 方法，传入定制prompt，5秒超时线程防阻塞
- **模板规则（fallback）**：中文正则 `[\u4e00-\u9fff]{2,6}` 提取关键词 + 3个模板问题
- 响应格式：`{ ..., "related_questions": ["问题1", "问题2", "问题3"] }`

### 前端
- AI消息下方渲染 `.related-questions` 区域
- 每个关联问题为可点击的 `.rq-item` 标签
- 点击后自动填入输入框并触发 `doMainChat()`

## 测试结果
- ✅ chat_v2 返回3个高质量关联追问（LLM生成）
- ✅ goal 模式同样支持
- ✅ LLM超时/失败自动fallback到模板规则
- ✅ 前端UI正常渲染和交互
