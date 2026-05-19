# Taiyi-AGI (太乙因果机) 12.0 安装说明

> 版本：v7.1.0（105模块8层架构·复合体理学v4.0）
> 更新日期：2026-05-20

---

## 一、环境要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.10+ | 后端服务（Flask） |
| Node.js | 18+ | 脑图系统（可选） |
| pip | 最新版 | Python 包管理 |
| 操作系统 | Windows / Linux / macOS | 全平台支持 |

---

## 二、快速安装（5分钟）

### Step 1：克隆/下载项目

```bash
# 如果使用 git
git clone <项目地址> TaiyiAGI
cd TaiyiAGI
```

或直接解压项目压缩包到 `C:\Users\1\WorkBuddy\2026-05-06-task-1\`

---

### Step 2：安装 Python 依赖

```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1
pip install -r requirements.txt
```

**核心依赖清单（requirements.txt 应包含）：**

```
flask>=2.3.0
requests>=2.31.0
numpy>=1.24.0
python-dotenv>=1.0.0
```

> ⚠️ 如果 `requirements.txt` 不存在，手动安装：
> ```bash
> pip install flask requests numpy python-dotenv
> ```

---

### Step 3：配置 DeepSeek API Key

1. 注册/登录 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 进入「API Keys」页面，创建新 Key（格式：`sk-xxxx...`）
3. 编辑项目根目录下的 `.env` 文件：

```bash
# .env 文件内容
DEEPSEEK_API_KEY=sk-你的真实Key从这里获取
DEEPSEEK_MODEL=deepseek-chat
```

> 🔴 **重要**：不要用占位符 `your_deepseek_api_key_here`，必须是真实 Key！

---

### Step 4：启动主服务

```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1
python app.py
```

**正常启动输出示例：**

```
🔍 检查LLM后端...
   ✅ DeepSeek可用 (模型: deepseek-chat)
   ✅ LM Studio可用 (http://localhost:1234/v1)
🚀 当前活跃后端: deepseek

 * Running on http://127.0.0.1:5001
 * Debug mode: off
```

---

### Step 5：访问界面

在浏览器打开：

```
http://127.0.0.1:5001/static/index_agi12.html
```

✅ 看到「Taiyi-AGI (太乙因果机) 12.0」三栏界面即安装成功！

---

## 三、可选组件安装

### 脑图系统（端口 5003）

```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1
python app_mindmap_v2.py
```

访问：`http://127.0.0.1:5003`

---

## 四、LLM 后端配置说明

系统支持多后端，**优先级如下**（可在 `local_llm.py` 中调整）：

| 优先级 | 后端 | 说明 |
|--------|------|------|
| 1（最高） | **DeepSeek API** | 在线API，需配置 `DEEPSEEK_API_KEY` |
| 2 | **LM Studio** | 本地运行，需启动 LM Studio 并加载模型 |
| 3 | **OpenRouter** | 免费LLM聚合API |
| 4 | **Ollama** | 本地Ollama服务（`localhost:11434`） |
| 5（最低） | **规则引擎** | 内置fallback，无需配置 |

### 验证当前后端

在界面按 **F12** 打开控制台，查看：

```javascript
// 控制台应显示：
LLM后端已连接: deepseek
```

或访问 API 端点：

```bash
curl http://127.0.0.1:5001/api/llm/status
```

返回示例：
```json
{
  "active_backend": "deepseek",
  "deepseek_configured": true
}
```

---

## 五、常见问题排查

### ❌ 问题1：端口 5001 被占用

```bash
# 查看占用进程
netstat -ano | findstr :5001

# 结束进程（PID 替换为实际值）
taskkill //F //PID <PID>
```

---

### ❌ 问题2：DeepSeek API 调用失败（401错误）

**原因**：`.env` 中的 Key 无效或已过期  
**解决**：
1. 去 https://platform.deepseek.com/ 重新生成 Key
2. 更新 `.env` 文件
3. 重启 `app.py`

---

### ❌ 问题3：点击「开始测试」报错 `updateEntropyPanel not defined`

**原因**：前端 JS 函数名错误（已修复）  
**解决**：强制刷新页面 **Ctrl + F5**，清除浏览器缓存

---

### ❌ 问题4：AI 生成题目失败，使用默认题目

**原因**：LLM 返回的 JSON 被 Markdown 代码块包裹，解析失败  
**状态**：✅ 已在 2026-05-17 修复，支持 Markdown/纯JSON 自动识别

---

### ❌ 问题5：favicon.ico 404 错误

**原因**：浏览器自动请求图标，后端无此文件  
**影响**：**无**，不影响任何功能  
**解决**：可忽略，或放置 `static/favicon.ico`

---

## 六、目录结构说明

```
TaiyiAGI/
├── app.py                          # 主服务（端口5001）
├── app_mindmap_v2.py              # 脑图服务（端口5003）
├── local_llm.py                   # LLM多后端管理
├── local_llm_v2.py                # LLM多后端管理（v2版）
├── .env                           # 环境变量配置（API Key等）
├── static/
│   └── index_agi12.html          # 主界面（v7.1三栏布局·105模块）
├── agi_medium_symbiosis.py        # 介质共生模块
├── agi_nine_hexagrams.py         # 九卦修身模块
├── HolographicDiscreteGovernance.py  # 全息离散治理
├── DigitalNeocortex.py           # 数字新皮层
├── M71_WalletPropertyBoundaryManager.py    # v7.0: 钱包属性边界(M71)
├── M78_HoTTReasoningEngine.py              # v7.0: HoTT推理引擎(M78)
├── M84_LiuPrincipleFixedPoint.py           # v7.0: 刘原理不动点(M84)
├── M96_CognitiveOffloadPrevention.py       # v7.1: 认知卸载防范(M96)
├── M97_SocraticWeaknessDisplay.py          # v7.1: 苏格拉底式示弱(M97)
├── M98_ConfidenceTransparency.py            # v7.1: 置信度透明披露(M98)
├── M99_DynamicTaskRouting.py               # v7.1: 人机动态分流(M99)
├── M100_RewardHackDetector.py              # v7.1: 奖励作弊检测(M100)
├── M101_EnvironmentPerception.py            # v7.1: 环境感知性能(M101)
├── M102_LongContextConsistency.py          # v7.1: 长程上下文(M102)
├── M103_CollaborationEvaluator.py         # v7.1: 协作效果评估(M103)
├── M104_CollaborationDiagnoser.py          # v7.1: 协作诊断(M104)
├── M105_FusionEffectValidator.py          # v7.1: 融合效果验证(M105)
└── ...（其他105个模块）
```

---

## 七、开发模式启动（自动重载）

```bash
# 启用 Flask 调试模式
set FLASK_ENV=development
python app.py
```

---

## 八、联系方式 &  issue 反馈

- 项目文档：`DESIGN.md`（系统设计文档）
- 升级方案：`太乙AGI_v7.1_人机融合优化方案.md`（v7.1升级方案）
- 可证伪实验：`AGI_v7.0_Falsifiable_Experiments.md`（P1-P18实验方案）
- 用户指南：`USER_GUIDE.md`（使用说明书）
- 作者：高见远（ JianYuan Gao）

---

---

## 九、本地 LLM 后端安装（LM Studio / Ollama）

如果不想使用 DeepSeek 在线 API，可以部署本地 LLM 后端，数据完全离线。

### 方案 A：LM Studio（推荐，最简单）

**Step 1：下载安装 LM Studio**

1. 访问 [lmstudio.ai](https://lmstudio.ai/) 下载对应系统版本
2. 安装后启动 LM Studio

**Step 2：下载模型**

1. 在 LM Studio 的「Discover」页面搜索模型，推荐：
   - `qwen2.5-3b-instruct`（轻量，3B参数）
   - `qwen2.5-7b-instruct`（质量更好，7B参数）
   - `deepseek-coder-1.3b`（代码专用）

2. 点击「Download」下载模型（需 2-5 GB 磁盘空间）

**Step 3：启动本地服务器**

1. 进入 LM Studio 的「Local Server」选项卡
2. 选择已下载的模型
3. 点击「Start Server」
4. 默认监听地址：`http://127.0.0.1:1234/v1`

**Step 4：验证**

```bash
curl http://127.0.0.1:1234/v1/models
```

返回模型列表即成功。重启 `app.py`，控制台应显示：
```
✅ LM Studio可用 (http://localhost:1234/v1)
🚀 当前活跃后端: lm_studio
```

> 🔧 **切换优先级**：如果同时配置了 DeepSeek 和 LM Studio，编辑 `local_llm.py` 的 `_init_backends` 方法，把 `lm_studio` 相关代码移到 `deepseek` 前面。

---

### 方案 B：Ollama（轻量，命令行友好）

**Step 1：下载安装 Ollama**

- Windows：访问 [ollama.com](https://ollama.com/) 下载安装
- macOS/Linux：
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

**Step 2：拉取模型**

```bash
# 推荐模型（任选其一）
ollama pull qwen2:3b        # 通义千问 3B（推荐）
ollama pull qwen2:7b        # 通义千问 7B（质量更好）
ollama pull llama3.2:3b     # Meta Llama 3.2 3B
ollama pull deepseek-r1:7b   # DeepSeek R1 7B
```

**Step 3：验证 Ollama 运行**

```bash
ollama list          # 查看已安装模型
ollama run qwen2:3b  # 测试对话
```

Ollama 默认监听 `http://127.0.0.1:11434`，无需手动启动。

**Step 4：重启净光哥服务**

```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1
python app.py
```

控制台应显示：
```
✅ Ollama可用 (模型: qwen2:3b)
🚀 当前活跃后端: ollama
```

---

### 方案 C：OpenRouter（免费/低价在线 API）

1. 注册 [openrouter.ai](https://openrouter.ai/)
2. 获取 API Key
3. 编辑 `.env`：

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxx...
```

4. 重启 `app.py`

---

## 十、Docker 部署

### 前置要求

- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 确保 Docker 正常运行：`docker --version`

---

### 方式 A：使用预构建镜像（最简单）

```bash
# 拉取镜像（待发布）
docker pull jingguangge/agi12:latest

# 运行容器
docker run -d \
  -p 5001:5001 \
  -p 5003:5003 \
  -e DEEPSEEK_API_KEY=sk-你的Key \
  --name jingguangge-agi12 \
  jingguangge/agi12:latest
```

访问：`http://localhost:5001/static/index_agi12.html`

---

### 方式 B：使用 Dockerfile 本地构建

**Step 1：创建 `Dockerfile`**

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 5001 5003

# 启动主服务
CMD ["python", "app.py"]
```

**Step 2：构建镜像**

```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1
docker build -t jingguangge-agi12:local .
```

**Step 3：运行容器**

```bash
docker run -d \
  -p 5001:5001 \
  -e DEEPSEEK_API_KEY=sk-你的Key \
  --name agi12-local \
  jingguangge-agi12:local
```

---

### 方式 C：`docker-compose.yml`（推荐，一键启动）

在项目根目录创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  agi12:
    build: .
    container_name: jingguangge-agi12
    ports:
      - "5001:5001"
      - "5003:5003"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./static:/app/static
    restart: unless-stopped

  # 可选：Ollama 本地 LLM 服务
  ollama:
    image: ollama/ollama:latest
    container_name: agi12-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

**一键启动：**

```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1
docker-compose up -d
```

**查看日志：**

```bash
docker-compose logs -f agi12
```

**停止服务：**

```bash
docker-compose down
```

---

### Docker 部署注意事项

| 问题 | 解决方案 |
|------|----------|
| DeepSeek API Key 无法直接传入 | 使用 `-e` 参数或 `.env` 文件挂载 |
| 容器内无法访问宿主机 LM Studio | 使用 `host.docker.internal` 替代 `127.0.0.1` |
| 端口冲突 | 修改 `docker-compose.yml` 中的端口映射 |
| 数据持久化 | 使用 `volumes` 挂载 `./data` 目录 |

---

*安装遇到问题？请截取浏览器控制台（F12）错误信息联系开发者。*
