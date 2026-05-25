"""
M184 LLM Wiki 知识引擎 — 架构设计文档
================================================
版本：v7.24-draft
来源：drpang.ai《RAG 之后：LLM Wiki 正在成为个人知识库的新范式》
对接模块：M176 OrgMemoryEngine（RAG→Wiki升级）、M178 AgentOS（事件驱动更新）

## 一、范式跃迁定义

### RAG 范式（当前 M176）
- 输入：用户提问
- 过程：向量检索 top-K 片段 → LLM 生成答案
- 输出：一次性答案
- 缺陷：知识不积累、跨文档关系丢失、结果不可复用

### LLM Wiki 范式（M184 目标）
- 输入：文档/聊天记录/代码/网页（持续流入）
- 过程：
    1. 抽取概念/主题 → 生成 WikiPage（Markdown）
    2. 建立 WikiPage 之间的双向链接（[[page_id]]）
    3. 新资料流入 → 更新已有页面（增量，非重建）
    4. 维护 WikiGraph（页面拓扑 + 引用计数 + 新鲜度）
- 输出：持续生长的知识网络
- 优势：知识积累、关系可追溯、跨时间一致、可审计

## 二、核心数据结构

### WikiPage（对应 M176 MemoryEntry 的升级版）
```python
@dataclass
class WikiPage:
    page_id: str                # 唯一ID（概念名规范化）
    title: str                   # 人类可读标题
    content: str                 # Markdown 正文
    links: List[str] = []       # 出链 page_id 列表
    backlinks: List[str] = []   # 入链 page_id 列表（自动维护）
    tags: List[str] = []        # 标签
    source_docs: List[str] = [] # 来源文档路径/URL
    created_at: float
    updated_at: float
    version: int = 1            # 页面版本号（增量更新计数）
    verification_status: str = "unverified"  # unverified/verified/refuted
    theorem_ids: List[str] = [] # 关联的定理ID（T1-T188）
    module_ids: List[str] = []  # 关联的模块ID（M1-M184）
```

### WikiGraph（知识图谱拓扑）
```python
class WikiGraph:
    pages: Dict[str, WikiPage]       # page_id → WikiPage
    adjacency: Dict[str, Set[str]]    # 有向边集（page_id → {link_ids}）
    reverse_adj: Dict[str, Set[str]] # 反向边（自动维护 backlinks）
    theorem_index: Dict[str, List[str]] # theorem_id → [page_id, ...]
    module_index: Dict[str, List[str]] # module_id → [page_id, ...]
```

## 三、核心类设计

### LLMWikiEngine（主引擎）
```python
class LLMWikiEngine:
    """LLM Wiki 知识引擎 — RAG→Wiki 范式跃迁"""

    def __init__(self, org_memory=None, agent_os=None):
        self.graph = WikiGraph()
        self.org_memory = org_memory      # 对接 M176（可选）
        self.agent_os = agent_os          # 对接 M178 MessageBus（可选）
        self._lock = threading.Lock()

    # ---- 核心 API ----
    def ingest(self, doc: str, source: str = "") -> IngestResult:
        """
        摄入一篇文档，执行完整 Wiki 更新流程：
        1. extract_concepts()    → 抽取概念列表
        2. match_or_create()     → 匹配已有页面 or 创建新页面
        3. generate_page_content()→ 生成/更新 Markdown 内容
        4. extract_links()       → 抽取页面间链接
        5. update_graph()        → 更新 WikiGraph 拓扑
         return IngestResult(pages_created, pages_updated, links_added)
        """

    def query(self, question: str, mode: str = "wiki") -> QueryResult:
        """
        查询接口（兼容 RAG 模式）：
        - mode="rag": 传统 RAG（检索片段 → 生成答案）
        - mode="wiki": Wiki 模式（读取相关页面 → 综合答案）
        - mode="hybrid": RAG + Wiki 混合
        """

    def get_page(self, page_id: str) -> Optional[WikiPage]: ...
    def get_backlinks(self, page_id: str) -> List[str]: ...
    def get_related_pages(self, page_id: str, max_hops: int = 2) -> List[str]: ...
    def verify_page(self, page_id: str, status: str, theorem_id: str = "") -> bool: ...
```

### ConceptExtractor（概念抽取器）
```python
class ConceptExtractor:
    """从文档中抽取概念/主题，输出标准化概念名列表"""
    def extract(self, doc: str) -> List[Concept]:
        """
        1. LLM 调用：抽取关键概念（名称 + 定义 + 关系）
        2. 规范化：去重、合并近义词（基于嵌入相似度）
        3. 返回 Concept(name, definition, related)
        """
```

### PageGenerator（页面生成器）
```python
class PageGenerator:
    """为概念生成/更新 WikiPage Markdown 内容"""
    def generate(self, concept: Concept, existing_page: Optional[WikiPage],
                source_doc: str) -> str:
        """
        生成 Markdown 格式页面：
        - 标题：# 概念名
        - 定义：简明定义（1-3句）
        - 详细说明：展开描述
        - 与其他概念的关系：[[相关概念]] 链接
        - 来源：> 来源：source_doc
        - 关联定理：{{T183}} 格式（可点击跳转）
        - 关联模块：{{M181}} 格式
        """
```

### LinkExtractor（链接抽取器）
```python
class LinkExtractor:
    """从页面内容中抽取 [[page_id]] 链接，并更新 WikiGraph"""
    def extract_links(self, page: WikiPage) -> List[str]: ...
    def update_backlinks(self, page_id: str, new_links: List[str]) -> None: ...
```

### IncrementalUpdater（增量更新器 — 核心差异点）
```python
class IncrementalUpdater:
    """
    LLM Wiki 的核心优势：新资料不是重建页面，而是增量更新
    """
    def update_page(self, page: WikiPage, new_info: str, source: str) -> WikiPage:
        """
        增量更新逻辑：
        1. 读取已有 content
        2. LLM 调用：将 new_info 融合到已有内容
           - 补充新细节 → 插入对应段落
           - 修正错误 → 标注 [[需要验证]]
           - 新增反例 → 添加反例段落
        3. 更新 updated_at, version += 1, source_docs.append(source)
        4. 返回更新后的 WikiPage
        """
```

## 四、定理设计（T189-T190）

### T189 — LLM Wiki 知识积累定理
```
陈述：
  在 LLM Wiki 范式下，经过 N 次文档摄入后，
  知识库中的有效知识单元数 K(N) 满足：
    K(N) ≥ K_RAG(N)
  其中 K_RAG(N) 是同等条件下 RAG 范式的有效知识单元数。
  且当 N→∞ 时，K(N) → K_max（知识图谱饱和），
  而 K_RAG(N) 受限于上下文窗口，存在上限瓶颈。

形式化：
  ∀N, K_Wiki(N) = |{p ∈ Pages : p.verification_status ≠ "refuted"}|
  K_RAG(N) = |{chunk ∈ RetrievalCorpus : chunk ∈ ContextWindow(N)}|
  ⇒ K_Wiki(N) ≥ K_RAG(N)
  ∧ lim(N→∞) K_Wiki(N) = K_max > K_RAG_max

验证方法：
  1. 构造 N=10/50/100/500 次文档摄入实验
  2. 分别用 RAG 和 Wiki 范式构建知识库
  3. 在 20 个保留问题上测试回答准确率 + 知识覆盖率
  4. 验证 K_Wiki(N) > K_RAG(N) 且差距随 N 扩大
```

### T190 — Wiki 增量更新收敛定理
```
陈述：
  LLM Wiki 的增量更新机制保证：
  对于任意页面 p，经过 N 次相关文档摄入后，
  p 的内容收敛到稳定状态（version 增量趋近0，
  或内容编辑距离 < ε），且不会因重复摄入而退化。

形式化：
  ∀p ∈ Pages, ∃N_p, ∀n > N_p:
    edit_distance(p_v(n), p_v(n-1)) < ε
  ∧ consistency_score(p_v(n)) ≥ consistency_score(p_v(n-1))

验证方法：
  1. 对同一概念摄入 10 次相似但不同角度的文档
  2. 测量每次更新后的内容编辑距离和一致性评分
  3. 验证编辑距离随版本数增加趋近0（收敛）
  4. 验证一致性评分不下降（非退化）
```

## 五、P9 MVE 实验设计

### P9-M184-T189：知识积累对比实验
```python
class P9_T189_KnowledgeAccumulationExperiment(MVExperiment):
    """
    对比 RAG vs Wiki 范式的知识积累能力
    指标：准确率、知识覆盖率、跨文档推理正确率
    """
    def run(self) -> MVResult:
        # 1. 准备 50 篇相关文档（太乙AGI论文/文章）
        # 2. RAG 组：依次摄入，每次只检索 top-K 片段回答
        # 3. Wiki 组：依次摄入，构建 WikiGraph，回答时读取相关页面
        # 4. 在 20 个保留问题上评估
        # 5. 验证：Wiki 组准确率 > RAG 组，且差距随文档数扩大
```

### P9-M184-T190：增量更新收敛实验
```python
class P9_T190_IncrementalConvergenceExperiment(MVExperiment):
    """
    验证 Wiki 增量更新机制的收敛性
    """
    def run(self) -> MVResult:
        # 1. 选定一个概念页面（如 "E2E归约"）
        # 2. 摄入 10 次相关但角度不同的文档
        # 3. 记录每次更新后的编辑距离和一致性评分
        # 4. 验证：编辑距离趋近0，一致性不下降
```

## 六、API 设计（对接 app.py）

### 新增路由组：`/api/v724/wiki/*`
```
GET  /api/v724/wiki/state           # 引擎状态
GET  /api/v724/wiki/page/<pid>     # 获取页面
POST /api/v724/wiki/ingest         # 摄入文档
GET  /api/v724/wiki/query          # 查询（wiki/rag/hybrid）
GET  /api/v724/wiki/graph          # 获取知识图谱拓扑
GET  /api/v724/wiki/backlinks/<pid> # 获取反向链接
POST /api/v724/wiki/verify         # 验证页面（关联定理）
GET  /api/v724/wiki/theorem/<tid> # 获取定理关联的页面
GET  /api/v724/wiki/mve/p9         # 运行 P9 MVE
GET  /api/v724/wiki/theorem/<tid> # T189/T190 定理验证
```

## 七、前端面板设计（index_agi12.html）

### v724-wiki-panel（LLM Wiki 知识引擎面板）
```
位置：v723 面板之后
 UI 组件：
  - 📚 摄入按钮：选择文档/粘贴文本 → 触发 ingest()
  - 🔍 查询模式切换：RAG / Wiki / Hybrid
  - 📄 页面浏览器：显示所有 WikiPage 卡片（标题+标签+更新时间）
  - 🕸️ 知识图谱可视化（Canvas）：节点=页面，边=链接
  - 📊 对比面板：RAG vs Wiki 准确率对比图（P9 实验结果）
  - ✅ 验证面板：页面验证状态（关联定理 T189/T190）
```

## 八、对接现有模块

### 对接 M176 OrgMemoryEngine
- M176 的 MemoryEntry → 可升级为 WikiPage（向后兼容）
- OrgMemoryEngine 的 query() → 可切换 rag/wiki/hybrid 模式
- FailureCaseLibrary → 对应 WikiPage.verification_status = "refuted"

### 对接 M178 AgentOS MessageBus
- 文档摄入可作为 Agent 消息广播
- Wiki 更新事件通知相关 Agent（订阅机制）
- Agent 可查询 Wiki 获取共享知识

### 对接 chat_v2（太乙AGI主对话）
- 对话历史 → 自动摄入 Wiki（增量）
- 回答时读取相关 Wiki 页面（增强上下文）
- 新发现 → 自动创建/更新 Wiki 页面

## 九、实现优先级

P0（本次必须完成）：
  [x] 架构设计文档（本文）
  [ ] M184_LLMWikiEngine.py 核心实现
  [ ] T189/T190 定理验证
  [ ] P9 MVE 实验
  [ ] app.py 路由集成
  [ ] 前端 v724-wiki-panel

P1（后续迭代）：
  [ ] 对接 M176 OrgMemoryEngine（升级现有记忆）
  [ ] 对接 M178 AgentOS MessageBus（事件驱动）
  [ ] 对接 chat_v2（对话历史自动摄入）
  [ ] Wiki 页面版本管理（diff/rollback）
  [ ] 敏感信息清理（PII 过滤）
```
