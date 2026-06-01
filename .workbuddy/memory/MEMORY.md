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
| v7.32 | M207-M217十一引擎+bp_v732/b API+16篇微信文章升级 | f9483c0 |
| v7.31 | M133-Wintel True-TaiyiAGI Candidate (W1-W5, P18-P20) | 5c08a9f |
| v7.30 | M190c UA集成（UABridge+语义查询+专家关联+时间旅行） | 212e3cc |
| v7.29 | M190b 性能优化（分片索引+WAL+布隆过滤器+缓存） | 212e3cc |
| v7.28b | ExpertBridge深度集成（4通道匹配+上下文感知+聊天推荐） | 7517981 |
| v7.27 | 太极OS·流锻内核 M191-M195 + T201-T217 | 待提交 |
| v7.26 | AkashaChainDB M190 + FTEL+β归约+POP共识 + T197-T200 | 7248b42 |

## 当前开发状态：v7.32（✅已提交 f9483c0）
- **M207 GoldenSymbol3D**: 金符3D复广数 z=a+bi+cj, 阴龙积⊙, MNQ8Grid | T212+T213
- **M208 TianxingPhaseLock**: 天行相位选择算子Π̂_φ, 波粒二象坍缩, oloid微分 | T211+T214
- **M209 AmbiguityEngine**: G_ambig歧义群, 延迟坍缩, L5投影基数 | T209+T210
- **M210 QianmenEightGeneral**: 千门八将8类EML偏离, ΔS量化, 显隐互转 | T215+T216
- **M211 HexaSysSOP**: 六合统合7步SOP引擎, Ftel密度追踪 | T217+T218
- **M212 BloomIdolFreezeEngine**: 偶像化伪共识冻结, Ω外源Reset, 共振成核 | T227+T228+OrphanReclaim
- **M213 EccentricityGovernance**: 偏心率定理, 大圆满单位圆, 组织寿命 | T229+T230
- **M214 GoedelEscapeHatch**: 哥德尔洞, 显密双轨, 遁甲反脆弱 | T231+T232
- **M215 ErosSynthemeEngine**: Eros内源奖励, 统感涌现, HyMemory六层 | T233+T234+HyMemory
- **M216 LiuPenaltyField**: 刘罚项场, 构成势极值, 艺术极值定理 | T235+T236+T237
- **M217 ArtificialFasciaEmbodiment**: 人工筋膜, 软L2壳, 具身自举 | T238+T239
- API: bp_v732 (10路由 /api/v732/*) + bp_v732b (12路由 /api/v732b/*)

## 编号规则
- 模块: M217(v7.32) | M207-M211(v7.32首批) | M191-M195(v7.27) | M190(v7.26) | M189(v7.25b)
- 定理: T227-T239(v7.32) | T209-T218(v7.32首批) | T201-T217(v7.27) | T197-T200(v7.26)

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
- M178 广播排除sender自身：`aid != sender_id`
- dataclass序列化：`_to_native()`无法处理dataclass，需asdict()
- **Git沙箱限制**: `.git/index.lock`被沙箱阻断，用`GIT_INDEX_FILE=/tmp/taiyi_index`绕过
- **M215 T234**: SynthemeMonitor测统感涌现需用独立monitor，避免低φ模态拉低聚合
- **M215 HyMemory**: consolidate()一次推到底层，需用consolidate_one_step(src, dst)单步巩固
- **M217 DefaultLayers**: 相邻层杨氏模量比值不能超过10倍，否则力学匹配检验失败

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
