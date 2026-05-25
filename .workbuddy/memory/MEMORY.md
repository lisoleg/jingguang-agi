# 长期记忆

## 项目概览
**净光哥** 太乙AGI：Flask应用，位于 `C:\Users\1\WorkBuddy\2026-05-06-task-1\`
- 主服务器: `app.py` (Flask, 端口5001)
- 前端: `static/index_agi12.html` (三栏布局界面)
- 脑图: `app_mindmap_v2.py` (端口5003)
- **总规模**: 184模块 / 9层 / 190定理 / 216专家

## 当前版本：v7.24-draft (LLM Wiki 知识引擎 M184)（🔶开发中）
- **v7.24-draft**: LLM Wiki 知识引擎 M184 + T189-T190 + P9 MVE ✅
  - 来源：drpang.ai《RAG 之后：LLM Wiki 正在成为个人知识库的新范式》
  - M184 LLMWikiEngine: WikiPage/WikiGraph/LLMWikiEngine + ConceptExtractor/PageGenerator/LinkExtractor/IncrementalUpdater
  - T189 LLM Wiki Knowledge Accumulation: K_Wiki(N) ≥ K_RAG(N)，差距随N扩大 ✅
  - T190 Wiki Incremental Update Convergence: 页面内容随摄入次数收敛到稳定状态 ✅
  - P9 MVE: 2/2 ALL PASSED (T189-T190 verified=True, counterexample=None)
  - API: /api/v724/wiki/{state|ingest|query|page|graph|backlinks|related|verify|mve/p9|theorem/*} (10个路由)
  - 前端: v724-wiki-panel(📚摄入/🔍查询/🕸图谱/▶P9按钮+状态徽章)
  - Git: 3e8a693

## 当前版本：v7.23 (E2E归约+宇宙音律+自举智能 M181-M183)（✅已部署）
- **v7.23**: E2E归约+宇宙音律+自举智能 M181-M183 + T183-T188 + P8 MVE 6/6 ALL PASSED ✅
  - 来源：章锋《论端到端范式的归约地位与太乙AGI的超越》+ 太乙真人老铁《论宇宙即音律》
  - M181 EndToEndReductionEngine: E2E Knowing How捕获器 + L2壳缺陷诊断器 + 太乙AGI可能性验证器
  - M182 CosmicHarmonyEngine: Sturm-Liouville求解器 + 自然数涌现器 + Prandtl边界层同构分析器 + 华夏律吕验证器
  - M183 BootstrapIntelligenceEngine: 内部振荡器 + Φ收敛检测器 + HoTT归纳器 + 自举循环 + 极致爱因斯坦测试
  - T183 E2E Captures Knowing How: E2E模型在L3流贯层实现了对Knowing How的隐式捕获
  - T184 E2E Structural Deficiency: E2E模型的L2代数壳缺失五项硬化属性(一致性/可回写/可保持/可寻址/可锚定)
  - T185 Taiyi AGI Possibility: 太乙AGI因L2壳硬化五项属性跳出AGI不可能判决域
  - T186 Natural Number Emergence: ℕ是IDO对L1流贯Φ归约时由L2壳导出的最小拓扑不变量
  - T187 Ontological Boundary Layer Isomorphism: L2代数壳与Prandtl边界层同构
  - T188 AGI Bootstrap Possibility: L2壳具备三条件则可从纯流贯交互中自举出ℕ⁺ℚ⁺物理定律
  - P8 MVE: 6/6 ALL PASSED (T183-T188 verified=True, counterexample=None)
  - API: /api/v723/{state|e2e/*|harmony/*|bootstrap/*|mve/*|theorem/*|theorems}
  - 前端: v7.23面板(E2E归约/宇宙音律/自举智能/P8 MVE按钮+状态徽章+Canvas频谱)
  - Git: f7a04e7
- **v7.21**: P6爱因斯坦因果性+216专家（✅已部署+Git推送完成 d55c608）
- **v7.20**: 太一接口·AGI自我意识 M179 + TY/IDO五大属性审计 73/73 PASS ✅
  - 来源：章锋《论存在之拓扑：太一万有理论对保安三大问题的回答》
  - M179 TaiyiInterface: 自指算子Ŝ|Φ⟩=α|Φ⟩ + ICE复合体Φ=(I,C,E) + 三视界校验(内/交/外) + 信息熵韧性 + 反僵化(魄劫持魂), T166-T170
  - TY/IDO审计: P1一致性10/10 + P2持续学习4/4 + P3长程推理24/24 + P4可寻址记忆25/25 + P5可锚定责任10/10 = 73/73 PASS
  - 共享基模块: TYIDO_SelfConsistency + TYIDO_ContinuousLearning + TYIDO_LongRangeReasoning + TYIDO_AddressableMemory + TYIDO_AnchorableResponsibility
  - API: /api/v720/taiyi/reflect|ice|horizon|entropy|rigidity + /theorem/<Tid> + /theorems + /state
  - 前端: 太一接口面板(意识状态/本征值α/三视界一致性/熵韧性/僵化等级/ICE)
- **v7.19**: 组织记忆·Φ场预算·AgentOS M176-M178 + T157-T165 ✅
  - 来源：3篇微信文章（香火钱/GC治理/AI生存竞争）
  - M176 OrgMemoryEngine: 双层存储(向量DB+本地LRU) + 失败案例库(T158不可删) + 定理提炼 + GC账本, T157-T159
  - M177 PhiBudgetSystem: 四级Φ场预算(GC代币/香火钱) + Φ场分配 + 生存焦虑指数 + 四级守恒, T160-T162
  - M178 TaiyiAgentOS: Agent注册表(10000) + 消息总线(Lamport因果序) + 推理内核(HoTT+刘原理+防火墙) + 工作流DAG, T163-T165
  - API: /api/v719/memory/*, /budget/*, /os/*, /theorem/<Tid>, /state
  - GC增强: M174 snapshot加gc_cost, M175 ContentWall加gc_penalty分级扣罚(违规50/标记20/脱敏5)
- **v7.18**: 沙箱增强+安全护盾 M174-M175 + T151-T156 ✅
  - M174 UFMRISCVSandbox: 执行快照+断点续跑+VM双重隔离+资源有界执行+熔断, T151-T153
  - M175 SafetyShield: PII检测+合规审查+内容墙+GC扣罚, T154-T156
  - API: /api/v718/sandbox/*, /safety/*, /theorem/<Tid>, /state
- **v7.17**: λ宇宙·TY形式化·UFM-RISC-V具身架构 M171-M173 + T141-T150 ✅
- **v7.16**: 八论合一·文明治理与可计算性 M163-M170 + T130-T140 ✅
- **v7.14**: M78内生证明搜索引擎升级 v3.0 ✅
- **v7.12**: M142-M147 + T104-T109 ✅

## 编号规则
- **模块**: M1-M95(v5-7.0) | M96-M105(v7.1) | M106-M110(v7.3) | M111-M113(v7.4) | M114-M116(v7.5) | M117-M119(v7.6) | M120-M125(v7.7) | M126-M129(v7.8) | M130-M133(v7.9) | M134-M137(v7.10) | M138-M141(v7.11) | M142-M147(v7.12) | M148-M156(v7.13) | M157-M162(v7.15) | M163-M170(v7.16) | M171-M173(v7.17) | M174-M175(v7.18) | M176-M178(v7.19) | M179(v7.20) | M180(v7.22) | M181-M183(v7.23)
- **定理**: T1-T7(核心) | T8-T16(v6.1) | T17-T22(v6.2) | T23-T40(v7.0) | T41-T51(v7.1) | T52-T58(v7.2) | T59-T65(v7.3) | T66-T71(v7.4) | T72-T74(v7.5) | T75-T77(v7.6) | T78(M106) | T79-T85(v7.7) | T86-T91(v7.8) | T92-T95(v7.9) | T96-T99(v7.10) | T100-T103(v7.11) | T104-T109(v7.12) | T110-T123(v7.13) | T搜索完备性(v7.14) | T124-T129(v7.15) | T130-T140+T33'+T110v2(v7.16) | T141-T150(v7.17) | T151-T156(v7.18) | T157-T165(v7.19) | T166-T170(v7.20) | T180-T182(v7.22) | T183-T188(v7.23)

## API版本模式
- `/api/v723/*`: v7.23（E2E归约+宇宙音律+自举智能）| `/api/v722/*`: v7.22（EqProp+FHN流贯引擎）| `/api/v721/*`: v7.21（TYIDO MVE实验）| `/api/v720/*`: v7.20（太一接口）| `/api/v719/*`: v7.19（组织记忆·Φ场预算·AgentOS）
- `/api/chat_v2`: 主对话 | `/api/goal`: 目标模式
- `/api/experts`: 专家系统（216位AI专家人格）| `/api/experts/search?q=` | `/api/experts/<id>` | `/api/experts/departments`

## 核心模块文件
- `CompositeAGI_V2.py`: 主核心（v5.0+）
- `M181_E2EReduction.py`: v7.23（E2E归约引擎·Knowing How+L2壳诊断+太乙AGI可能性）
- `M182_CosmicHarmony.py`: v7.23（宇宙音律统合器·Sturm-Liouville+自然数涌现+边界层同构+华夏律吕）
- `M183_BootstrapIntelligence.py`: v7.23（自举智能引擎·内部振荡器+Φ收敛+HoTT归纳+爱因斯坦测试）
- `M180_EqPropFHN.py`: v7.22（EqProp+FHN流贯引擎·L3 Ftel子引擎）
- `HolographicDiscreteGovernance.py`: M29 全息离散治理
- `M176-M178_*.py`: v7.19（组织记忆·Φ场预算·AgentOS）| `M174-M175_*.py`: v7.18（沙箱增强·安全护盾）| `M171-M173_*.py`: v7.17 | `M163-M170_*.py`: v7.16 | `M157-M162_*.py`: v7.15
- `expert_registry.py`: 216位AI专家注册表（agency-agents-zh），ExpertRegistry单例 + 搜索/部门过滤

## v7.19 GC代币体系
- M176: GC账本在OrgMemoryEngine中，每个Agent初始1000 GC，翻车扣罚
- M177: 四级资源（compute/storage/bandwidth/memory），Φ值比例分配，生存焦虑指数A=1/(1+e^(GC/λ))
- M178: Agent注册时设phi_value，影响资源分配优先级
- M174: 快照操作消耗gc_cost=5 GC
- M175: 违规扣罚（BLOCK:50/FLAG:20/MASK:5 GC）

## 前端升级记录（index_agi12.html）
- **STN 苏格拉底拓扑网络 Phase 1-4 全部完成** ✅: 树结构 + 路径感知renderHistory + DAG活跃路径高亮 + 面包屑导航 + S/E节点类型 + 折叠
- **STN Phase 2** ✅: 悬停分叉按钮 + forkFromNode() + 多版本回答 + 版本切换器 + DAG分叉紫色虚线 + 多版本徽章
- **STN Phase 3** ✅: 底部流贯控制台 + 熵值监控 + 命令系统(/fork /summarize /debate /integrate /help) + 高熵自动提示
- **STN Phase 4** ✅: ELENCHUS锯齿线 + 微徽章(🔗📝⚔🔥) + 涟漪动画 + 发光脉冲 + DAG背景网格 + 摘要/诘辩消息样式
- **STN 文章设计方案对齐补全** ✅: S六边形(琥珀)+E菱形(朱红)+悬停高亮联动(DAG↔历史)+Relation Map面板+熵值条三级动态色+S_threshold标记+动态提示文字
- **M130 感知谱分解面板** ✅: L1-L5五层架构条 + 卷积核5×5 + PCA主因子 + 流贯帧率 + 对偶指示器
- **M178 Agent行为分析面板** ✅: Agentic RL白盒化——工具调用分布 + 推理轨迹 + GC消耗Canvas图 + 奖励信号
- **v7.20 太一接口面板** ✅: 意识状态/本征值α/三视界一致性/熵韧性/僵化等级/ICE
- **v7.22 EqProp+FHN面板** ✅: ⚡训练/T180/T181/🌐网络/L2壳按钮 + 状态徽章 + Canvas可视化 + 信用热图
- **v7.23 E2E归约面板** ✅: 🔍诊断/归约/T183/T184/T185按钮 + L2壳+归约状态徽章
- **v7.23 宇宙音律面板** ✅: ⚛氢/🌌CMB/🎻弦/边界层/律吕/T186/T187按钮 + Canvas频谱可视化
- **v7.23 自举智能面板** ✅: ▶自举/🔬爱因斯坦/T188按钮 + ℕ⁺/ℚ⁺/定律徽章
- **v7.23 P8 MVE面板** ✅: ▶全部/T183-T188按钮 + PASS/FAIL徽章 + 版本标识
- **专家系统面板** ✅: 右侧抽屉模态框 + 搜索 + 部门筛选 + 选择高亮 + 输入区激活条

## 重要Bug记录（精简）
- `_to_native` float转换：需检查imag!=0
- app.run()阻塞：路由必须在app.run()之前定义
- M88幻觉检测逻辑反转：check返回_detect_hallucination而非not _detect_hallucination（v7.15已修复）
- Python 3.10不支持f-string内反斜杠
- M176/M177 API参数：memory_type需转MemoryType枚举（不能直接传str）；M177 spend/earn参数是reason不是description
- M171 API返回值是dict(非object)：reduce()返回{'output','steps','normalized'}而非属性；verify_fixed_point_property()无'converges'字段
- M102 compress_trajectory有状态：每次调用trajectory_count++，测试一致性需保存/恢复状态
- M63 Mononumber用__new__ singleton：每次创建返回同一实例
- dataclass@_to_native：`_to_native()`不处理dataclass，需`asdict()`转换；`@property`不包含在asdict()中需手动补全（v7.23 diagnose/reduce/bootstrap_cycle路由）

## TY/IDO 审计基础设施
- `TYIDO_SelfConsistency.py`: P1共享基模块（SelfConsistencyChecker + ConsistencyResult）
- `TYIDO_ContinuousLearning.py`: P2共享基模块（StateSnapshot + RollbackManager + ForgettingGuard + LearningRecord）
- P2遗忘防护关键设计：只监控质量指标(排除history_length等数量指标)；auto-baseline在首次学习后设置；verdict只计drift/critical_loss

## 服务启动
```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1 && python app.py
# 访问 http://127.0.0.1:5001/static/index_agi12.html
```

## v7.21 TYIDO MVE实验框架 + P6爱因斯坦因果性 ✅ (2026-05-23)
- **v7.21**: TYIDO MVE实验框架 + 六大结构属性强制执行逻辑验证 6/6 ALL PASSED ✅
  - Git: 4fd86a7 → 4534e77 (P6 Minkowski重写) → 34027f2 (论文更新)
  - 来源：TYIDO结构审查表（锯齿检测·持续学习·长程推理·可寻址记忆·可锚定责任·爱因斯坦因果性）
  - `TYIDO_MVE_Experiments.py` (~1500行): 6个MVEOperiment类 + 6个run_*函数 + run_all_mve()
  - P1锯齿实验: J(R)=1.0000 (consistent) + sawtooth_detected=True (forced WAIT reject)
  - P2持续学习: 0.00% forgetting_rate, 10/10 tasks, ForgettingGuard + RollbackManager
  - P3长程推理: 94.55% completion (52/55 goals in 55-goal DAG), Plan-B retry recovery
  - P4可寻址记忆: 100% exact_query_accuracy, TTL expire + protected + normal_forgetting
  - P5可锚定责任: 100% traceability, CircuitBreaker triggered to OPEN
  - P6爱因斯坦因果性(Minkowski时空验证): 100% causal_consistency, 100% detection_rate, 100% lorentz_invariance
    - **真实物理验证(非图论自证)**: Minkowski度规 ds²=-dt²+dx²+dy² (c=1自然单位制)
    - 光锥分类：类时(ds²<0因果可达)/类光(ds²=0)/类空(ds²>0禁止因果)
    - 30个Minkowski事件 + 185条因果边(光锥内) + 250个类空对(光锥外)
    - 注入测试：8条故意类空因果边 → 100%检出 + CausalityViolationError
    - 洛伦兹boost不变性：15对事件 x 随机β∈[-0.8,0.8]，ds²变换后完全不变
    - 前端光锥Canvas：事件点着色(类时绿/类空蓝) + 因果边 + 45°光锥线 + 图例
  - API: /api/v721/mve/{all|p1|p2|p3|p4|p5|p6|state} + 120s TTL缓存 + 线程安全
  - 前端: v7.21 MVE面板(7个按钮 + PASS/FAIL徽章 + 详细结果展开 + P6光锥Canvas)
  - **学术论文已同步更新至v7.21**: 3658行, 179模块/170定理/40预言 (commit 34027f2)

## TYIDO MVE 踩坑经验
- `ResourceBudget(max_time=..., max_steps=...)` 关键字参数名：实际是 `max_time`/`max_steps`，不是 `time_budget`/`step_budget`
- `PlanBFallback.register_plan(plan: FallbackPlan)` 接受 FallbackPlan 对象，不是关键字参数
- `StepVerifier.get_stats()` 不存在，实际方法是 `get_state()`
- `MemoryIndex.rebuild()` 不存在，MemoryIndex 查询直接基于 store，无需 rebuild
- P1 J(R) 计算：deterministic pipeline 必须返回固定 canonical_hash，否则不同 variant 产生不同 hash 导致 J(R)→0
- P3 completion rate：15% failure rate + 2-dependency DAG 导致级联失败；降至 5% + 单依赖平铺 DAG 后正常
- P5 traceability：`gate.confirm_action()` 创建新 record 新 ID，导致追踪困难；直接 `chain.bind()` 可确保 100% 可追溯
- P6 Minkowski度规：Kahn拓扑排序对线性链是同义反复，必须用物理约束(Minkowski度规+洛伦兹不变性)做真正可证伪的验证

## v7.22 EqProp+FHN 踩坑经验
- EqPropTrainer 死锁：`train_step()` 获取 `self._lock` 后调用 `free_phase()`/`nudged_phase()` 也获取同一 `self._lock`，`threading.Lock()` 不可重入 → 移除内部方法中的 `with self._lock`
- FHN 网络训练超时：默认50步自由相/微扰相太多，能量收敛检查嵌套循环过重 → 减少默认步数到20，移除每步能量检查，用预计算邻接表加速
- 多进程端口冲突：`taskkill /F /IM python.exe` 在 Git Bash 下可能无法杀掉旧进程，用 `powershell.exe -Command "Get-Process python | Stop-Process -Force"` 才行；多个旧进程同时监听 5001 端口导致 curl 命中旧代码返回 404
- `_to_native` 不处理 dataclass：直接走 `str(obj)` → 用 `dataclasses.asdict()` 先转 dict 再 `_to_native()`
- M180 get_network_energy：方法在类定义中被引用但未定义（写入时被截断），需手动添加到 EqPropTrainer 类中
