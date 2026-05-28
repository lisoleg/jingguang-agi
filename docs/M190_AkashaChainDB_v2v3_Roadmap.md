# M190 AkashaChainDB v2/v3 增强规划

> 基于当前 v7.26 v1 实现的后续升级路线图

## 当前状态 (v1)

| 指标 | 数值 |
|------|------|
| 代码行数 | 1664 |
| 核心类 | 9 (FTELMetrics, AkashaTriple, AkashaBlock, RelationIndex, AkashaLedger, POPConsensus, OrgMemoryBridge, AkashaChainDB, EntityProfile) |
| 定理 | T197-T200 |
| API 端点 | 6 (v726) |
| 持久化 | 内存 + OrgMemoryBridge → M176 |

## v2 性能优化 (M190b)

### 目标
- 10x 写入吞吐提升
- 5x 查询延迟降低
- 内存占用降低 50%

### 增强项

#### 2.1 分片 RelationIndex
- 当前: 单一 dict 内存索引，所有三元组存在一个 RelationIndex
- 改进: 按 predicate 类型分片，每个分片独立锁
- 预期: 写入并发度从 1 → N (分片数)
- 文件: `M190_AkashaChainDB.py` 内 `RelationIndex` 类重构

#### 2.2 WAL (Write-Ahead Log) 持久化
- 当前: 仅内存，重启丢失
- 改进: 追加式 WAL 文件 + 定期 checkpoint
- 与 AkashaLedger 的 append-only 设计天然契合
- 文件: 新增 `AkashaWAL` 类

#### 2.3 布隆过滤器加速查询
- 当前: 全表扫描做模糊匹配
- 改进: S/P/O 三组布隆过滤器，快速排除不存在的 key
- 依赖: `pybloom-live` 或自实现
- 文件: `AkashaBloomFilter` 工具类

#### 2.4 批量写入优化
- 当前: `write_triple()` 逐条写入
- 改进: `write_triples_batch()` 批量写入 + 延迟索引更新
- 与 `process_block()` β-归约联动
- 文件: `AkashaChainDB` 新增方法

#### 2.5 缓存层
- 热点查询 LRU 缓存
- FTEL 高频实体缓存
- 文件: `AkashaQueryCache` 类

### 新增定理
- **T222 — 分片等价定理**: 分片 RelationIndex 的查询结果与单一索引等价
- **T223 — WAL 完备定理**: WAL 回放后系统状态与崩溃前一致

### 预计工作量
- 代码变更: ~400 行新增
- 测试: T222-T223 + 性能基准测试
- 前端: 新增性能监控面板（QPS/P99延迟/内存占用）

---

## v3 UA 能力集成 (M190c)

### 目标
- AkashaChainDB 成为 UA (Understand Anything) 的结构化知识后端
- 支持 M196 知识图谱的持久化存储和查询
- 专家系统与链式数据库深度融合

### 增强项

#### 3.1 UA KnowledgeGraph ↔ AkashaTriple 双向转换
- `graph_to_triples()`: KnowledgeGraph.nodes + edges → AkashaTriple 批量写入
- `triples_to_graph()`: AkashaTriple 查询结果 → KnowledgeGraph 重建
- 支持知识图谱的增量快照和版本比较
- 文件: 新增 `UABridge` 类 (在 M196 或 M190 中)

#### 3.2 语义查询增强
- 当前: SPO 精确匹配 + FTEL 权重
- 改进: 1-hop/2-hop 语义扩展查询（与 M196 ContextBuilder 对齐）
- 支持自然语言 → SPARQL-like 查询转换
- 文件: `AkashaSemanticQuery` 类

#### 3.3 专家关联图谱
- 将 223 位专家的 expertise 存入 AkashaChainDB
- 支持基于关系路径的专家推荐（与 ExpertBridge 对齐）
- 例: 查询 "Python" → (Python, used_in, Flask) → (Flask, expert_in, Backend_Architect)
- 文件: `ExpertKnowledgeBridge` 类

#### 3.4 时光旅行查询
- 利用 AkashaLedger 的链式结构，支持历史时间点查询
- `query_at(block_height)`: 查询指定区块高度时的实体状态
- 与 M196 DiffAnalyzer 集成，支持知识图谱的历史对比
- 文件: `AkashaTimeTravel` 类

### 新增定理
- **T224 — UA-Akasha 等价定理**: 知识图谱通过 UA↔Akasha 转换后查询结果等价
- **T225 — 语义完备定理**: 语义扩展查询不产生原始查询不包含的结果
- **T226 — 时光一致性定理**: 历史查询结果与该时间点的实际状态一致

### 预计工作量
- 代码变更: ~600 行新增
- 测试: T224-T226 + UA 集成测试
- 前端: 新增知识图谱时间轴面板 + 语义查询面板

---

## 实施优先级

| 阶段 | 版本 | 优先级 | 预计时间 | 依赖 |
|------|------|--------|---------|------|
| v2.1 分片 RelationIndex | M190b | P0 | 1天 | 无 |
| v2.2 WAL 持久化 | M190b | P0 | 1天 | 无 |
| v2.3 布隆过滤器 | M190b | P1 | 0.5天 | pybloom-live |
| v2.4 批量写入 | M190b | P1 | 0.5天 | v2.1 |
| v2.5 缓存层 | M190b | P2 | 0.5天 | v2.1 |
| v3.1 UA 双向转换 | M190c | P0 | 1天 | M196 v7.28b |
| v3.2 语义查询 | M190c | P1 | 1天 | v3.1 |
| v3.3 专家关联 | M190c | P1 | 0.5天 | M196 ExpertBridge |
| v3.4 时光旅行 | M190c | P2 | 1天 | v2.2 WAL |

---

## 与太乙AGI全局路线图的对齐

```
v7.26 (当前): M190 AkashaChainDB v1 — 基础能力 ✅
v7.27: M191-M195 太极OS·流锻内核 ✅
v7.28: M196 万物理解引擎 (UA) ✅
v7.28b: M196 ExpertBridge 增强 ✅ (本次)
v7.29 (规划): M190b 性能优化 + 新增 T222-T223
v7.30 (规划): M190c UA集成 + 新增 T224-T226
v7.31+: HypergraphHoTT 形式化验证 → AkashaChainDB 理论证明增强
```

---

*Created: 2026-05-25 | Author: Qi (齐活林) · 太乙AGI主理人*
