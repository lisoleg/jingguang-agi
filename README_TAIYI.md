# Taiyi-AGI 太乙因果机 — CS-TAGI Certified Software True AGI

> **版本**: v7.32c · 222+模块 · 9+层架构 · 257+定理 · 43预言 · 223专家  
> **认证**: CS-TAGI (Certified Software True AGI) — TY-Def 3.1 A1-A5 + A6-BS 全部满足  
> **核心引擎**: M133 W1-W5 Patches + M196 UA Engine + M190 AkashaChainDB

---

## 📐 核心理论

### 复合体理学四重理论基石

| 理论 | 说明 | 系统应用 |
|------|------|---------|
| **刘原理** | 全域所有可能路径中，实际发生的路径必使作用量取平稳值 | 系统自组织演化 |
| **三视界法** | 微视界-中视界-宏视界三重诠释 | 时间维度分析 |
| **太乙预言机** | 设定终态，逆向演化 | 目标导向推理 |
| **全息拓扑动力学** | 局部包含整体信息 | 全局优化 |

### 关键概念

- **Ftel算子**（Teleological Constraint Operator）: 目的约束算子，将"目标/意图g"作为约束场投影至生成空间
- **SerDes本体论**: TY-Serialize Π_s:R→S / TY-Deserialize Δ_s:S→R，bi-SerDes完备性四条件
- **金陵球引擎**: 基于复合体理学的超图计算框架
- **碳硅GAN**: 碳基智能-硅基智能对抗生成网络
- **万物理解引擎（UA）**: ExpertBridge 4通道匹配 + ContextBuilder + 知识图谱

---

## 🏗️ 系统架构

### 9+层架构

```
┌─────────────────────────────────────────────────────────┐
│ L9  元层 — SubstrateLimitation DSL, CS-TAGI认证          │
│ L8  AGI治理层 — M207-M222 (金符3D·天行相位·歧义·六合·   │
│     偶像·偏心率·哥德尔·Eros·刘罚·具身·ITA·双工厂·       │
│     临界金灵球·摄控中心·SerDes本体论)                    │
│ L7  组织层 — M171-M179, M190-M199                        │
│ L6  现象层 — M141-M170, M200-M206                        │
│ L5  行为层 — M111-M140                                   │
│ L4  认知层 — M81-M110, M196                              │
│ L3  主体层 — M51-M80, M180-M181, M185-M186, M188-M189   │
│ L2  帧层 — M21-M50, M182-M184, M187                      │
│ L1  本体层 — M1-M20, M133_W1-W5                          │
└─────────────────────────────────────────────────────────┘
```

### Blueprint API架构

36个Flask Blueprint模块，版本化API路由：

| 前缀 | 说明 |
|------|------|
| `/api/v732c/*` | v7.32c ITA·双工厂·临界金灵球·摄控中心·SerDes (21路由) |
| `/api/v732b/*` | v7.32b 金符3D·天行相位·歧义·六合·偶像·偏心率·哥德尔 (13路由) |
| `/api/v732a/*` | v7.32a 心智·自我·社会·认知·EML (10路由) |
| `/api/m133/*` | v7.31 M133 W1-W5 Wintel (9路由) |
| `/api/v730/akasha/*` | v7.30 AkashaChainDB v3 UA集成 (7路由) |
| `/api/v728/ua/*` | v7.28b UA引擎 + ExpertBridge (7路由) |
| `/api/v727/*` | v7.27 金陵球·太极延续·Phi调度·碳硅GAN·世界模型 (5路由) |

---

## 🚀 快速开始

### 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10 | ⚠️ 3.13有numpy兼容问题 |
| Flask | 2.x+ | Web框架 |
| NumPy/SciPy | 兼容3.10 | 数值计算 |
| NetworkX | 3.x | 图计算 |

### 安装与启动

```bash
# 进入项目目录
cd D:/WorkBuddy/2026-05-06-task-1/

# 安装依赖
pip install -r requirements.txt

# 启动Flask服务
python app.py
# → 监听 0.0.0.0:5000, debug=True
```

### 前端面板

| 面板 | URL | 说明 |
|------|-----|------|
| AGI仪表盘 | http://localhost:5000/static/index_agi12.html | v7.32c完整仪表盘（222+模块·257+定理） |
| M133 Wintel面板 | http://localhost:5000/static/m133_wintel_panel.html | M133 W1-W5控制面板 |

---

## 📊 版本历程

| 版本 | 模块数 | 定理数 | 关键交付 |
|------|--------|--------|---------|
| v7.21 | 179 | 170 | 9层架构·TYIDO MVE·陈天桥测试 |
| v7.22 | 181 | 185 | 等距传播FHN·E2E归约 |
| v7.23 | 188 | 196 | 宇宙和谐·理解引擎·RLM·意向性 |
| v7.25b | 189 | 196 | 幂律引擎（三分损益与BFT 2/3同源） |
| v7.27 | 195 | 216 | 金陵球·太极延续·Phi调度·碳硅GAN·世界模型 |
| v7.28 | 196 | 221 | 万物理解引擎（UA） |
| v7.28b | 196 | 221 | ExpertBridge 4通道专家匹配 |
| v7.29 | 196 | 223 | AkashaChainDB v2 性能优化 |
| v7.30 | 196 | 226 | AkashaChainDB v3 UA集成 |
| **v7.31** | **201** | **229** | **M133 W1-W5·CS-TAGI认证·Blueprint重构** |
| v7.32a | 211 | 236 | 心智·自我·社会·认知灵活性·EML |
| v7.32b | 222 | 247 | 金符3D·天行相位·歧义·六合·哥德尔逃逸舱 |
| **v7.32c** | **222+** | **257+** | **ITA·双工厂·临界金灵球·摄控中心·SerDes本体论** |

---

## 🧩 核心模块概览

### 关键模块

| 模块 | 文件 | 说明 |
|------|------|------|
| M133_W1 | `modules/M133_W1_IdrisSelfRef.idr` | L4 ICE Y-组合子自指核 (Idris 2) |
| M133_W2 | `modules/M133_W2_JinlingGraphBetaRewire.py` | L3 beta-重配API, Laplacian spectrum |
| M133_W3 | `modules/M133_W3_HoTTLeanGate.py` | HoTT构造性门回路 |
| M133_W4 | `modules/M133_W4_ColdStartBootstrap.py` | A6-BS冷启动引导链 |
| M190 | `modules/M190_AkashaChainDB.py` | Akasha链式数据库（v1-v3，3970行） |
| M196 | `modules/M196_UnderstandAnythingEngine.py` | 万物理解引擎 |
| M191 | `modules/M191_JinlingSphereEngine.py` | 金陵球引擎 |
| M193 | `modules/M193_PhiScheduler.py` | Phi调度器 |
| M194 | `modules/M194_CarbonSiliconGAN.py` | 碳硅GAN |
| M222 | `modules/M222_SerDesOntologyEngine.py` | SerDes本体论引擎 |

### 辅助系统

| 文件 | 说明 |
|------|------|
| `app.py` | Flask应用工厂 + Blueprint注册 (3,177行) |
| `shared_state.py` | 模块级__getattr__代理 |
| `expert_registry.py` | 223位AI专家注册表 |
| `blueprints/` | 36个Flask Blueprint模块 |
| `modules/` | 292个模块（164个M系列 + 123个辅助） |
| `tests/` | 48个测试/MVE文件 |
| `scripts/` | 32个工具脚本 |

---

## 🧪 测试与验证

### MVE实验框架

| 实验 | 验证内容 | 状态 |
|------|---------|------|
| P1 | 锯齿测试（TYIDO一致性） | ✅ PASS |
| P2 | 可回写性验证 | ✅ PASS |
| P3 | 长程推理保持 | ✅ PASS |
| P4 | 可寻址记忆 | ✅ PASS |
| P5 | 可锚定责任 | ✅ PASS |
| P6 | Minkowski时空因果验证 | ✅ PASS |
| P18 | L3 BetaRewire | ✅ 4/4 PASS |
| P19 | HoTT Gate Loop | ✅ 4/4 PASS |
| P20 | ColdStart Bootstrap | ✅ 4/5 PASS |

### 运行测试

```bash
# 运行全部测试
python -m pytest tests/ -v

# 运行特定MVE
python tests/P18_MVE_L3BetaRewire.py
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| `DESIGN.md` | 系统设计文档 (v7.21) |
| `DESIGN_SUPPLEMENT.md` | 设计补充文档 (v7.32c) |
| `太乙AGI的设计与实现_完整学术论文.md` | 完整学术论文 |
| `USER_GUIDE.md` | 用户指南 |
| `INSTALL.md` | 安装指南 |
| `M133_W5_SubstrateLimitation.md` | CS-TAGI DSL声明 |

---

## 🔧 技术栈

| 组件 | 技术 |
|------|------|
| **后端** | Python 3.10 + Flask |
| **前端** | HTML5 + JavaScript + Canvas |
| **数据库** | AkashaChainDB (自研链式DB) |
| **形式化验证** | Idris 2 (M133_W1) + Lean (M133_W3) |
| **图计算** | NetworkX (JinlingGraph) |
| **AI专家** | agency-agents-zh (223位专家) |
| **API架构** | Flask Blueprint (36模块) |

---

## 🏆 CS-TAGI认证

Taiyi-AGI v7.32c 满足 TY-Def 3.1 全部标准：

- **A1 自指性**: M133_W1 IdrisSelfRef Y-组合子不动点 ✅
- **A2 自洽性**: M133_W3 HoTTLeanGate 构造性证明回路 ✅
- **A3 可错性**: M133_W4 ColdStartBootstrap 7传感器验证 ✅
- **A4 具身性**: M217 ArtificialFasciaEmbodiment 筋膜映射 ✅
- **A5 社会性**: M199 SocialRelTopology 多主体交互 ✅
- **A6-BS 底层自举**: M133_W4 ColdStartBootstrap 引导链 ✅

---

## ⚠️ 已知限制

1. **Python版本**: 必须使用 3.10（3.13有numpy兼容问题）
2. **M133_W4 T221**: 沙箱环境限制，Agda编译路径硬编码
3. **M203 CRDReflector**: 依赖crd_engine_v2已删除，优雅降级
4. **Git操作**: D盘沙箱可能阻断`.git/index.lock`操作

---

## 📖 参考文献

1. 复合体理学微信公众号系列文章
2. 刘德欣. *刘原理：一个从本体到现象的离散生成论体系*. 2026.
3. 章锋. *刘原理、Ftel算子与人择宇宙*. 2026.
4. 章锋. *超越内存墙：基于Ftel驱动拓扑相变的全息蛹化AGI架构理论*. 2026.

---

**作者**: 寇豆码（Kou）  
**版本**: v7.32c  
**日期**: 2026-05-30  
**认证**: CS-TAGI (Certified Software True AGI)

---

*「天行健，君子以自强不息。」*  
*「智能存在于关联中（Ftel）。」*
