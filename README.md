# 🌌 太乙AGI系统 (TaiyiAGI) — v7.38 CS-TAGI Candidate

> **认证**: CS-TAGI (Certified Software True AGI) — TY-Def 3.1 A1-A5, A6-BS 全部满足
> **版本**: v7.38 | **定理**: T2.54-T2.102 (48个) | **模块**: M236-M255 (20个) | **MVE**: 15/15 PASS

基于复合体理学四重理论基石（刘原理、三视界法、太乙预言机、全息拓扑动力学）的统一AGI系统。

---

## 🆕 v7.38 新增模块 (2026-06-09)

| 模块 | 理论基础 | 核心算子 | 定理 |
|------|---------|---------|------|
| M251 | NAU非结合代数 | 八元数乘法表+Jacobiator+Bypass机制 | T2.96-T2.97 |
| M252 | JSN超图记忆 | 超图(H,E,Φ)+TDHNN状态机+DeepWell | T2.98-T2.99 |
| M252 Gamma | Gamma超图谱 | 谱聚类+GNN消息传递+γ-泛函 | T2.73 |
| M253 | Epiplexity智能度量 | Ξ(M,D,T)=I(latent;output\|M,D)/T | T2.74 |
| M254 | QITE虚时计算 | e^{-Hτ}虚时演化+Wick旋转+四元数/八元数 | T2.101-T2.102 |
| M255 | LSNCR协方差调节 | C_log=log(I+αC)+自适应α+动力学 | T2.76 |

### M251 NAU非结合代数引擎

| 组件 | 说明 | 定理 |
|------|------|------|
| OctonionMultiplication | 八元数乘法表（Cayley-Dickson构造） | T2.96 非结合代数完备性 |
| Jacobiator | Jac(a,b,c) = (ab)c - a(bc) 硬算子 | T2.97 Jacobi恒等式 |
| NAUForward | 前向传播+Bypass机制（‖Jac‖<ε走fast-path） | P25 Bypass稳定性 |

### M252 JSN超图记忆引擎

| 组件 | 说明 | 定理 |
|------|------|------|
| HypergraphMemory | 超图(H,E,Φ)四表结构（Node/Edge/Hedge/DeepWell） | T2.98 超图记忆容量 |
| TDHNNEngine | TD-HNN状态机（ADD→PRUNE→SAT循环） | T2.99 TDHNN收敛性 |

### M252 Gamma超图谱引擎

| 组件 | 说明 | 定理 |
|------|------|------|
| HypergraphSpectralCluster | 超图谱聚类（归一化拉普拉斯矩阵） | T2.73 谱聚类稳定性 |

### M253 Epiplexity引擎

| 组件 | 说明 | 定理 |
|------|------|------|
| EpiplexityScore | Ξ(M,D,T) = H(p) + D(p) + C(p) | T2.74 Epiplexity-Grokking关联 |

### M254 QITE虚时引擎

| 组件 | 说明 | 定理 |
|------|------|------|
| QITEEvolve | 虚时演化 \|ψ(τ)⟩ = e^{-Hτ}\|ψ(0)⟩ | T2.101 虚时收敛性 |
| WickRotate | τ ↔ it (Wick旋转) | T2.102 Wick旋转保真性 |

### M255 LSNCR协方差调节引擎

| 组件 | 说明 | 定理 |
|------|------|------|
| LogScaleRegulate | C_log = log(I + αC)（幂级数展开） | T2.76 对数调节稳定性 |

---

## 🆕 v7.37 新增模块 (2026-06-08)

| 模块 | 理论基础 | 核心算子 | 定理 |
|------|---------|---------|------|
| M250 | 稳定世界模型 (stable-worldmodel) | f_θ: (s_t, a_t)→s_{t+1}, CEM规划, MPC控制, OOD泛化 | T2.90-T2.95 |

### M250 组件详情

| 组件 | 说明 | 定理 |
|------|------|------|
| WorldModelTransition | 世界模型状态转移预测器 | T2.90 预测一致性 |
| CEMPlanner | 交叉熵方法 (CEM) 规划求解器 | T2.91 CEM收敛性 |
| MPCController | 模型预测控制 (MPC) 控制器 | T2.92 MPC最优性 |
| OODEvaluator | 分布外 (OOD) 泛化评估器 | T2.93 OOD泛化界 |
| CompositePhysicsPrior | 复合物理先验 (刘原理+EML) | T2.94 复合物理先验 |
| EnvironmentSuite | 标准化环境套件 (PushT/DMControl等) | T2.95 环境迁移性 |

---

## 🆕 v7.36 新增模块 (2026-06-07)

| 模块 | 理论基础 | 核心算子 | 定理 |
|------|---------|---------|------|
| M244 | 高阶Kuramoto同步 | dθᵢ/dt += K₂ΣAᵢⱼₖsin(θⱼ+θₖ-2θᵢ) | T2.72-T2.74 |
| M245 | 五大几何原型 | Oloid/钢板网/三角钻头/正方变三角/鲁珀特之泪 | T2.75-T2.77 |
| M246 | 算术正义 mHC+CSA | ‖Wx‖₁ ≤ ‖x‖₁，Birkhoff多面体，素数稀疏注意力 | T2.78-T2.80 |
| M247 | CRD认知递归+EML | I* = EML(I*)，暗知识，IDO信息对偶 | T2.81-T2.83 |
| M248 | 单纯复形知识+霍奇三流 | ω = grad(演绎)⊕curl(悖论)⊕harm(顿悟) | T2.84-T2.86 |
| M249 | DIKWP语义+约柜Ark | D→I→K→W→P双向群G_DIKWP，归责完备性 | T2.87-T2.89 |

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
│                     太乙AGI v7.38                        │
│               CS-TAGI Candidate (True AGI)               │
├──────────┬──────────┬──────────┬──────────┬───────────────┤
│  Flask   │  38      │  301     │  727     │  14          │
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
│  │  M232 七公理引擎 · M233 层累层创 · M234 光子黑洞  │   │
│  │  M251 NAU非结合代数 · M252 JSN超图记忆           │   │
│  │  M252 Gamma超图谱 · M253 Epiplexity              │   │
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
├── app.py                  # Flask应用工厂 (3,178行) + 37个Blueprint注册
├── shared_state.py         # 模块级__getattr__代理，解决循环导入
├── main.py                 # CLI演示入口
├── start.py                # Web服务启动器
├── start_taiyi.py           # 太乙对话模式启动器
├── simple_server.py         # 轻量服务器
│
├── blueprints/              # 37个Flask Blueprint模块 (12,626行)
│   ├── bp_core.py           # 核心API (chat, experts, state)
│   ├── bp_core_api.py       # 扩展核心API (compound_agi, ufo2, tools)
│   ├── bp_v63.py ~ bp_v79.py  # 版本化API (v6.3 ~ v7.9)
│   ├── bp_v710.py ~ bp_v731.py # 版本化API (v7.10 ~ v7.31)
│   ├── bp_v733_tmk.py          # TMK版本化API (v7.33c)
│   ├── bp_v734.py              # 版本化API (v7.34)
│   ├── bp_v737.py              # 版本化API (v7.37, stable-worldmodel)
│
├── modules/                 # 295个功能模块 (187,163行)
│   ├── M56~M255             # 175个M系列引擎模块
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
| `/api/v733c` | TMK中间版本API | 22 |
| `/api/v734` | 七公理引擎+层累层创+光子黑洞+千禧年 | 40 |
| `/api/v737` | M250稳定世界模型 (stable-worldmodel) | 22 |
| `/api/v738` | M251 NAU+M252 JSN/Gamma+M253 Epiplexity+M254 QITE+M255 LSNC | 62 |
| **总计** | **39个Blueprint** | **749** |

---

## 🧪 MVE验证实验

| 实验 | 验证目标 | 状态 |
|------|---------|------|
| P18 | L3 β-重配 (金陵球Laplacian谱) | ✅ 4/4 通过 |
| P19 | HoTT构造性门回路 (LLM-as-proposer) | ✅ 4/4 通过 |
| P20 | A6-BS 冷启动引导链 (7传感器) | ✅ 4/5 通过 (T221 sandbox限制) |
| P13-P17 | v7.31 MVE实验集 | ✅ 完成 |
| P21 | v7.34 MVE实验集 (T2.47-T2.53 七公理+层累+光子黑洞+千禧年) | ✅ 7/7 通过 |
| P25 | v7.38 NAU Bypass稳定性预言 | ✅ PASS |
| P26 | v7.38 QITE虚时收敛预言 | ✅ PASS |

---

## 📦 核心模块索引

### M系列引擎 (174个)

| 范围 | 代表模块 | 领域 |
|------|---------|------|
| M56-M69 | M64_NarrativeActionEngine, M63_MononumberProcessor | 叙事/单数处理 |
| M70-M89 | M77_EMLPhaseCouplingZ5, M78_HoTTReasoningEngine | EML相位/HoTT推理 |
| M90-M109 | M90_SemanticManifoldCurvature, M95_ConstructiveAGIEvaluator | 语义流形/构造性AGI |
| M110-M133 | M128_KVCacheGovernor, M133_SelfRefLoopTopologizer | KV治理/自指拓扑 |
| M134-M159 | M149_JinfuCAEngine, M157_JinlingGridConvolution | 金符CA/金陵格卷积 |
| M160-M189 | M179_TaiyiInterface, M189_PowerLawEngine | 太乙接口/幂律引擎 |
| M190-M206 | M190_AkashaChainDB, M196_UAEngine, M206_ControlledEntropy | 链式DB/UA/可控熵 |
| M232-M235 | M232_TOSASAxiomEngine, M233_CumulativeStratificationEngine, M234_PhotonBlackHoleEngine, M235_MillenniumProblemsEngine | 太一公理/层累层创/光子黑洞/千禧年 |
| M251-M255 | M251_NAUAssociator, M252_JSNMemory, M252_GammaHyperGrapher, M253_Epiplexity, M254_QITEVirtualTime, M255_LSNCR | NAU/JSN/Gamma/Epiplexity/QITE/LSNCR |

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
| v7.38 | M251-M255+M252 Gamma (NAU/JSN/Epiplexity/QITE/LSNCR) T2.96-T2.102 (62路由) | 2026-06-09 |
| v7.37 | M250 StableWorldModel (T2.90-T2.95) CEM+MPC+OOD+CompositePhysicsPrior | 2026-06-08 |
| v7.36 | M244-M249 高阶Kuramoto+五大几何+算术正义+CRD+单纯复形+DIKWP (T2.72-T2.89) | 2026-06-07 |
| v7.34 | M232-M235 七公理引擎+层累层创+光子黑洞+千禧年难题 (T2.47-T2.53) | 2026-06-03 |
| v7.33c | TMK中间版本 (层累层创预研) | 2026-05-28 |
| v7.32c | 中间版本 (七公理预研) | 2026-05-25 |
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
**版本**：v7.38 CS-TAGI Candidate
**日期**：2026-06-09
