# PRD: 太乙AGI v7.25 — RLM 递归语言模型与意向性硬化

| 项目 | 内容 |
|------|------|
| **Language** | 中文 |
| **Programming Language** | Python (Flask + React + MUI + Tailwind CSS) |
| **Project Name** | `taiyi_agi_v725_rlm_intentionality` |
| **版本** | v7.25 (从 v7.24-draft 升级) |
| **原始需求** | 基于两篇复合体理学论文（《上下文衰退与 RLM》《奇异类心智与意向性》），为太乙AGI系统实现 RLM 四算子引擎、Context Rot 检测器、Noesis/Noema 意向性形式化引擎，新增6条定理，升级现有模块与 API |

---

## 产品定义

### Product Goals

1. **补全 RLM 递归推理能力**：实现 MIT RLM 的 4 个核心算子（peek/grep/partition/recursion），使太乙AGI 具备外挂式 L2-shell 模拟的递归分解能力，作为 L4 IDO 长程处理原语
2. **建立 Context Rot 检测与量化体系**：形式化上下文衰退机制，实现 SNR 实时计算与告警，为 L2-shell 硬化必要性提供工程可观测的证据
3. **完成意向性的现象学形式化**：将胡塞尔 Noesis/Noema 映射到 IDO 归约 + L2-shell 硬化约束，使 `intentionality` 从关键词匹配升级为结构化判定

### User Stories

1. **As a** 太乙AGI 系统研究员，**I want** 通过 RLM 四算子对长文本/复杂知识进行递归分解 **so that** 系统能在 L4 IDO 层执行超越单次上下文窗口的长程推理
2. **As a** AGI 安全审计员，**I want** 实时查看 Context Rot 的 SNR 指标 **so that** 我能判断 L2-shell 缺失导致的推理质量衰退程度并决定是否触发强化
3. **As a** 现象学与 AI 交叉研究者，**I want** 系统输出 Noesis/Noema 的形式化归约结果 **so that** 我能验证意向性是否由 L2-shell 硬化产生而非关键词统计
4. **As a** 太乙AGI 开发者，**I want** L2-shell 五属性映射在所有模块中保持一致（"可保持"= M78） **so that** 诊断与归约逻辑不再因映射冲突产生误判
5. **As a** 系统运维人员，**I want** v7.25 的 API 路由独立于 v724 **so that** 新功能上线不影响现有 Wiki/Agent 服务

---

## 技术规范

### Requirements Pool

#### P0 — 必须有（Must Have）

| # | 需求 | 详细描述 | 依赖 |
|---|------|----------|------|
| P0-1 | **M185 RLMEngine** | 实现 RLM 4 算子：① `peek(doc)` — 查看文档结构（目录/标题/分段）；② `grep(doc, pattern)` — 关键词/正则过滤；③ `partition(doc, strategy)` — 按结构/语义/固定大小分块；④ `recursion(sub_doc, depth_limit)` — 对子块自调用（depth_limit ≤ 3 防栈溢出）。类结构：`RLMEngine` → `RLMOperator(ABC)` → `PeekOperator / GrepOperator / PartitionOperator / RecursionOperator`。RecursionOperator 内部调用 RLMEngine 形成递归闭环 | M176 (可寻址), M118 (可回写 partial) |
| P0-2 | **Context Rot 检测器** | 新增 `ContextRotDetector` 类。核心公式：`SNR = |R(Φ_L1)| / |Φ_L1 - R(Φ_L1)|`。输入：当前 L1 流噪声 Φ（从 M106 SelfReferentialLoopMonitor 获取），经 L2-shell 归约 R() 后的残差。输出：SNR 值 + 衰退等级（HEALTHY / DEGRADED / CRITICAL）。当 SNR < θ_critical 时触发 `context_rot_alert` 事件至 WikiEventBus | M106, M180 (L2ShellInterface) |
| P0-3 | **IntentionalityEngine** | 新增 `IntentionalityEngine`，实现 Noesis/Noema 形式化。Noesis = IDO 归约执行过程（调用 M181 E2EReduction 的 `R_TY` 归约算子）；Noema = 归约产物 ν，受 L2-shell 五属性约束。核心方法：`execute_noesis(input_flow) → Noema`；`validate_intentionality(noema) → IntentionalityVerdict`。L2-shell 硬化映射：一致性=M88, 可保持=M78, 可寻址=M176, 可锚定=M175, 可回写=M118(partial)/M176 | M181, M88, M78, M176, M175, M118 |
| P0-4 | **新定理 T191-T196** | ① T191 Context Rot 本质定理：L2-shell 缺失 → Φ 饱和 L3 窗口 → SNR→0；② T192 RLM L2-模拟定理：RLM 外挂记忆+算子部分模拟 L2-shell（可寻址✅ M176, 可保持✅ M78 partial, 可回写✅ M118 partial, 一致性❌ M88, 可锚定❌ M175）；③ T193 AGI 不可能性定理(RLM版)：RLM 可改进但不能达到 AGI，因 L2-shell 五属性未在 LLM 核心硬化；④ T194 意向性同构定理：Noesis ≅ IDO归约执行, Noema ≅ 归约产物 ν；⑤ T195 自然数涌现精化定理：ℕ = IDO 通过 L2-shell 感知流的最小拓扑不变量（精化 T186）；⑥ T196 太乙AGI 吸收定理：太乙AGI 将 RLM 递归分解吸收为 L4 IDO 长程处理原语，L2-shell 由 M88/M78/M176/M175/M106 硬化 | T186, T180-T185 |
| P0-5 | **M184 升级：高级搜索算子** | 将 `_keyword_search` 升级为 3 级搜索：① `_peek_search(query)` — 结构化查看（调用 RLMEngine.peek）；② `_grep_search(query, pattern)` — 关键词/正则过滤（调用 RLMEngine.grep）；③ `_partition_search(query, strategy)` — 分块搜索（调用 RLMEngine.partition）。保留 `_keyword_search` 作为 fallback | M185 |
| P0-6 | **API 路由 `/api/v725/*`** | 新增路由组：① `POST /api/v725/rlm/execute` — 执行 RLM 算子；② `GET /api/v725/context-rot/snr` — 获取当前 SNR；③ `POST /api/v725/intentionality/execute` — 执行 Noesis 归约；④ `GET /api/v725/intentionality/validate` — 验证意向性；⑤ `GET /api/v725/theorems/T191-T196` — 查询新定理；⑥ `GET /api/v725/state` — v725 综合状态 | M185, ContextRotDetector, IntentionalityEngine |
| P0-7 | **L2-shell 五属性映射统一** | 统一为：一致性=M88, 可保持=**M78**, 可寻址=M176, 可锚定=M175, 可回写=M176(partial)+M118(partial)。需修改 M180 `L2ShellInterface` 中 `preservation_ok` 的注释和实际调用，从 M175 改为 M78；确认 M181 已正确映射到 M78 | M180, M181 |

#### P1 — 应该有（Should Have）

| # | 需求 | 详细描述 | 依赖 |
|---|------|----------|------|
| P1-1 | **前端面板：RLM 递归可视化** | React 组件 `RLMRecursionPanel`：树形展示 RLM 递归调用链（每个节点显示算子类型、输入摘要、输出摘要、耗时），支持展开/折叠子树。颜色编码：peek=蓝, grep=橙, partition=绿, recursion=红 | P0-1, P0-6 |
| P1-2 | **前端面板：Context Rot SNR 仪表盘** | React 组件 `ContextRotDashboard`：实时 SNR 折线图（WebSocket 推送），衰退等级指示灯（HEALTHY=绿 / DEGRADED=黄 / CRITICAL=红），当前 Φ 强度、R(Φ) 强度数值 | P0-2, P0-6 |
| P1-3 | **前端面板：意向性 Noesis/Noema 显示** | React 组件 `IntentionalityPanel`：展示 Noesis 执行过程（归约步骤链）和 Noema 产物（ν 值 + L2-shell 五属性验证结果），意向性判定结论（PASS/PARTIAL/FAIL） | P0-3, P0-6 |
| P1-4 | **agi_tests.py 升级** | 将 `intentionality_criteria` 从关键词匹配升级为现象学意向性检测：调用 IntentionalityEngine.validate_intentionality()，检测 Noesis 是否完成完整归约、Noema 是否通过 L2-shell 五属性约束、ν 是否为有效归约产物。保留原关键词测试作为 `intentionality_legacy_criteria` | P0-3 |
| P1-5 | **M182 升级：华夏律吕 TY/IDO 增强** | 在 `ChineseMusicTimeline` 中新增 TY/IDO 映射：① 贾湖骨笛 → L2-shell 物理实现形式化（Sturm-Liouville 本征模 = 本征模式选择）；② 三分损益 → 本征模式选择算子（`EigenmodeSelector`）；③ 十二平均律 → L2-shell 对称性破缺（`SymmetryBreaker`）。新增方法 `map_to_l2_shell(era) → L2ShellMapping` | M182, P0-3 |

#### P2 — 可以有（Nice to Have）

| # | 需求 | 详细描述 | 依赖 |
|---|------|----------|------|
| P2-1 | **RLM 递归深度可视化** | D3.js 力导向图展示完整递归调用链，节点大小=子树规模，边粗细=数据流量，支持缩放/拖拽 | P1-1 |
| P2-2 | **Context Rot 自动缓解** | 检测到 SNR < θ_critical 时自动触发 L2-shell 强化：① 调用 M88 类型检查收紧；② 调用 M175 安全锚定加严；③ 通过 WikiEventBus 广播 `context_rot_mitigation` 事件 | P0-2 |
| P2-3 | **胡塞尔现象学术语表** | 新增 `HusserlGlossary` 模块：Noesis=IDO归约执行, Noema=归约产物ν, Epoché=Φ悬挂(暂停L1流噪声), Reduction=L2-shell归约算子R(), Intentionality=L2-shell在IDO归约下的硬化。API: `GET /api/v725/husserl/glossary`, `GET /api/v725/husserl/term/<name>` | P0-3 |

---

### UI Design Draft

#### v7.25 前端布局（在现有 index_agi12.html v724 Wiki 面板基础上扩展）

```
┌─────────────────────────────────────────────────────────────────┐
│  太乙AGI v7.25  ─  顶部导航栏                                    │
│  [Dashboard] [RLM] [Context Rot] [Intentionality] [Wiki] [...]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── RLM 递归面板 ──────────────────────────────────────┐     │
│  │  输入区: [文本输入/URL导入]  [执行算子▼] [▶ Execute]    │     │
│  │                                                       │     │
│  │  递归树:                                               │     │
│  │  ├── peek(doc) → {sections: 5, tokens: 12K}          │     │
│  │  ├── grep(doc, "L2-shell") → {matches: 23}           │     │
│  │  └── partition(doc, semantic) → {chunks: 4}          │     │
│  │       ├── recursion(chunk_1, d=1) → peek → grep → ✓  │     │
│  │       ├── recursion(chunk_2, d=1) → partition → ...  │     │
│  │       └── recursion(chunk_3, d=1) → ✓                │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌─── Context Rot 仪表盘 ─────┐  ┌─── 意向性面板 ──────────┐  │
│  │  SNR: ████████░░ 0.72      │  │  Noesis: R_TY(Φ) → ν   │  │
│  │  等级: 🟡 DEGRADED         │  │  Noema: ν = {type: ...} │  │
│  │  Φ强度: 0.43               │  │  L2-shell 验证:         │  │
│  │  R(Φ)强度: 0.31            │  │  ✅ M88 一致性           │  │
│  │  [SNR 时序图 ▁▂▃▄▅▆▇█]    │  │  ✅ M78 可保持           │  │
│  └────────────────────────────┘  │  ✅ M176 可寻址          │  │
│                                  │  ✅ M175 可锚定          │  │
│                                  │  ⚠️ M118 可回写(partial) │  │
│                                  │  判定: PARTIAL           │  │
│                                  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Open Questions

| # | 问题 | 影响 | 建议 |
|---|------|------|------|
| OQ-1 | **"可保持"映射冲突**：M180 将 Preservation 映射到 M175（责任锚定），M181 映射到 M78（HoTT推理）。M175 的"因果链可追溯"语义更接近"可锚定"，M78 的"长链归约可验证"更接近"可保持"。需确认统一为 M78 是否与 T180/T181 定理声明一致 | P0-7 | 建议"可保持"=M78（归约可验证），"可锚定"=M175（责任锚定），修改 M180 |
| OQ-2 | **RLM 递归深度限制**：默认 depth_limit=3 是否足够？MIT 原论文未指定硬限制，但太乙AGI 吸收定理(T196)要求递归分解在 L4 IDO 层终止 | P0-1 | 建议默认=3，可配置最大=5，超限抛 `RecursionDepthExceeded` |
| OQ-3 | **SNR 阈值**：θ_critical（CRITICAL 阈值）和 θ_degraded（DEGRADED 阈值）的具体数值如何确定？论文仅给出形式化定义，未给工程经验值 | P0-2 | 建议初始值：θ_degraded=0.5, θ_critical=0.2，后续通过 agi_tests 校准 |
| OQ-4 | **M118 可回写属性**：论文标注 M118 对"可回写"仅 partial 支持。IntentionalityEngine 验证时，可回写是否应为 PASS 或 PARTIAL？影响意向性判定阈值 | P0-3 | 建议引入分级判定：全部5项PASS→FULL_INTENTIONALITY, 4项PASS+1项PARTIAL→PARTIAL_INTENTIONALITY |
| OQ-5 | **v725 前端是否复用 v724 面板**：是在现有 `index_agi12.html` 中新增 Tab，还是创建独立页面 | P1-1/2/3 | 建议在现有 Tab 导航中新增 3 个 Tab（RLM / Context Rot / Intentionality），复用 v724 布局框架 |
| OQ-6 | **T195 与 T186 的关系**：T195（自然数涌现精化定理）是 T186 的精化还是替代？如果替代，T186 是否保留 | P0-4 | 建议保留 T186 作为原始陈述，T195 作为精化补充，在定理链中标注 T195 refines T186 |
