# PRD: 太乙AGI v7.25 — Understand Anything 吸纳

| 项目 | 内容 |
|------|------|
| **Language** | 中文 |
| **Programming Language** | Python (Flask + React + MUI + Tailwind CSS) |
| **Project Name** | `taiyi_agi_v725_understand_anything` |
| **版本** | v7.25 (从 v7.24-draft 升级) |
| **原始需求** | 将开源项目 Understand Anything (UA, v2.7.3, 25.9k stars) 的核心能力概念移植+Python重实现到太乙AGI，升级 M184 WikiGraph 从 1节点1边类型 到 21节点35边类型的富类型知识图谱，新增7个专用专家、8个 API 端点、Tree-sitter 代码分析、学习路径引导和3种 Dashboard 视图 |

---

## 产品定义

### Product Goals

1. **升级知识图谱 Schema 到富类型系统**：将 M184 WikiGraph 从单一 WikiPage+links/backlinks 升级为 21种节点类型 + 35种边类型（8大类），同时保留太乙AGI 特有的 theorem_ids/module_ids/verification_status 扩展字段
2. **实现确定性代码结构分析**：通过 Python tree-sitter 绑定替代 UA 的 TypeScript tree-sitter，为太乙AGI 的 184 个 Python 模块提供 import/export/function/class/inheritance 的确定性提取，消除纯 LLM 分析的不确定性
3. **构建引导式学习与领域分析能力**：将 UA 的 Tour（学习路径）和 Domain（业务领域建模）能力引入太乙AGI，使新用户可通过引导式步骤理解系统架构，研究者可按领域（L1-L5 层/定理链/模块依赖）浏览知识图谱

### User Stories

1. **As a** 太乙AGI 新开发者，**I want** 通过引导式学习路径（TourStep）逐步理解 184 模块的架构分层 **so that** 我能在 1 小时内掌握系统全貌而不是迷失在代码海洋中
2. **As a** 复合体理学研究者，**I want** 在知识图谱中按"领域"节点（如"L2-shell硬化"、"TY/IDO归约"）浏览相关定理和模块 **so that** 我能快速定位跨模块的理论关联
3. **As a** 太乙AGI 系统运维，**I want** 通过 Dashboard 的结构图视图实时查看 184 模块的依赖关系和调用链 **so that** 我能评估某个模块升级的影响范围
4. **As a** 代码贡献者，**I want** 使用 tree-sitter 确定性分析自动提取函数签名、类继承和 import 关系 **so that** 知识图谱的代码节点不需要手动维护且零幻觉
5. **As a** 知识工程师，**I want** Wiki 文章中的实体(entity)、主张(claim)、来源(source)自动提取并建立 cites/contradicts/builds_on 边 **so that** 论文间的理论关联可以被图谱查询而非人工记忆

---

## 技术规范

### Requirements Pool

#### P0 — 必须有（Must Have）

| # | 需求 | 详细描述 | 依赖 |
|---|------|----------|------|
| P0-1 | **M185 UnderstandEngine** | 吸纳 UA 核心的新模块，包含 5 个核心组件：① `EnhancedGraphNode`（21种节点类型 + DomainMeta + KnowledgeMeta + 太乙扩展字段 theorem_ids/module_ids/verification_status）；② `EnhancedGraphEdge`（35种边类型 + direction[forward/backward/bidirectional] + weight[0-1] + description）；③ `GraphSchemaValidator`（Python dataclass 验证 + alias 规范化 + autoFix 逻辑 + referential integrity 检查，移植 UA schema.ts 的 4 层验证管线：sanitize→normalize→autoFix→validate）；④ `TreeSitterParser`（Python tree-sitter 绑定，支持 Python 代码的 import/export/function/class/inheritance 确定性提取，输出 FunctionFingerprint/ClassFingerprint/ImportFingerprint/FileFingerprint）；⑤ `UnderstandOrchestrator`（编排 7 个分析专家的流水线：scan→analyze→architecture→domain→article→review→tour） | tree-sitter Python pkg, M184, M176, M178 |
| P0-2 | **7个新专家** | 在 `agency-agents-zh/understand/` 目录下新增 7 个专家 Markdown 文件，格式与现有 ExpertConfig 一致（YAML frontmatter + 正文），注册到 ExpertRegistry：① `understand-scanner` — 项目扫描（目录结构、技术栈、入口文件）；② `understand-analyzer` — 代码结构提取（函数签名、类继承、模块关系）；③ `understand-architect` — 架构分层识别（L1-L5 层映射、模块分组）；④ `understand-tour-guide` — 学习路径生成（TourStep 排序、语言课程）；⑤ `understand-reviewer` — 图谱完整性验证（孤立节点、悬空边、覆盖度）；⑥ `understand-domain` — 业务域提取（domain/flow/step 建模）；⑦ `understand-article` — Wiki 文章分析（entity/claim/source 提取 + cites/contradicts 边） | expert_registry.py |
| P0-3 | **API 路由 `/api/v725/understand/*`** | 8 个端点映射 UA 的 8 个命令：① `POST /api/v725/understand/scan` — 项目扫描（→understand-scanner）；② `POST /api/v725/understand/analyze` — 代码分析（→understand-analyzer + TreeSitterParser）；③ `GET /api/v725/understand/explain?node_id=` — 节点解释；④ `POST /api/v725/understand/diff` — 变更分析（fingerprint 对比）；⑤ `POST /api/v725/understand/onboard` — 新人引导（→tour 步骤生成）；⑥ `POST /api/v725/understand/domain` — 领域分析（→domain/flow/step）；⑦ `POST /api/v725/understand/knowledge` — 知识提取（→article 分析）；⑧ `GET /api/v725/understand/chat?q=` — 图谱问答 | M185, app.py |
| P0-4 | **M184 桥接** | M185 的分析结果可写入 M184 WikiGraph，需实现 `GraphNode→WikiPage` 映射器：① `EnhancedGraphNode` 的 `article`/`concept` 类型 → `WikiPage`（content 取 knowledgeMeta.content，tags 合并，theorem_ids/module_ids 透传）；② `EnhancedGraphEdge` 的 cites/related/builds_on → WikiPage links/backlinks；③ `EnhancedGraphNode` 的非 Wiki 类型（file/function/class 等）→ 写入 WikiPage.content 的结构化 Markdown 表格（标题+签名+摘要），关联 module_ids；④ 桥接通过 WikiEventBus 发布 `graph_node_synced` 事件 | M184, M185 |

#### P1 — 应该有（Should Have）

| # | 需求 | 详细描述 | 依赖 |
|---|------|----------|------|
| P1-1 | **前端面板：Understand Dashboard** | 在 `index_agi12.html` 新增 "Understand" Tab，含 3 种视图：① **结构图视图**（D3.js force-directed graph）— 节点按 21 种类型着色，边按 8 大类别着色，支持缩放/拖拽/搜索/筛选；② **领域图视图**（domain/flow/step 层级树 + cross_domain 边高亮）；③ **知识库图视图**（article/entity/topic/claim/source 子图 + cites/contradicts/builds_on 边）。共用组件：节点详情弹窗（含 summary/tags/complexity/theorem_ids/module_ids/verification_status）、学习路径侧边栏（TourStep 步进器） | P0-1, P0-3 |
| P1-2 | **RLM 算子集成到 M184** | M184 `query()` 方法增加 4 个 RLM 算子调用路径：① `_peek_search(query)` — 结构化查看（调用 UnderstandOrchestrator.peek 获取节点结构概览）；② `_grep_search(query, pattern)` — 关键词/正则过滤（在节点 summary/tags/content 中匹配）；③ `_partition_search(query, strategy)` — 分块搜索（按 domain/layer/complexity 分组返回）；④ `_recursion_search(query, depth_limit=3)` — 递归分解搜索（对复杂节点递归展开子图）。保留 `_keyword_search` 作为 fallback | M185, M184 |
| P1-3 | **Context Rot 检测器** | 新增 `ContextRotDetector` 模块（M186），核心公式：SNR = \|R(Φ_L1)\| / \|Φ_L1 - R(Φ_L1)\|。输入：L1 流噪声 Φ（M106），经 L2-shell 归约 R() 后的残差。输出：SNR 值 + 衰退等级（HEALTHY/DEGRADED/CRITICAL）。SNR < θ_critical 时触发 `context_rot_alert` 事件至 WikiEventBus。API: `GET /api/v725/context-rot/snr` | M106, M180 |
| P1-4 | **IntentionalityEngine** | 新增 `IntentionalityEngine` 模块（M187），实现 Noesis/Noema 形式化。Noesis = IDO 归约执行过程；Noema = 归约产物 ν，受 L2-shell 五属性约束。核心方法：`execute_noesis(input_flow) → Noema`；`validate_intentionality(noema) → IntentionalityVerdict`。L2-shell 映射：一致性=M88, 可保持=M78, 可寻址=M176, 可锚定=M175, 可回写=M118(partial)。API: `POST /api/v725/intentionality/execute`, `GET /api/v725/intentionality/validate` | M181, M88, M78, M176, M175, M118 |

#### P2 — 可以有（Nice to Have）

| # | 需求 | 详细描述 | 依赖 |
|---|------|----------|------|
| P2-1 | **多语言 Tree-sitter** | TreeSitterParser 扩展支持 JS/TS/Go/Java/Rust，通过 language-registry 配置加载对应 .so 语法库。UA 原生支持 TS/JS，Python 版本需通过 `tree_sitter.Language` 加载编译好的 .so 文件 | P0-1 |
| P2-2 | **语义搜索** | embedding-based search：对节点 summary/content 生成 embedding 向量，存入向量数据库（复用 M176 或 FAISS），支持余弦相似度搜索。API: `POST /api/v725/understand/semantic-search` | P0-1, 向量DB |
| P2-3 | **自动 Diff 分析** | Git commit hook 触发 understand-diff：post-commit 钩子自动对比 fingerprint 变更，结构性变更自动更新图谱节点，通过 WikiEventBus 发布 `graph_updated` 事件 | P0-1, P0-3 |

---

### UA Schema → 太乙AGI Python Dataclass 映射详解

#### 节点类型（21种 → Python Enum）

```python
class NodeType(Enum):
    # 代码节点 (5)
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    CONCEPT = "concept"
    # 非代码节点 (8)
    CONFIG = "config"
    DOCUMENT = "document"
    SERVICE = "service"
    TABLE = "table"
    ENDPOINT = "endpoint"
    PIPELINE = "pipeline"
    SCHEMA = "schema"
    RESOURCE = "resource"
    # 领域节点 (3)
    DOMAIN = "domain"
    FLOW = "flow"
    STEP = "step"
    # 知识节点 (5)
    ARTICLE = "article"
    ENTITY = "entity"
    TOPIC = "topic"
    CLAIM = "claim"
    SOURCE = "source"
```

#### 边类型（35种 → Python Enum，8大类）

```python
class EdgeCategory(Enum):
    STRUCTURAL = "structural"      # imports, exports, contains, inherits, implements
    BEHAVIORAL = "behavioral"      # calls, subscribes, publishes, middleware
    DATAFLOW = "dataflow"          # reads_from, writes_to, transforms, validates
    DEPENDENCIES = "dependencies"  # depends_on, tested_by, configures
    SEMANTIC = "semantic"          # related, similar_to
    INFRASTRUCTURE = "infrastructure"  # deploys, serves, provisions, triggers
    SCHEMA_DATA = "schema_data"    # migrates, documents, routes, defines_schema
    DOMAIN = "domain"              # contains_flow, flow_step, cross_domain
    KNOWLEDGE = "knowledge"        # cites, contradicts, builds_on, exemplifies, categorized_under, authored_by
```

#### GraphNode → WikiPage 桥接映射规则

| GraphNode.type | WikiPage 映射策略 |
|----------------|-------------------|
| `article` | 直接映射：content=knowledgeMeta.content, tags=原tags+["article"] |
| `concept` | 直接映射：content=summary, tags=原tags+["concept"] |
| `topic` | 直接映射：content=summary, tags=原tags+["topic"] |
| `claim` | 直接映射：content=summary, tags=原tags+["claim"] |
| `source` | 直接映射：content=summary, tags=原tags+["source"] |
| `entity` | 直接映射：content=summary, tags=原tags+["entity"] |
| `function`/`class`/`module` | 间接映射：生成结构化 Markdown 表格写入 WikiPage.content，关联 module_ids |
| `file`/`config`/`service`/... | 间接映射：生成摘要写入 WikiPage.content，关联 module_ids |
| `domain`/`flow`/`step` | 间接映射：领域描述写入 WikiPage.content，添加 domain 标签 |

---

### UI Design Draft

#### v7.25 Understand Dashboard（index_agi12.html 新增 Tab）

```
┌─────────────────────────────────────────────────────────────────────┐
│  太乙AGI v7.25  ─  顶部导航栏                                       │
│  [Dashboard] [Wiki] [Understand▼] [RLM] [Context Rot] [Intention]  │
├─────────────────────────────────────────────────────────────────────┤
│  Understand 子导航: [结构图] [领域图] [知识库图] [学习路径] [扫描]    │
├──────────────────────────────┬──────────────────────────────────────┤
│                              │                                      │
│  ┌─── 图谱视图 ──────────┐   │  ┌─── 节点详情 ──────────────────┐  │
│  │                       │   │  │  📦 M184_LLMWikiEngine        │  │
│  │   [D3.js Force Graph] │   │  │  类型: module                 │  │
│  │                       │   │  │  复杂度: ●●○ moderate          │  │
│  │   节点: ●file ●class  │   │  │  定理: T189, T190             │  │
│  │         ●module ●fn   │   │  │  模块: M184                   │  │
│  │         ●domain ●flow │   │  │  验证: ✅ verified             │  │
│  │         ●article ●... │   │  │  标签: [wiki] [rag] [知识库]  │  │
│  │                       │   │  │  ─────────────────────────    │  │
│  │   边: ──structural    │   │  │  依赖 (depends_on):           │  │
│  │       --behavioral    │   │  │    → M176 OrgMemoryEngine     │  │
│  │       ··dataflow      │   │  │    → M178 TaiyiAgentOS        │  │
│  │       ──knowledge     │   │  │  包含 (contains):             │  │
│  │                       │   │  │    → LLMWikiEngine class      │  │
│  │   [筛选: 类型▼ 层▼]   │   │  │    → WikiGraph class          │  │
│  │   [搜索: ________]    │   │  │    → ConceptExtractor         │  │
│  └───────────────────────┘   │  └──────────────────────────────┘  │
│                              │                                      │
│  ┌─── 学习路径 ─────────────────────────────────────────────────┐  │
│  │  Step 1/8: 项目概览 → 了解太乙AGI的TY/IDO五层架构            │  │
│  │  [◀ Prev]                                    [Next ▶]       │  │
│  │  当前节点: M172_TYFormalizer, M180_EqPropFHN, M181_E2E...  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Open Questions

| # | 问题 | 影响 | 建议 |
|---|------|------|------|
| OQ-1 | **tree-sitter Python 依赖**：Python tree-sitter 包 (`tree-sitter-python`) 需要 `.so` 编译文件，Docker/Windows 环境是否需要预编译？是否使用 `py-tree-sitter` 还是直接调用 tree-sitter CLI | P0-1 | 建议使用 `tree-sitter` Python 包（0.21+），启动时自动编译 `.so` 缓存到 `.tree_sitter_cache/`；备选方案为预编译 `.so` 随项目分发 |
| OQ-2 | **7个专家的 Prompt 来源**：UA 的 7 个 Agent 是 TypeScript 编排 + Markdown prompt，Python 重实现时专家 prompt 是否直接移植 UA 的 `.md` 文件内容，还是针对太乙AGI 的 184 模块特化 | P0-2 | 建议移植 UA prompt 作为基础，追加太乙AGI 特化指令（如"识别 TY/IDO 五层架构"、"关联 theorem_ids"） |
| OQ-3 | **GraphNode→WikiPage 双向同步**：当 M185 图谱节点更新时，是推式（实时同步到 M184）还是拉式（按需查询时桥接）？推式可能产生大量 WikiEventBus 事件 | P0-4 | 建议拉式为主 + 定时批量推送（每 5 分钟），大批量变更（如首次 scan）使用批量事件 |
| OQ-4 | **M185 模块编号**：当前最大模块编号 M184，新模块应为 M185。但 P1-3 (ContextRotDetector) 和 P1-4 (IntentionalityEngine) 也需要编号。是否按优先级分配：M185=UnderstandEngine, M186=ContextRotDetector, M187=IntentionalityEngine | 全局 | 建议按此编号分配，与 v7.25 版本对应 |
| OQ-5 | **UA 别名系统**：UA 有 NODE_TYPE_ALIASES (76个) 和 EDGE_TYPE_ALIASES (44个)，Python 版本是否完整移植？别名系统对 LLM 生成的不规范类型名有重要纠偏作用 | P0-1 | 建议完整移植，作为 GraphSchemaValidator.normalize() 的一部分 |
| OQ-6 | **UnderstandOrchestrator LLM 调用**：UA 的 Agent 编排依赖 Claude/GPT API 调用，太乙AGI 是使用现有 LLM 后端（local_llm.py）还是独立配置？7个专家是否需不同 LLM 模型 | P0-1 | 建议复用太乙AGI 现有 LLM 后端（local_llm.py / lm_studio_backend.py），通过 ExpertConfig.system_prompt 注入 UA 专用指令 |
