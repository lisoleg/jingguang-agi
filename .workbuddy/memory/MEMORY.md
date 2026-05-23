# 长期记忆

## 项目概览
**净光哥** 太乙AGI：Flask应用，位于 `C:\Users\1\WorkBuddy\2026-05-06-task-1\`
- 主服务器: `app.py` (Flask, 端口5001)
- 前端: `static/index_agi12.html` (三栏布局界面)
- 脑图: `app_mindmap_v2.py` (端口5003)
- **总规模**: 179模块 / 9层 / 170定理

## 当前版本：v7.20（✅已部署+Git推送完成 d9d7840）
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
- **模块**: M1-M95(v5-7.0) | M96-M105(v7.1) | M106-M110(v7.3) | M111-M113(v7.4) | M114-M116(v7.5) | M117-M119(v7.6) | M120-M125(v7.7) | M126-M129(v7.8) | M130-M133(v7.9) | M134-M137(v7.10) | M138-M141(v7.11) | M142-M147(v7.12) | M148-M156(v7.13) | M157-M162(v7.15) | M163-M170(v7.16) | M171-M173(v7.17) | M174-M175(v7.18) | M176-M178(v7.19) | M179(v7.20)
- **定理**: T1-T7(核心) | T8-T16(v6.1) | T17-T22(v6.2) | T23-T40(v7.0) | T41-T51(v7.1) | T52-T58(v7.2) | T59-T65(v7.3) | T66-T71(v7.4) | T72-T74(v7.5) | T75-T77(v7.6) | T78(M106) | T79-T85(v7.7) | T86-T91(v7.8) | T92-T95(v7.9) | T96-T99(v7.10) | T100-T103(v7.11) | T104-T109(v7.12) | T110-T123(v7.13) | T搜索完备性(v7.14) | T124-T129(v7.15) | T130-T140+T33'+T110v2(v7.16) | T141-T150(v7.17) | T151-T156(v7.18) | T157-T165(v7.19) | T166-T170(v7.20)

## API版本模式
- `/api/v719/*`: v7.19（组织记忆·Φ场预算·AgentOS）| `/api/v718/*`: v7.18（沙箱增强·安全护盾）| `/api/v717/*`: v7.17（λ宇宙·TY形式化·UFM-RISC-V具身架构）| `/api/v716/*`: v7.16 | `/api/v715/*`: v7.15 | `/api/v714/*`: v7.14
- `/api/chat_v2`: 主对话 | `/api/goal`: 目标模式

## 核心模块文件
- `CompositeAGI_V2.py`: 主核心（v5.0+）
- `HolographicDiscreteGovernance.py`: M29 全息离散治理
- `M176-M178_*.py`: v7.19（组织记忆·Φ场预算·AgentOS）| `M174-M175_*.py`: v7.18（沙箱增强·安全护盾）| `M171-M173_*.py`: v7.17 | `M163-M170_*.py`: v7.16 | `M157-M162_*.py`: v7.15

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
- **M130 感知谱分解面板** ✅: L1-L5五层架构条 + 卷积核5×5 + PCA主因子 + 流贯帧率 + 对偶指示器
- **M178 Agent行为分析面板** ✅: Agentic RL白盒化——工具调用分布 + 推理轨迹 + GC消耗Canvas图 + 奖励信号

## 重要Bug记录（精简）
- `_to_native` float转换：需检查imag!=0
- app.run()阻塞：路由必须在app.run()之前定义
- M88幻觉检测逻辑反转：check返回_detect_hallucination而非not _detect_hallucination（v7.15已修复）
- Python 3.10不支持f-string内反斜杠
- M176/M177 API参数：memory_type需转MemoryType枚举（不能直接传str）；M177 spend/earn参数是reason不是description
- M171 API返回值是dict(非object)：reduce()返回{'output','steps','normalized'}而非属性；verify_fixed_point_property()无'converges'字段
- M102 compress_trajectory有状态：每次调用trajectory_count++，测试一致性需保存/恢复状态
- M63 Mononumber用__new__ singleton：每次创建返回同一实例

## TY/IDO 审计基础设施
- `TYIDO_SelfConsistency.py`: P1共享基模块（SelfConsistencyChecker + ConsistencyResult）
- `TYIDO_ContinuousLearning.py`: P2共享基模块（StateSnapshot + RollbackManager + ForgettingGuard + LearningRecord）
- P2遗忘防护关键设计：只监控质量指标(排除history_length等数量指标)；auto-baseline在首次学习后设置；verdict只计drift/critical_loss

## 服务启动
```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1 && python app.py
# 访问 http://127.0.0.1:5001/static/index_agi12.html
```
