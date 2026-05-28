# 长期记忆（精简版 2026-05-25-v2）

## 项目概览
**净光哥** 太乙AGI：Flask应用，位于 `C:\Users\1\WorkBuddy\2026-05-06-task-1\`
- 主服务器: `app.py` (Flask, 端口5001)
- 前端: `static/index_agi12.html` (三栏布局界面)
- 脑图: `app_mindmap_v2.py` (端口5003)
- **总规模**: 195模块 / 9层 / 217定理 / 223专家

## 版本历史（精简）

| 版本 | 内容 | Git |
|------|------|-----|
| v7.27 | 太极OS·流锻内核 M191-M195 + T201-T217 | 待提交 |
| v7.26 | AkashaChainDB M190 + FTEL+β归约+POP共识 + T197-T200 | 7248b42 |
| v7.25b | 幂律·三分损益·类型论 M189 + BFT升级 + M187/M188升级 + T191-T196 | — |
| v7.25 | RLM M186 + ContextRot M187 + Intentionality M188 + T191-T196 | — |
| v7.24-draft | LLM Wiki M184 + T189-T190 + P9 MVE + M176/M178对接 | 3e8a693 |
| v7.23 | E2E归约+宇宙音律+自举智能 M181-M183 + T183-T188 + P8 MVE | f7a04e7 |
| v7.22 | EqProp+FHN M180 + T180-T182 + P7 MVE | — |
| v7.21 | TYIDO MVE + P6 Minkowski因果性 6/6 PASS | d55c608 |
| v7.20 | 太一接口 M179 + TY/IDO审计 73/73 PASS | — |
| v7.19 | 组织记忆·Φ场·AgentOS M176-M178 + T157-T165 | — |
| v7.18 | 沙箱+安全护盾 M174-M175 + T151-T156 | — |

## 当前开发状态：v7.27（✅完成）
- **M191 金灵球堆垒引擎** (~800行): 堆垒算子/三才五行映射/金灵球生成/β归约桥接
- **M192 太极延拓** (~500行): 延拓公理/同伦延拓/Φ场延拓/因果延拓
- **M193 Φ调度器** (~300行): Φ场预算/资源调度/优先级仲裁/三级调度
- **M194 碳硅GAN** (~350行): 生成器/判别器/对抗训练/碳硅桥接
- **M195 世界模型子系统** (~350行): ⟨W,S,C⟩三元组/世界帧/感知模拟/因果推理
- T201-T217 共17定理, v727 API 14端点, 前端5面板
- Git commit 待手动执行（沙箱D: drive index.lock限制）
- **待集成**: agency-agents-zh(223专家), _understand_anything_ref(UA能力)
- **待实现**: M190 v2/v3增强, M196 UA引擎

## 编号规则
- 模块: M195(v7.27) | M190(v7.26) | M189(v7.25b) | M186-M188(v7.25) | M184(v7.24) | M181-M183(v7.23) | M180(v7.22)
- 定理: T201-T217(v7.27) | T197-T200(v7.26) | T191-T196(v7.25b) | T189-T190(v7.24) | T183-T188(v7.23) | T180-T182(v7.22)

## 核心文件
- `M195_WorldModelSubsystem.py`: 世界模型子系统 ⟨W,S,C⟩ (v7.27)
- `M194_CarbonSiliconGAN.py`: 碳硅GAN 对抗训练 (v7.27)
- `M193_PhiScheduler.py`: Φ场调度器 三级调度 (v7.27)
- `M192_TaijiContinuation.py`: 太极延拓 同伦延拓 (v7.27)
- `M191_JinlingSphereEngine.py`: 金灵球堆垒引擎 (v7.27)
- `M190_AkashaChainDB.py`: 阿卡西链式数据库（v7.26核心，FTEL+β归约+POP共识）
- `M189_PowerLawEngine.py`: 幂律·对数·三分损益引擎（v7.25b核心）
- `M188_IntentionalityEngine.py`: 意向性+Curry-Howard类型论 (v7.25b)
- `M187_ContextRotDetector.py`: ContextRot+对数压缩+稀疏注意力 (v7.25b)
- `DIKWPReliabilityLayer.py`: BFT+三分损益同源+逗号补偿 (v7.25b)
- `CompositeAGI_V2.py`: 主核心（v5.0+）
- `M184_LLMWikiEngine.py`: LLM Wiki引擎（含OrgMemoryBridge + WikiEventBus）
- `M186_RLMEngine.py`: 递归语言模型引擎
- `expert_registry.py`: 223位AI专家注册表（解析agency-agents-zh/）

## API版本模式
- `/api/v727/*`: M191-M195 | `/api/v726/*`: M190 AkashaChainDB | `/api/v725b/*`: M189 幂律+三分损益+类型论
- `/api/v725/*`: M186-M188 | `/api/v724/*`: M184 Wiki
- `/api/v723/*`: M181-M183 | `/api/v722/*`: M180
- `/api/chat_v2`: 主对话 | `/api/experts`: 专家系统

## 服务启动
```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1 && python app.py
# 访问 http://127.0.0.1:5001/static/index_agi12.html
```

## M176/M178 接口速查
- `OrgMemoryEngine.remember(agent_id, content, memory_type, tags, confidence)` — 写入
- `OrgMemoryEngine.recall(query, top_k)` — 返回 `[{'entry': {...}, 'similarity': float}]`
- `TaiyiAgentOS.message_bus.send(sender_id, receiver_id, topic, payload)` — 发送
- `TaiyiAgentOS.message_bus.register_queue(agent_id)` — 注册队列
- 广播：`receiver_id="*"` — 发送给所有注册队列（除sender自身）

## 重要Bug记录
- `_to_native` 不处理 dataclass → 用 `asdict()` 转换，`@property` 需手动补全
- M181 类名：`EndToEndReductionEngine`（非`E2EReductionEngine`）
- M176 recall 返回结构：`{'entry': {'content':..., 'memory_type':...}, 'similarity': float}`
- Python 3.10不支持f-string内反斜杠
- M176/M177 API：memory_type需转枚举；M177 spend/earn参数是reason不是description
- M178 广播排除sender自身：`aid != sender_id` — WikiEventBus发出的广播不会投递回自己队列
- dataclass序列化：`_to_native()`无法处理dataclass，v7.23 diagnose/reduce/bootstrap_cycle路由均需asdict()

## 前端面板记录
- STN Phase 1-4 ✅ | v7.20太一接口 ✅ | v7.22 EqProp+FHN ✅
- v7.23 E2E归约/宇宙音律/自举智能/P8 MVE ✅
- v7.24 Wiki面板（M176/M178桥接徽章）✅
- v7.25b PowerLaw+Curry-Howard面板 ✅
- v7.26 AkashaChainDB+β归约面板 ✅
- v7.27 金灵球+太极延拓+Φ调度+碳硅GAN+世界模型面板 ✅
- 专家系统面板 ✅

## TYIDO MVE 踩坑
- P6 Minkowski度规：Kahn拓扑排序是同义反复，必须用Minkowski度规+洛伦兹不变性
- P1 J(R) 计算：deterministic pipeline必须返回固定canonical_hash
- EqPropTrainer死锁：`threading.Lock()`不可重入，移除内部方法中的`with self._lock`

## M133+M191 β-Rewire 踩坑
- **Y-combinator Python严格求值**: `y_kernel(ice_fn, state) = ice_fn(λs.y_kernel(ice_fn,s))(state)` 会RecursionError，因为_correct末尾调self_ref(state)触发无限展开。修复：y_kernel改为单步应用`ice_fn(identity)(state)`，递归由run_cycle外部迭代承担
- **Laplacian纯Python实现**: 不依赖numpy，用幂迭代+deflation+shift-invert，k=5特征值足够做谱跳变检测

## TY/IDO 审计基础设施
- `TYIDO_SelfConsistency.py`: P1 | `TYIDO_ContinuousLearning.py`: P2
- `TYIDO_LongRangeReasoning.py`: P3 | `TYIDO_AddressableMemory.py`: P4 | `TYIDO_AnchorableResponsibility.py`: P5

## v7.19 GC代币体系
- M176: 每Agent初始1000 GC | M175: BLOCK:50/FLAG:20/MASK:5 GC扣罚
- M177: 四级资源，Φ值比例分配，生存焦虑指数A=1/(1+e^(GC/λ))
