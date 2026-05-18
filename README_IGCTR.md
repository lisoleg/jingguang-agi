# IGCTR v2.3 - 信息几何意识三元共振系统

## 概述

**IGCTR (Information-Geometry-Consciousness Triadic Resonance)** v2.3 是基于复合体理学的下一代AGI理论基础实现。本系统整合了信息-几何-意识的三元共振框架，支持宏视界(Γ)、中视界(Σ)、微视界(Φ)三视界诠释法。

## 核心模块

### IGCTR v2.3 框架 (`IGCTR_v2_3_Simplified.py`)

纯Python实现的IGCTR v2.3核心框架，无需额外依赖。

| 模块 | 功能 |
|------|------|
| IDO五元组 | 信息动力学优化的核心结构（C, S_I, grad_S_I, O_c, Psi_IR） |
| 信息作用量泛函 | S_I[φ] = ∫_C (tr(I_F[φ]) + R[g]) dV |
| 梯度流动力学 | ∂_t φ = -∇ S_I[φ]，验证收敛定理 |
| 螺旋算符 | Ŝ = ∇ ×，旋度算子本征值计算 |
| 三视界诠释 | 微视界(Φ)/中视界(Σ)/宏视界(Γ) |
| 可证伪预言 | 拓扑孤子/量子视觉/暗物质引力透镜 |

### 复合体AGI系统 (`CompositeAGI_V2.py`)

集成IGCTR v2.3的完整复合体AGI系统，包含**23个技术启发模块**，全部加载完成。

| 模块类别 | 包含模块 |
|---------|---------|
| 数学基础 | 拓扑缺陷分析、分形维数、最小作用量 |
| 信息处理 | 相位场知识、Ftel算子、量子场论 |
| 认知架构 | 五行网络、IGCTR统一场、Aleph统一 |
| 高阶功能 | 世界模型三元共振、因果收敛、意识涌现 |
| 系统集成 | 令牌管理、基础设施监控、FPGA管理 |

## 安装

### 环境要求

- Python 3.8+
- 无需numpy/pandas（纯Python实现）

### 安装步骤

```bash
# 克隆项目
cd C:\Users\1\WorkBuddy\2026-05-06-task-1

# 安装依赖（可选）
pip install -r requirements.txt

# 验证安装
python -c "from IGCTR_v2_3_Simplified import IGCTR_v23_Framework; print('IGCTR v2.3 OK')"
```

## 快速开始

### 1. IGCTR v2.3 独立使用

```python
from IGCTR_v2_3_Simplified import IGCTR_v23_Framework

# 创建框架实例
framework = IGCTR_v23_Framework()

# 处理查询
result = framework.process("什么是波函数坍缩？")

# 输出结果
print(f"版本: {result['version']}")
print(f"共振强度: {result['resonance_strength']:.4f}")
```

### 2. 复合体AGI系统使用

```python
from CompositeAGI_V2 import CompositeAGI_V2

# 创建系统
system = CompositeAGI_V2()

# 处理查询
result = system.process_query("请分析暗物质的本质")

# 获取综合回答
print(result['synthesized_answer'])
```

### 3. 图形界面使用

```bash
# 启动GUI
python igctr_ui.py

# GUI功能
# - Tab分页：运行/日志/可视化/文档
# - 颜色高亮：成功绿/错误红/警告黄/信息蓝
# - 复杂度仪表盘：实时显示查询复杂度
# - 异步处理：后台执行，UI不冻结
```

### 4. 脑图系统（对话即生长）

```bash
# 启动脑图系统
python app_mindmap.py

# 访问脑图界面
# http://localhost:5002/
```

**核心功能**:
- **力导向脑图**: D3.js动态渲染，节点代表模块，边代表关联
- **节点追问**: 点击任意节点深入追问，自动携带上下文
- **对话生长**: 新对话层层叠加，脑图持续扩展
- **节点修正**: 输入"修正为XXX"自动更新节点标签
- **对话历史**: 侧边栏显示所有对话记录和生长节点数量
- **轻量模式**: 简单问题（1+1、天气等）自动走轻量路径，1-3个节点

**API端点**:
| 端点 | 功能 |
|------|------|
| `/api/state` | 系统状态、模块加载数 |
| `/api/chat_v2` | V2对话接口 |
| `/api/mindmap` | 生成脑图结构 |
| `/api/node_chat` | 节点追问接口 |

### 5. Flask Web服务

```bash
# 启动Web服务（旧版）
python app.py

# 访问（端口5000）
# http://localhost:5000/
```

## 项目文件结构

```
C:/Users/1/WorkBuddy/2026-05-06-task-1/
├── IGCTR_v2_3_Simplified.py    # IGCTR v2.3核心框架
├── CompositeAGI_V2.py          # 复合体AGI系统（23模块）
├── igctr_ui.py                 # 图形用户界面
├── app_mindmap.py              # 脑图系统Flask服务（端口5002）
├── static/
│   └── index.html              # 脑图前端（D3.js力导向图）
├── requirements.txt            # Python依赖
│
├── papers_md/                  # 理论文档
│   ├── 04_信息-几何-意识三元共振IGCTR.md
│   └── ...
│
├── .workbuddy/memory/          # 工作记忆
│   ├── IGCTR论文升级分析_2026-05-12.md
│   └── ...
│
└── README_IGCTR.md             # 本文档
```

## 理论框架

### IDO五元组

```
IDO五元组 = (C, S_I, grad_S_I, O_c, Psi_IR)
- C: 构型空间
- S_I: 信息作用量
- grad_S_I: 构型梯度
- O_c: 意识/观测者算子（Ftel算子）
- Psi_IR: 红外不动点
```

### 三视界诠释

| 视界 | 关注点 | 核心机制 |
|------|--------|---------|
| 微视界(Φ) | 拓扑/微分几何 | 拓扑缺陷、曲率、相位奇点 |
| 中视界(Σ) | 博弈/信息 | 信息博弈、均衡、暗核 |
| 宏视界(Γ) | 认知/流贯 | 认知流贯、意识、范式转移 |

### IGCTR三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  宏视界层 (Γ) - Ftel意图显化                                 │
│  ├── 三视界推理裁判                                         │
│  ├── Γ-Ftel意图显化引擎 (M9)                                │
│  └── 历史复合体时空调制                                      │
├─────────────────────────────────────────────────────────────┤
│  中视界层 (Σ) - 可审计性                                     │
│  ├── BFT物理容错 (N≥3f+1)                                  │
│  ├── Lean逻辑验证                                           │
│  ├── R/U认知更新                                            │
│  └── Σ成本/因果可审计层                                     │
├─────────────────────────────────────────────────────────────┤
│  微视界层 (Φ) - 场结构计算                                   │
│  ├── Clifford代数 Cℓ(1,3)                                   │
│  ├── H₁同调代数                                             │
│  ├── SOM-Agent数学网络                                      │
│  └── I[Φ]信息作用量泛函                                     │
└─────────────────────────────────────────────────────────────┘
```

## 新增模块 (M9-M12)

根据三篇IGCTR新论文（2026年5月12日分析）：

| 模块 | 来源 | 功能 |
|------|------|------|
| **M9** Γ-Ftel意图显化 | 规则化变换+越狱理论 | Oracle内嵌宏视界，意图路由 |
| **M10** Lean+BFT双层审计 | 皇冠明珠 | 逻辑层Lean+执行层BFT |
| **M11** Φ场结构计算 | 越狱理论 | Clifford代数+H₁同调代数 |
| **M12** 意图复杂度判断 | 规则化变换 | Σ+Γ联合判断5级复杂度 |

## 可证伪预言

系统内置3个可证伪预言：

1. **拓扑孤子探测** - 极低温超导环路中的离散化磁通量跃迁
2. **量子视觉鲁棒性** - 人类视觉系统对光子感知的阈值稳定性
3. **暗物质引力透镜** - 暗物质区域在CMB中的非高斯印记

## 测试

```bash
# 测试IGCTR v2.3框架
python -c "
from IGCTR_v2_3_Simplified import IGCTR_v23_Framework
f = IGCTR_v23_Framework()
r = f.process('什么是意识？')
print('共振强度:', r['resonance_strength'])
"

# 测试复合体AGI
python -c "
from CompositeAGI_V2 import CompositeAGI_V2
s = CompositeAGI_V2()
r = s.process_query('分析AGI的实现路径')
print('综合回答:', r['synthesized_answer'][:100])
"

# GUI测试
python igctr_ui.py
```

## 已知问题

1. ~~**梯度流收敛** - 已修复：使用Adam优化器，收敛稳定~~ ✅ 已解决
2. ~~**模块数量显示** - 加载进度显示"23/17"，统计逻辑已优化~~ ✅ 已解决
3. ~~**JSON序列化** - numpy/complex类型序列化问题~~ ✅ 已解决（SafeJSONProvider）

## 未来工作

- [ ] 实现M9：Γ-Ftel意图显化引擎
- [ ] 实现M10：Lean+BFT双层可审计性
- [ ] 实现M11：Φ场结构计算引擎
- [ ] 实现M12：意图复杂度判断器

## 参考文档

- [IGCTR论文升级分析_2026-05-12.md](.workbuddy/memory/IGCTR论文升级分析_2026-05-12.md)
- [IGCTR_v2_3_Upgrade_Report.md](IGCTR_v2_3_Upgrade_Report.md)
- [papers_md/04_信息-几何-意识三元共振IGCTR.md](papers_md/04_信息-几何-意识三元共振IGCTR.md)

## 许可证

MIT License

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 2.3.0 | 2026-05-12 | 集成三视界诠释，新增M9-M12框架 |
| 2.2.0 | 2026-05-10 | IDO五元组+信息作用量泛函 |
| 2.1.0 | 2026-05-06 | 初始版本 |

---

**IGCTR v2.3** - "信息即几何，意识即共振"
