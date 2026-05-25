# 长期记忆（精简版 2026-05-25）

## 项目概览
**净光哥** 太乙AGI：Flask应用，位于 `C:\Users\1\WorkBuddy\2026-05-06-task-1\`
- 主服务器: `app.py` (Flask, 端口5001)
- 前端: `static/index_agi12.html` (三栏布局界面)
- 脑图: `app_mindmap_v2.py` (端口5003)
- **总规模**: 189模块 / 9层 / 196定理 / 216专家

## 版本历史（精简）

| 版本 | 内容 | Git |
|------|------|-----|
| v7.25b | 幂律·三分损益·类型论 M189 + BFT升级 + M187/M188升级 + T191-T196 | — |
| v7.25 | RLM M186 + ContextRot M187 + Intentionality M188 + T191-T196 | — |
| v7.24-draft | LLM Wiki M184 + T189-T190 + P9 MVE + M176/M178对接 | 3e8a693 |
| v7.23 | E2E归约+宇宙音律+自举智能 M181-M183 + T183-T188 + P8 MVE | f7a04e7 |
| v7.22 | EqProp+FHN M180 + T180-T182 + P7 MVE | — |
| v7.21 | TYIDO MVE + P6 Minkowski因果性 6/6 PASS | d55c608 |
| v7.20 | 太一接口 M179 + TY/IDO审计 73/73 PASS | — |
| v7.19 | 组织记忆·Φ场·AgentOS M176-M178 + T157-T165 | — |
| v7.18 | 沙箱+安全护盾 M174-M175 + T151-T156 | — |

## 当前开发状态：v7.25b（🔶开发中）
- **M189 PowerLawEngine** (~1600行): 幂律拟合/对数压缩/三分损益/2/3共识/非结合代数/Curry-Howard/稀疏注意力
- T191-T196 共6定理, MVE 8/8 ALL PASSED ✅
- BFT升级: 毕达哥拉斯逗号补偿机制 (T194)
- M187 升级: 对数压缩预处理 + 幂律稀疏注意力 ψ
- M188 升级: Curry-Howard意图映射 + 银弹定理T195
- API: /api/v725b/{powerlaw/*, consensus/bft, sanfen/cycle, curry_howard/map, silver_bullet, rot/sparse_attention, mve, theorem/*}
- 前端: ⚛️ PowerLaw面板 + 📐 Curry-Howard面板

## 编号规则
- 模块: M189(v7.25b) | M186-M188(v7.25) | M184(v7.24) | M181-M183(v7.23) | M180(v7.22)
- 定理: T191-T196(v7.25b) | T189-T190(v7.24) | T183-T188(v7.23) | T180-T182(v7.22)

## 核心文件
- `M189_PowerLawEngine.py`: 幂律·对数·三分损益引擎（v7.25b核心）
- `M188_IntentionalityEngine.py`: 意向性+Curry-Howard类型论 (v7.25b)
- `M187_ContextRotDetector.py`: ContextRot+对数压缩+稀疏注意力 (v7.25b)
- `DIKWPReliabilityLayer.py`: BFT+三分损益同源+逗号补偿 (v7.25b)
- `CompositeAGI_V2.py`: 主核心（v5.0+）
- `M184_LLMWikiEngine.py`: LLM Wiki引擎（含OrgMemoryBridge + WikiEventBus）
- `M186_RLMEngine.py`: 递归语言模型引擎

## API版本模式
- `/api/v725b/*`: M189 幂律+三分损益+类型论 | `/api/v725/*`: M186-M188
- `/api/v724/*`: M184 Wiki | `/api/v723/*`: M181-M183 | `/api/v722/*`: M180
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
- 专家系统面板 ✅

## TYIDO MVE 踩坑
- P6 Minkowski度规：Kahn拓扑排序是同义反复，必须用Minkowski度规+洛伦兹不变性
- P1 J(R) 计算：deterministic pipeline必须返回固定canonical_hash
- EqPropTrainer死锁：`threading.Lock()`不可重入，移除内部方法中的`with self._lock`

## TY/IDO 审计基础设施
- `TYIDO_SelfConsistency.py`: P1 | `TYIDO_ContinuousLearning.py`: P2
- `TYIDO_LongRangeReasoning.py`: P3 | `TYIDO_AddressableMemory.py`: P4 | `TYIDO_AnchorableResponsibility.py`: P5

## v7.19 GC代币体系
- M176: 每Agent初始1000 GC | M175: BLOCK:50/FLAG:20/MASK:5 GC扣罚
- M177: 四级资源，Φ值比例分配，生存焦虑指数A=1/(1+e^(GC/λ))
