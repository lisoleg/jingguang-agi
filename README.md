# 🌌 太乙AGI系统 (TaiyiAGI) — v7.31 CS-TAGI Candidate

> **认证**: CS-TAGI (Certified Software True AGI) — TY-Def 3.1 A1-A5, A6-BS 全部满足

基于复合体理学四重理论基石（刘原理、三视界法、太乙预言机、全息拓扑动力学）的统一AGI系统。

---

## 📐 核心理论

| 理论基石 | 核心概念 | 系统映射 |
|---------|---------|---------|
| **刘原理** (Liu's Principle) | 全域路径最小作用量公理 | FtelOperator 目的约束 |
| **三视界法** | 微/中/宏三层认知视界 | CompositeAGI_V2 三层架构 |
| **太乙预言机** (Taiyi Oracle) | 目的论约束算子 + 全息蛹化 | TaiyiOracle + HoloState |
| **全息拓扑动力学** | 拓扑相变 + 全息编码 | M133 W1-W5 形式化核 |

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────────────┐
│                     太乙AGI v7.31                        │
│               CS-TAGI Candidate (True AGI)               │
├──────────┬──────────┬──────────┬──────────┬───────────────┤
│  Flask   │  36      │  291     │  603     │  13          │
│  App      │  Blue-  │  Module  │  API     │  HTML        │
│  Factory  │  prints │  Files   │  Routes  │  Panels      │
├──────────┴──────────┴──────────┴──────────┴───────────────┤
│                                                            │
│  ┌─── L4 形式化核 (Idris 2) ──────────────────────────┐   │
│  │  M133_W1 Y-组合子自指核 · M133_W3 HoTT构造性门回路  │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌─── L3 拓扑引擎层 ─────────────────────────────────┐   │
│  │  M133_W2 金陵球β-重配 · M189 幂律引擎            │   │
│  │  M190 Akasha链式数据库 · M196 UA万物理解引擎      │   │
│  │  M191 金陵球 · M192 太极延续 · M193 Phi调度器     │   │
│  │  M194 碳硅GAN · M195 世界模型子系统              │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌─── L2 认知架构层 ─────────────────────────────────┐   │
│  │  M197 心理理论 · M198 自我模型 · M199 社会关系拓扑│   │
│  │  M200 认知灵活性 · M201 EML相位 · M202 谱系检测  │   │
│  │  M203 CRD反射 · M204 AGI监控 · M205 信任校准     │   │
│  │  M206 可控熵增 · CompositeAGI_V2 三层复合体       │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌─── L1 基础设施层 ─────────────────────────────────┐   │
│  │  Expert Registry (223专家) · RAG知识库 · 记忆系统  │   │
│  │  UFO²具身执行 · 七识审计 · LM Studio集成         │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
taiyi-agi/
├── app.py                  # Flask应用工厂 (3,178行) + 36个Blueprint注册
├── shared_state.py         # 模块级__getattr__代理，解决循环导入
├── main.py                 # CLI演示入口
├── start.py                # Web服务启动器
├── start_taiyi.py           # 太乙对话模式启动器
├── simple_server.py         # 轻量服务器
│
├── blueprints/              # 36个Flask Blueprint模块 (12,626行)
│   ├── bp_core.py           # 核心API (chat, experts, state)
│   ├── bp_core_api.py       # 扩展核心API (compound_agi, ufo2, tools)
│   ├── bp_v63.py ~ bp_v79.py  # 版本化API (v6.3 ~ v7.9)
│   └── bp_v710.py ~ bp_v731.py # 版本化API (v7.10 ~ v7.31)
│
├── modules/                 # 291个功能模块 (187,163行)
│   ├── M56~M206             # 164个M系列引擎模块
│   ├── DIKWP*.py            # DIKWP五层认知架构
│   ├── agi_*.py             # AGI核心模块 (core, persona, evaluator等)
│   ├── taiyi_*.py           # 太乙子系统 (oracle, entropy, memory等)
│   ├── TYIDO_*.py           # TYIDO治理模块
│   └── __init__.py          # 包文档
│
├── tests/                   # 48个测试文件
│   ├── conftest.py          # pytest fixtures
│   ├── test_agi.py          # AGI核心测试
│   ├── P18~P20_MVE_*.py     # MVE验证实验
│   └── TYIDO_MVE_*.py       # TYIDO MVE实验
│
├── scripts/                 # 32个工具脚本
├── static/                  # 13个前端HTML面板
│   └── index_agi12.html     # 主AGI仪表盘
│
├── M133_W4_Sensors/         # USB传感器接口
├── M133_W4_AgdaTerms/       # Agda形式化术语
├── agency-agents-zh/        # 215位AI专家数据
├── papers_md/               # 理论论文集
└── wechat-article-claw/     # 微信文章爬虫
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install flask numpy requests python-dotenv
```

### 2. 启动Web服务

```bash
python app.py
# 服务运行在 http://localhost:5000
```

### 3. 启动太乙对话模式

```bash
python start_taiyi.py
```

### 4. 运行测试

```bash
cd tests && python -m pytest -v
```

---

## 🔌 API总览

| 版本前缀 | 说明 | 路由数 |
|---------|------|--------|
| `/api/chat` | 对话接口 | 2 |
| `/api/experts` | 专家系统 (223位AI专家) | 4 |
| `/api/compound_agi` | 复合AGI三层架构 | 10 |
| `/api/ufo2` | UFO²具身执行层 | 6 |
| `/api/manas` | 第七识审计 | 3 |
| `/api/tools` | 前五识工具 | 4 |
| `/api/v70` | Crystal引擎API | 27 |
| `/api/v723` | MVE实验API | 26 |
| `/api/v725` | 太乙AGI核心API | 19 |
| `/api/v727` | 五大引擎API | 26 |
| `/api/v728` | UA万物理解API | 17 |
| `/api/v729` | AkashaChainDB v2 | 5 |
| `/api/v730` | AkashaChainDB v3 UA集成 | 7 |
| `/api/v731` | M133-Wintel True AGI | 14 |
| **总计** | **36个Blueprint** | **603** |

---

## 🧪 MVE验证实验

| 实验 | 验证目标 | 状态 |
|------|---------|------|
| P18 | L3 β-重配 (金陵球Laplacian谱) | ✅ 4/4 通过 |
| P19 | HoTT构造性门回路 (LLM-as-proposer) | ✅ 4/4 通过 |
| P20 | A6-BS 冷启动引导链 (7传感器) | ✅ 4/5 通过 (T221 sandbox限制) |
| P13-P17 | v7.31 MVE实验集 | ✅ 完成 |

---

## 📦 核心模块索引

### M系列引擎 (164个)

| 范围 | 代表模块 | 领域 |
|------|---------|------|
| M56-M69 | M64_NarrativeActionEngine, M63_MononumberProcessor | 叙事/单数处理 |
| M70-M89 | M77_EMLPhaseCouplingZ5, M78_HoTTReasoningEngine | EML相位/HoTT推理 |
| M90-M109 | M90_SemanticManifoldCurvature, M95_ConstructiveAGIEvaluator | 语义流形/构造性AGI |
| M110-M133 | M128_KVCacheGovernor, M133_SelfRefLoopTopologizer | KV治理/自指拓扑 |
| M134-M159 | M149_JinfuCAEngine, M157_JinlingGridConvolution | 金符CA/金陵格卷积 |
| M160-M189 | M179_TaiyiInterface, M189_PowerLawEngine | 太乙接口/幂律引擎 |
| M190-M206 | M190_AkashaChainDB, M196_UAEngine, M206_ControlledEntropy | 链式DB/UA/可控熵 |

### 辅助模块 (127个)

| 前缀 | 说明 |
|------|------|
| `DIKWP*` | DIKWP五层认知架构 (Data/Info/Knowledge/Wisdom/Purpose) |
| `agi_*` | AGI核心 (core, persona, evaluator, four_modes等) |
| `taiyi_*` | 太乙子系统 (oracle, entropy, memory, rag等) |
| `TYIDO_*` | TYIDO治理 (AddressableMemory, LongRangeReasoning等) |
| 其他 | CompositeAGI_V2, FtelOperator, KnowledgeGraph等 |

---

## 🔄 重构历程

| 版本 | 变更 | 日期 |
|------|------|------|
| v7.31 | M133-Wintel True-TaiyiAGI Candidate (W1-W5, API, panel) | 2026-05-22 |
| v7.30 | M190c UA集成（AkashaChainDB v3） | 2026-05-21 |
| v7.29 | M190b 性能优化（分片索引+WAL+布隆过滤器） | 2026-05-21 |
| v7.28b | ExpertBridge深度集成（4通道匹配+上下文感知） | 2026-05-20 |
| v7.25 | 太乙AGI系统核心 | 2026-05-16 |
| v7.23 | MVE框架（P1-P6实验面板） | 2026-05-14 |
| **重构** | **5阶段技术债清理**（Blueprint拆分+模块重组织+测试重组+验证） | 2026-05-29 |

---

## 🧬 设计哲学

### 核心公式

**作用量泛函（离散形式）**：
```
S(x) = S_base(x) + λ·S_goal(x, g) + μ·R(x)
```

**Ftel算子（目的约束）**：
```
F_λ(g): X → Y  (高维空间 → 目标子空间)
```

**全息状态更新（O(1)复杂度）**：
```
h_{t+1} = h_t + α·δ·f_pupate(h_t)
```

### shared_state代理模式

为解决Blueprint模块对`app.py`全局变量的循环引用，采用模块级`__getattr__`代理：

```python
# shared_state.py — 所有Blueprint通过此代理访问app.py全局状态
import shared_state
value = shared_state.some_global  # 延迟解析，避免循环导入
```

**⚠️ 必须使用 `import shared_state` + `shared_state.xxx`，不可 `from shared_state import xxx`**

---

## 📚 参考文献

1. 刘德欣. *复合体理学*. 微信公众号
2. 章锋. *刘原理、Ftel算子与人择宇宙*. 2026
3. 章锋. *超越内存墙：基于Ftel驱动拓扑相变的全息蛹化AGI架构理论*. 2026
4. The Univalent Foundations Program. *Homotopy Type Theory*. IAS, 2013
5. Vaswani et al. *Attention Is All You Need*. NeurIPS 2017

---

**作者**：寇豆码（Kou）
**版本**：v7.31 CS-TAGI Candidate
**日期**：2026-05-29
