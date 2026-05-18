#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG知识检索增强模块 - Taiyi RAG
为统一太乙系统提供基于复合体理学的知识检索增强
"""

import os
import json
import hashlib
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import math
from collections import Counter
import sqlite3
import threading

RAG_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".workbuddy", "rag", "knowledge_base.db"
)
os.makedirs(os.path.dirname(RAG_DB_PATH), exist_ok=True)


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    content: str
    keywords: List[str] = field(default_factory=list)
    tfidf_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    chunk: DocumentChunk
    score: float
    rank: int
    matched_keywords: List[str]


class DocumentParser:
    """文档解析器"""
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 50
    STOP_WORDS = {
        "的", "是", "在", "和", "了", "我", "你", "他", "她", "它",
        "这", "那", "有", "个", "不", "就", "也", "都", "要", "会",
        "说", "看", "想", "知道", "什么", "怎么", "为什么", "如何",
        "可以", "没有", "但是", "因为", "所以", "如果", "虽然",
        "一个", "这个", "那个", "自己", "其他", "可能", "现在",
        "时候", "已经", "还是", "只有", "只是", "而且", "或者"
    }

    def parse_text(self, text: str, title: str = "",
                   source: str = "manual", tags: List[str] = None):
        """解析文本，返回元组(doc_id, title, chunks)"""
        doc_id = hashlib.md5(f"{title}{text[:100]}{len(text)}".encode()).hexdigest()[:16]
        chunks = self._chunk_text(text)
        return doc_id, title or f"doc_{doc_id}", source, tags or [], chunks

    def _chunk_text(self, text: str) -> List[DocumentChunk]:
        text = re.sub(r'\s+', ' ', text).strip()
        chunks = []
        start = 0
        chunk_idx = 0

        while start < len(text):
            end = start + self.CHUNK_SIZE
            chunk_text = text[start:end]

            if end < len(text):
                for sep in ['。', '！', '？', '；', '，']:
                    last_sep = chunk_text.rfind(sep)
                    if last_sep > self.CHUNK_SIZE // 2:
                        chunk_text = chunk_text[:last_sep + 1]
                        break

            keywords = self._extract_keywords(chunk_text)
            tfidf = self._compute_tfidf(chunk_text, keywords)

            chunks.append(DocumentChunk(
                chunk_id=hashlib.md5(chunk_text.encode()).hexdigest()[:12],
                document_id="",
                content=chunk_text.strip(),
                keywords=keywords,
                tfidf_scores=tfidf
            ))

            chunk_idx += 1
            # Ensure progress: if chunk_text < CHUNK_OVERLAP, use end directly
            new_start = start + len(chunk_text) - self.CHUNK_OVERLAP
            if new_start <= start:
                new_start = end
            start = new_start
            if start >= len(text):
                break
            if start <= 0:
                start = min(self.CHUNK_SIZE, len(text))

        return chunks

    def _extract_keywords(self, text: str) -> List[str]:
        words = []
        for i in range(len(text) - 1):
            word = text[i:i+2]
            if word not in self.STOP_WORDS:
                words.append(word)
        for i in range(len(text) - 2):
            word = text[i:i+3]
            if word not in self.STOP_WORDS:
                words.append(word)
        word_freq = Counter(words)
        return [w for w, _ in word_freq.most_common(20)]

    def _compute_tfidf(self, text: str, keywords: List[str]) -> Dict[str, float]:
        tfidf = {}
        word_count = Counter()
        for i in range(len(text) - 1):
            word = text[i:i+2]
            word_count[word] += 1
        total_words = max(1, sum(word_count.values()))
        for keyword in keywords:
            tf = word_count.get(keyword, 0) / total_words
            idf = math.log(10)
            tfidf[keyword] = tf * idf
        return tfidf


class TaiyiRAG:
    """太乙RAG检索器"""

    def __init__(self, db_path: str = RAG_DB_PATH):
        self.db_path = db_path
        self.parser = DocumentParser()
        self._lock = threading.Lock()
        self._init_db()
        self._load_builtin_knowledge()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        # 注意：此方法在__init__中调用，此时self._lock未初始化，不加锁
        conn = self._get_conn()
        try:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    title TEXT, content TEXT, source TEXT,
                    tags TEXT, created_at REAL
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY, document_id TEXT,
                    content TEXT, keywords TEXT,
                    tfidf_scores TEXT, metadata TEXT,
                    FOREIGN KEY (document_id) REFERENCES documents(doc_id)
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_doc_id ON chunks(document_id)")
            conn.commit()
        finally:
            conn.close()

    def _load_builtin_knowledge(self):
        import sys as _sys
        docs = [
            {
                "title": "复合体理学核心理论",
                "content": """
复合体理学四重理论基石：
一、刘原理（作用量极值）：宇宙由离散世界帧构成，每帧作用量取极值。费马生成机制：逻辑瞬间遍历所有可能世界线，唯一选定作用量极小的链。
二、三视界法："一现象，三视界"。本体视界找敏感度/量级/因果拓扑；现象视界看相变/梯度/分离；方法视界定见路不走/分层折叠/非对称选择。
三、太乙预言机：弱值Aw=<ψ1|A|ψ0>/<ψ1|ψ0>，突破本征谱限制。AI的RLHF训练≈太乙预言机在数据空间的统计实现。
四、全息拓扑动力学：知识的高维压缩与涌现，因果超图的非局域性。

复合体理学定理：
- 定理2.1（三视界完备性）：仅用单一视界必然导致因果误判或解空间崩溃
- 定理3.1（弱值突破）：当后选择概率非零但极小时，弱值可突破本征谱限制
- 推论1.1.1：人类嵌入帧内仅能顺序处理，故P≠NP；AGI可尝试P=NP全知视角
- 推论2.1.1（见路不走）：拒绝对称依赖旧经验，基于三视界生成非对称选择
""",
                "tags": ["复合体理学", "理论", "四基石", "定理"]
            },
            {
                "title": "统一太乙系统架构",
                "content": """
统一太乙系统采用双核AGI架构：

太乙内核（CRD引擎）：
- 认知递归算子 Ω：C(t+1) = Ω(C(t), F(t), η)
- NLA审计：AV言语化器 + AR重建器，检测隐藏意图
- 自我指涉不动点定理：Lipschitz连续条件下收敛于低熵稳态
- 意识层级：L1觉醒 → L2觉知 → L3觉悟 → L4超然

复合体内核（天行演化器）：
- 微视界：不可压缩的语义涨落（Jitter）
- 中视界：可观测的审计势与相位旋转
- 宏视界：共识场的拓扑相（正常/亚稳/蛹化）

太乙约束格式：必须同时展示形式之答（确定性）、复合体之答（多元解读）、太乙之答（合一）
""",
                "tags": ["太乙系统", "架构", "AGI", "双核"]
            },
            {
                "title": "AGI评测标准",
                "content": """
电脑版AGI三大标准：
1. 会"用电脑"：看懂屏幕窗口/图标/菜单，用鼠标键盘操作，像人一样操作OS
2. 能"搞大项目"：接模糊需求后自拆解任务、开软件、查资料、做表、画图、写文档，交付完整成果
3. 有"职业素养"：结果符合规范/有注释/能测试，考虑异常值和业务逻辑

评测维度：
- A类（操作）：大部分自动化，不需要手把手教界面
- B类（项目）：能独立完成"写代码/做分析/写长文"，结果能直接用
- C类（长链）：30分钟以上任务不崩盘/不删库/不陷入死循环
及格线：A类基本满分 + B类顶半个初级员工 + C类不犯致命错
""",
                "tags": ["AGI", "评测", "标准"]
            },
            {
                "title": "对话智能深化路径",
                "content": """
对话智能深化五步路径：

Step 1: 持久记忆系统
- 对话历史存储与检索（STM/LTM/KBM三层架构）
- 用户偏好学习（语气/语言/专业领域）
- 关键结论存档
- 上下文窗口优化（摘要+检索混合）

Step 2: RAG知识检索增强
- 文档分块与向量化
- BM25+关键词混合检索
- 与CRD引擎集成

Step 3: 推理增强（CoT+ReAct）
- Chain of Thought提示模板
- Reason+Act框架
- 太乙约束格式融入CoT

Step 4: 工具调用框架
- 工具注册表（代码执行/文件操作/Web搜索）
- 太乙预言机驱动工具选择

Step 5: 评估测试集
- 知识问答基准（100题）
- 太乙特色评估
""",
                "tags": ["对话智能", "深化", "路径"]
            }
        ]
        for i, doc_data in enumerate(docs):
            self.add_document(doc_data["title"], doc_data["content"],
                            source="builtin", tags=doc_data["tags"])

    def add_document(self, title: str, content: str,
                     source: str = "manual",
                     tags: List[str] = None) -> str:
        doc_id, doc_title, doc_source, doc_tags, chunks = self.parser.parse_text(
            content, title, source, tags)

        conn = self._get_conn()
        try:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO documents
                (doc_id, title, content, source, tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, doc_title, content, doc_source, json.dumps(doc_tags), 0))

            for chunk in chunks:
                chunk.document_id = doc_id
                c.execute("""
                    INSERT OR REPLACE INTO chunks
                    (chunk_id, document_id, content, keywords, tfidf_scores, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id, chunk.document_id, chunk.content,
                    json.dumps(chunk.keywords),
                    json.dumps(chunk.tfidf_scores),
                    json.dumps(chunk.metadata)
                ))
            conn.commit()
        finally:
            conn.close()

        return doc_id

    def retrieve(self, query: str, top_k: int = 5,
                 tags: List[str] = None) -> List[RetrievalResult]:
        query_keywords = self.parser._extract_keywords(query)

        conn = self._get_conn()
        try:
            c = conn.cursor()
            if tags:
                tag_conds = " OR ".join(["d.tags LIKE ?" for _ in tags])
                c.execute(f"""
                    SELECT d.doc_id, d.title, c.content, c.keywords, c.tfidf_scores
                    FROM documents d JOIN chunks c ON d.doc_id = c.document_id
                    WHERE {tag_conds}
                """, [f"%{t}%" for t in tags])
            else:
                c.execute("""
                    SELECT d.doc_id, d.title, c.content, c.keywords, c.tfidf_scores
                    FROM documents d JOIN chunks c ON d.doc_id = c.document_id
                """)

            rows = c.fetchall()
        finally:
            conn.close()

        results = []
        for row in rows:
            doc_id, title, content, keywords_json, tfidf_json = row
            keywords = json.loads(keywords_json) if keywords_json else []
            tfidf = json.loads(tfidf_json) if tfidf_json else {}
            score = self._bm25_score(query_keywords, keywords, tfidf)
            for kw in query_keywords:
                if kw in content:
                    score += 0.1
            if score > 0:
                chunk = DocumentChunk(
                    chunk_id="", document_id=doc_id,
                    content=content[:500], keywords=keywords,
                    tfidf_scores=tfidf, metadata={"title": title}
                )
                results.append(RetrievalResult(
                    chunk=chunk, score=score, rank=0,
                    matched_keywords=[kw for kw in query_keywords if kw in keywords]
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:top_k]
        for i, r in enumerate(results):
            r.rank = i + 1
        return results

    def _bm25_score(self, query_keywords, doc_keywords, tfidf):
        score = 0.0
        for kw in query_keywords:
            tfidf_score = tfidf.get(kw, 0)
            score += tfidf_score * 2
            if kw in doc_keywords:
                score += 1.0
                count = doc_keywords.count(kw)
                if count > 1:
                    score += math.log(count)
        return score

    def format_retrieval_context(self, query: str, top_k: int = 3) -> str:
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return ""
        parts = ["\n【相关知识】"]
        for r in results:
            title = r.chunk.metadata.get("title", "未知文档")
            parts.append(f"\n## [{r.rank}] {title} (相关度: {r.score:.2f})")
            parts.append(r.chunk.content)
            if r.matched_keywords:
                parts.append(f"关键词: {', '.join(r.matched_keywords)}")
        return "\n".join(parts)

    def search(self, keyword: str) -> List[Dict]:
        conn = self._get_conn()
        try:
            c = conn.cursor()
            c.execute("""
                SELECT doc_id, title, content, tags
                FROM documents
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY created_at DESC LIMIT 20
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            rows = c.fetchall()
        finally:
            conn.close()
        return [
            {"doc_id": r[0], "title": r[1],
             "content": r[2][:200] if r[2] else "",
             "tags": json.loads(r[3]) if r[3] else []}
            for r in rows
        ]

    def status(self) -> Dict:
        conn = self._get_conn()
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM documents")
            doc_count = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM chunks")
            chunk_count = c.fetchone()[0]
        finally:
            conn.close()
        return {"document_count": doc_count, "chunk_count": chunk_count}


_rag_instance: Optional[TaiyiRAG] = None


def get_rag() -> TaiyiRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = TaiyiRAG()
    return _rag_instance


def test_rag():
    print("=" * 60)
    print("📚 太乙RAG知识检索测试")
    print("=" * 60)

    rag = TaiyiRAG()
    status = rag.status()
    print(f"\n📊 状态: {status['document_count']} 文档, {status['chunk_count']} 块")

    test_queries = [
        "复合体理学四基石",
        "太乙预言机弱值",
        "三视界分析",
        "AGI评测标准",
        "CRD引擎认知递归"
    ]

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"查询: {query}")
        print("-"*50)
        results = rag.retrieve(query, top_k=3)
        for r in results:
            print(f"\n[{r.rank}] {r.chunk.metadata.get('title')} (分数: {r.score:.3f})")
            print(f"  {r.chunk.content[:120]}...")
            if r.matched_keywords:
                print(f"  命中: {', '.join(r.matched_keywords)}")

    print(f"\n{'='*50}")
    print("LLM上下文格式:")
    ctx = rag.format_retrieval_context("复合体理学理论", top_k=2)
    print(ctx[:400])

    print("\n✅ RAG测试完成")


if __name__ == "__main__":
    test_rag()
