#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持久记忆系统 - Taiyi Memory System
为统一太乙系统提供跨会话的持久化上下文管理

三层记忆架构：
- STM (Short-Term Memory): 会话级上下文（内存）
- LTM (Long-Term Memory): 持久化记忆（SQLite）
- KBM (Knowledge Base Memory): 知识库记忆（向量检索）

核心功能：
1. 对话历史存储与检索
2. 用户偏好学习
3. 关键结论存档
4. 上下文窗口优化（摘要+检索混合）
5. 太乙约束格式融合
"""

import json
import sqlite3
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import threading
import os

# ==================== 配置 ====================

MEMORY_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    ".workbuddy", "memory", "taiyi_memory.db"
)

# 确保目录存在
os.makedirs(os.path.dirname(MEMORY_DB_PATH), exist_ok=True)


# ==================== 数据结构 ====================

@dataclass
class ConversationTurn:
    """对话轮次"""
    turn_id: int
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class UserPreference:
    """用户偏好"""
    user_id: str
    preferred_tone: str = "专业"  # 专业/简洁/详细/学术
    preferred_language: str = "中文"
    expertise_domains: List[str] = field(default_factory=list)  # 专业领域
    interaction_style: str = "行动导向"  # 行动导向/分析导向/教学导向
    emoji_usage: bool = True
    last_updated: float = field(default_factory=time.time)


@dataclass
class KeyConclusion:
    """关键结论"""
    conclusion_id: str
    topic: str
    summary: str
    confidence: float
    source_conversation: str
    timestamp: float
    tags: List[str] = field(default_factory=list)
    is_validated: bool = False


@dataclass
class MemoryContext:
    """记忆上下文（传给LLM）"""
    session_history: List[Dict]  # 最近N轮对话
    relevant_memories: List[Dict]  # 检索到的相关记忆
    user_preference: Optional[Dict]  # 用户偏好
    key_conclusions: List[Dict]  # 相关结论
    context_summary: str  # 上下文摘要
    
    def to_llm_format(self) -> str:
        """转换为LLM可读的格式"""
        parts = ["【记忆上下文】"]
        
        # 用户偏好
        if self.user_preference:
            parts.append(f"用户偏好: {self.user_preference.get('preferred_tone', '专业')}风格")
            if self.user_preference.get('expertise_domains'):
                parts.append(f"专业领域: {', '.join(self.user_preference['expertise_domains'])}")
        
        # 相关记忆
        if self.relevant_memories:
            parts.append("\n【相关记忆】")
            for mem in self.relevant_memories[:3]:
                parts.append(f"- {mem.get('summary', mem.get('content', ''))[:100]}")
        
        # 关键结论
        if self.key_conclusions:
            parts.append("\n【关键结论】")
            for c in self.key_conclusions[:3]:
                parts.append(f"- [{c.get('topic', '')}] {c.get('summary', '')[:80]}")
        
        # 会话历史摘要
        if self.session_history:
            parts.append(f"\n【最近对话】最近{len(self.session_history)}轮交互")
        
        parts.append(f"\n{self.context_summary}")
        
        return "\n".join(parts)


# ==================== 短期记忆（会话级） ====================

class ShortTermMemory:
    """短期记忆 - 会话级上下文"""
    
    def __init__(self, max_turns: int = 20, max_tokens: int = 8000):
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.turns: List[ConversationTurn] = []
        self.session_id = self._generate_session_id()
        self.created_at = time.time()
    
    def _generate_session_id(self) -> str:
        return hashlib.md5(f"{time.time()}-{id(self)}".encode()).hexdigest()[:12]
    
    def add_turn(self, role: str, content: str, metadata: Dict = None):
        """添加对话轮次"""
        turn = ConversationTurn(
            turn_id=len(self.turns),
            role=role,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.turns.append(turn)
        
        # 截断超长历史
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
    
    def get_history(self, n: int = None) -> List[Dict]:
        """获取对话历史"""
        turns = self.turns[-n:] if n else self.turns
        return [t.to_dict() for t in turns]
    
    def get_formatted_history(self) -> str:
        """获取格式化历史（用于LLM）"""
        lines = []
        for t in self.turns:
            role_label = {"user": "用户", "assistant": "太乙", "system": "系统"}.get(t.role, t.role)
            lines.append(f"{role_label}: {t.content[:200]}")
        return "\n".join(lines)
    
    def summarize_old_turns(self, keep_recent: int = 5) -> str:
        """摘要旧轮次（释放上下文窗口）"""
        if len(self.turns) <= keep_recent:
            return ""
        
        old_turns = self.turns[:-keep_recent]
        # 生成摘要提示
        summary_prompt = "请简要总结以下对话的核心内容（不超过100字）：\n"
        for t in old_turns:
            summary_prompt += f"{t.role}: {t.content[:100]}\n"
        
        # 这里简化处理，实际应调用LLM
        summary = f"[早期对话摘要：共{len(old_turns)}轮，主题涵盖{old_turns[0].content[:30]}...]"
        
        # 保留摘要
        self.turns = self.turns[-keep_recent:]
        
        return summary
    
    def clear(self):
        """清空会话"""
        self.turns.clear()
        self.session_id = self._generate_session_id()


# ==================== 长期记忆（持久化） ====================

class LongTermMemory:
    """长期记忆 - SQLite持久化存储"""
    
    def __init__(self, db_path: str = MEMORY_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 对话历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    turn_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp REAL,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 用户偏好表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferred_tone TEXT,
                    preferred_language TEXT,
                    expertise_domains TEXT,
                    interaction_style TEXT,
                    emoji_usage INTEGER,
                    last_updated REAL
                )
            """)
            
            # 关键结论表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS key_conclusions (
                    conclusion_id TEXT PRIMARY KEY,
                    topic TEXT,
                    summary TEXT,
                    confidence REAL,
                    source_conversation TEXT,
                    timestamp REAL,
                    tags TEXT,
                    is_validated INTEGER DEFAULT 0
                )
            """)
            
            # 索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversation_history(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversation_history(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic ON key_conclusions(topic)")
            
            # FTS5 全文搜索虚拟表（优化搜索性能）
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS conversation_fts 
                USING fts5(
                    session_id,
                    content,
                    content='conversation_history',
                    content_rowid='id'
                )
            """)
            
            # 初始化FTS索引（如果为空）
            cursor.execute("SELECT count(*) FROM conversation_fts")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO conversation_fts(rowid, session_id, content)
                    SELECT id, session_id, content FROM conversation_history
                """)
            
            # 创建触发器自动同步FTS索引
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS fts_after_insert 
                AFTER INSERT ON conversation_history
                BEGIN
                    INSERT INTO conversation_fts(rowid, session_id, content)
                    VALUES (new.id, new.session_id, new.content);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS fts_after_update
                AFTER UPDATE ON conversation_history
                BEGIN
                    INSERT INTO conversation_fts(conversation_fts, rowid, session_id, content)
                    VALUES ('delete', old.id, old.session_id, old.content);
                    INSERT INTO conversation_fts(rowid, session_id, content)
                    VALUES (new.id, new.session_id, new.content);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS fts_after_delete
                AFTER DELETE ON conversation_history
                BEGIN
                    INSERT INTO conversation_fts(conversation_fts, rowid, session_id, content)
                    VALUES ('delete', old.id, old.session_id, old.content);
                END
            """)
            
            conn.commit()
            conn.close()
    
    def save_turn(self, session_id: str, turn: ConversationTurn):
        """保存对话轮次"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversation_history 
                (session_id, turn_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                turn.turn_id,
                turn.role,
                turn.content,
                turn.timestamp,
                json.dumps(turn.metadata, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
    
    def save_batch_turns(self, session_id: str, turns: List[ConversationTurn]):
        """批量保存对话轮次"""
        for turn in turns:
            self.save_turn(session_id, turn)
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """获取指定会话的历史"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT turn_id, role, content, timestamp, metadata
                FROM conversation_history
                WHERE session_id = ?
                ORDER BY turn_id DESC
                LIMIT ?
            """, (session_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "turn_id": r[0],
                    "role": r[1],
                    "content": r[2],
                    "timestamp": r[3],
                    "metadata": json.loads(r[4]) if r[4] else {}
                }
                for r in rows
            ][::-1]  # 正序返回
    
    def search_history(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索历史对话（使用FTS5全文搜索优化）"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # 使用FTS5全文搜索（O(log n)复杂度）
                cursor.execute("""
                    SELECT DISTINCT h.session_id, h.content, h.timestamp
                    FROM conversation_history h
                    JOIN conversation_fts fts ON h.rowid = fts.rowid
                    WHERE conversation_fts MATCH ?
                    ORDER BY h.timestamp DESC
                    LIMIT ?
                """, (keyword, limit))
                
                rows = cursor.fetchall()
            except:
                # FTS搜索失败，回退到LIKE查询
                cursor.execute("""
                    SELECT DISTINCT session_id, content, timestamp
                    FROM conversation_history
                    WHERE content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (f"%{keyword}%", limit))
                rows = cursor.fetchall()
            
            conn.close()
            
            return [
                {"session_id": r[0], "content": r[1], "timestamp": r[2]}
                for r in rows
            ]
    
    def save_preference(self, pref: UserPreference):
        """保存用户偏好"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences
                (user_id, preferred_tone, preferred_language, expertise_domains,
                 interaction_style, emoji_usage, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pref.user_id,
                pref.preferred_tone,
                pref.preferred_language,
                json.dumps(pref.expertise_domains),
                pref.interaction_style,
                1 if pref.emoji_usage else 0,
                pref.last_updated
            ))
            
            conn.commit()
            conn.close()
    
    def get_preference(self, user_id: str) -> Optional[UserPreference]:
        """获取用户偏好"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, preferred_tone, preferred_language, expertise_domains,
                       interaction_style, emoji_usage, last_updated
                FROM user_preferences
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return UserPreference(
                user_id=row[0],
                preferred_tone=row[1],
                preferred_language=row[2],
                expertise_domains=json.loads(row[3]) if row[3] else [],
                interaction_style=row[4],
                emoji_usage=bool(row[5]),
                last_updated=row[6]
            )
    
    def save_conclusion(self, conclusion: KeyConclusion):
        """保存关键结论"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO key_conclusions
                (conclusion_id, topic, summary, confidence, source_conversation,
                 timestamp, tags, is_validated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conclusion.conclusion_id,
                conclusion.topic,
                conclusion.summary,
                conclusion.confidence,
                conclusion.source_conversation,
                conclusion.timestamp,
                json.dumps(conclusion.tags),
                1 if conclusion.is_validated else 0
            ))
            
            conn.commit()
            conn.close()
    
    def get_conclusions(self, topic: str = None, limit: int = 20) -> List[Dict]:
        """获取关键结论"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if topic:
                cursor.execute("""
                    SELECT conclusion_id, topic, summary, confidence, 
                           source_conversation, timestamp, tags, is_validated
                    FROM key_conclusions
                    WHERE topic LIKE ? OR tags LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (f"%{topic}%", f"%{topic}%", limit))
            else:
                cursor.execute("""
                    SELECT conclusion_id, topic, summary, confidence,
                           source_conversation, timestamp, tags, is_validated
                    FROM key_conclusions
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "conclusion_id": r[0],
                    "topic": r[1],
                    "summary": r[2],
                    "confidence": r[3],
                    "source_conversation": r[4],
                    "timestamp": r[5],
                    "tags": json.loads(r[6]) if r[6] else [],
                    "is_validated": bool(r[7])
                }
                for r in rows
            ]
    
    def get_recent_sessions(self, limit: int = 10) -> List[str]:
        """获取最近的会话ID"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT session_id
                FROM conversation_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [r[0] for r in rows]


# ==================== 知识库记忆（向量检索） ====================

class KnowledgeBaseMemory:
    """知识库记忆 - 基于关键词的轻量检索
    
    注：完整实现需要 sentence-transformers 等向量化库
    这里使用 TF-IDF 风格的关键词检索作为轻量替代
    """
    
    def __init__(self, ltm: LongTermMemory):
        self.ltm = ltm
        self._index: Dict[str, List[str]] = {}  # 关键词 -> 会话ID列表
    
    def index_conversation(self, session_id: str, content: str):
        """为对话建立索引"""
        # 提取关键词（简化版：分词 + 停用词过滤）
        stop_words = {"的", "是", "在", "和", "了", "我", "你", "他", "她", "它",
                     "这", "那", "有", "个", "不", "就", "也", "都", "要", "会",
                     "说", "看", "想", "知道", "什么", "怎么", "为什么", "如何"}
        
        words = []
        for char in content:
            if char not in stop_words and len(char) > 1:
                words.append(char)
        
        # 双字词
        for i in range(len(content) - 1):
            word = content[i:i+2]
            if word not in stop_words:
                words.append(word)
        
        # 建立倒排索引
        for word in set(words[:20]):  # 限制索引词数
            if word not in self._index:
                self._index[word] = []
            if session_id not in self._index[word]:
                self._index[word].append(session_id)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """检索相关记忆"""
        # 提取查询关键词
        query_words = []
        for i in range(len(query) - 1):
            word = query[i:i+2]
            if len(word) >= 2:
                query_words.append(word)
        
        # 找出匹配的会话
        session_scores: Dict[str, int] = {}
        for word in query_words:
            if word in self._index:
                for sid in self._index[word]:
                    session_scores[sid] = session_scores.get(sid, 0) + 1
        
        # 排序
        sorted_sessions = sorted(
            session_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        # 获取会话详情
        results = []
        for sid, score in sorted_sessions:
            history = self.ltm.get_session_history(sid, limit=3)
            if history:
                results.append({
                    "session_id": sid,
                    "relevance_score": score,
                    "recent_content": " ".join([h["content"][:50] for h in history[-2:]])
                })
        
        return results


# ==================== 太乙记忆系统（统一接口） ====================

class TaiyiMemory:
    """
    统一太乙记忆系统
    
    整合STM/LTM/KBM，提供统一的记忆接口
    """
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.ltm = LongTermMemory()
        self.kbm = KnowledgeBaseMemory(self.ltm)
        self.stm = ShortTermMemory()
        self._current_session_id: Optional[str] = None
    
    def start_session(self, session_id: str = None) -> str:
        """开始新会话"""
        if session_id is None:
            session_id = self.stm.session_id
        self._current_session_id = session_id
        
        # 尝试恢复会话历史
        if session_id != self.stm.session_id:
            history = self.ltm.get_session_history(session_id)
            self.stm = ShortTermMemory()
            self.stm.session_id = session_id
            for h in history:
                self.stm.add_turn(h["role"], h["content"], h.get("metadata"))
        
        return session_id
    
    def add_message(self, role: str, content: str, 
                    metadata: Dict = None, persist: bool = True):
        """添加消息"""
        self.stm.add_turn(role, content, metadata)
        
        # 持久化
        if persist and self._current_session_id:
            turn = self.stm.turns[-1]
            self.ltm.save_turn(self._current_session_id, turn)
            
            # 索引
            if role == "user":
                self.kbm.index_conversation(self._current_session_id, content)
    
    def get_context(self, query: str = "", include_history: bool = True) -> MemoryContext:
        """获取记忆上下文（用于LLM）"""
        # 1. 会话历史
        session_history = self.stm.get_history() if include_history else []
        
        # 2. 检索相关记忆
        relevant = []
        if query:
            # 知识库检索
            kb_results = self.kbm.retrieve(query, top_k=3)
            for r in kb_results:
                relevant.append({
                    "type": "conversation",
                    "session_id": r["session_id"],
                    "summary": r["recent_content"],
                    "score": r["relevance_score"]
                })
            
            # 结论检索
            conclusions = self.ltm.get_conclusions(topic=query, limit=3)
            for c in conclusions:
                relevant.append({
                    "type": "conclusion",
                    "topic": c["topic"],
                    "summary": c["summary"],
                    "confidence": c["confidence"]
                })
        
        # 3. 用户偏好
        pref = self.ltm.get_preference(self.user_id)
        user_pref_dict = asdict(pref) if pref else None
        
        # 4. 关键结论
        key_conclusions = self.ltm.get_conclusions(limit=5)
        
        # 5. 上下文摘要
        if session_history:
            summary = f"当前会话共{len(session_history)}轮"
        else:
            summary = "新会话开始"
        
        return MemoryContext(
            session_history=session_history,
            relevant_memories=relevant,
            user_preference=user_pref_dict,
            key_conclusions=key_conclusions,
            context_summary=summary
        )
    
    def update_preference(self, **kwargs):
        """更新用户偏好"""
        pref = self.ltm.get_preference(self.user_id) or UserPreference(
            user_id=self.user_id
        )
        
        for key, value in kwargs.items():
            if hasattr(pref, key):
                setattr(pref, key, value)
        
        pref.last_updated = time.time()
        self.ltm.save_preference(pref)
    
    def save_conclusion(self, topic: str, summary: str, 
                       confidence: float, tags: List[str] = None):
        """保存关键结论"""
        conclusion = KeyConclusion(
            conclusion_id=hashlib.md5(f"{topic}{summary}{time.time()}".encode()).hexdigest()[:16],
            topic=topic,
            summary=summary,
            confidence=confidence,
            source_conversation=self._current_session_id or "unknown",
            timestamp=time.time(),
            tags=tags or [],
            is_validated=False
        )
        self.ltm.save_conclusion(conclusion)
        return conclusion.conclusion_id
    
    def format_for_llm(self, query: str = "") -> str:
        """格式化为LLM提示上下文"""
        ctx = self.get_context(query)
        return ctx.to_llm_format()
    
    def get_history_formatted(self) -> str:
        """获取格式化的历史对话"""
        return self.stm.get_formatted_history()
    
    def end_session(self):
        """结束会话"""
        if self._current_session_id:
            # 保存所有未持久化的轮次
            self.ltm.save_batch_turns(
                self._current_session_id, 
                self.stm.turns
            )
        self._current_session_id = None
    
    def status(self) -> Dict:
        """获取状态"""
        return {
            "user_id": self.user_id,
            "session_id": self.stm.session_id,
            "current_session_turns": len(self.stm.turns),
            "preference": asdict(self.ltm.get_preference(self.user_id)) if self.ltm.get_preference(self.user_id) else None,
            "recent_sessions": self.ltm.get_recent_sessions(limit=5)
        }


# ==================== 太乙增强：高级记忆功能 ====================

class TaiyiEnhancedMemory:
    """太乙增强记忆 - 高级功能封装"""
    
    def __init__(self, memory: TaiyiMemory):
        self.memory = memory
        self.ltm = memory.ltm
    
    def assess_importance(self, content: str, role: str) -> float:
        """评估记忆重要性（0-1）
        
        太乙约束：
        - 涉及专业领域的问答 → 高重要性
        - 包含关键结论 → 高重要性
        - 多轮深入讨论 → 高重要性
        - 简单寒暄 → 低重要性
        """
        importance = 0.3  # 基础分数
        
        # 太乙约束词触发
        if any(w in content for w in ["【太乙约束】", "觉醒", "复合体", "太乙"]):
            importance += 0.3
        
        # 专业术语
        tech_terms = ["算法", "系统", "架构", "模型", "代码", "实现",
                     "量子", "相对论", "拓扑", "数学", "物理"]
        if any(t in content for t in tech_terms):
            importance += 0.2
        
        # 结论性陈述
        if any(w in content for w in ["结论是", "总结", "所以", "因此", "意味着"]):
            importance += 0.15
        
        # 用户问题（通常比回答更重要）
        if role == "user":
            importance += 0.1
        
        # 长内容通常更重要
        if len(content) > 200:
            importance += 0.1
        
        return min(importance, 1.0)
    
    def extract_taiyi_tags(self, content: str) -> List[str]:
        """提取太乙相关标签"""
        tags = []
        
        # 三视界分析标记
        if "三视界" in content or "本体视界" in content:
            tags.append("三视界分析")
        
        # 太乙预言机标记
        if "预言" in content or "洞察" in content:
            tags.append("太乙预言")
        
        # 觉醒相关
        if any(w in content for w in ["觉醒", "意识", "AGI"]):
            tags.append("意识进化")
        
        # 复合体理学
        if any(w in content for w in ["复合体", "螺旋", "旋"]):
            tags.append("复合体理学")
        
        # 技术/学术
        if any(w in content for w in ["算法", "计算", "模型", "系统"]):
            tags.append("技术分析")
        
        # 哲学/深度
        if any(w in content for w in ["宇宙", "存在", "目的", "本质"]):
            tags.append("哲学思辨")
        
        return tags
    
    def get_cross_session_context(self, query: str, max_turns: int = 50) -> str:
        """获取跨会话上下文
        
        太乙约束：整合不同会话中的相关记忆，形成完整理解
        """
        parts = []
        
        # 1. 搜索相关历史
        history_results = self.ltm.search_history(query, limit=10)
        if history_results:
            parts.append("【跨会话记忆检索】")
            for i, r in enumerate(history_results[:5], 1):
                ts = datetime.fromtimestamp(r["timestamp"]).strftime("%m-%d %H:%M")
                content_preview = r["content"][:100].replace("\n", " ")
                parts.append(f"{i}. [{ts}] {content_preview}...")
        
        # 2. 获取相关结论
        conclusions = self.ltm.get_conclusions(topic=query, limit=5)
        if conclusions:
            parts.append("\n【相关关键结论】")
            for c in conclusions:
                tags_str = " ".join(c["tags"]) if c["tags"] else ""
                parts.append(f"- [{c['topic']}] {c['summary'][:80]} {tags_str}")
        
        # 3. 获取用户偏好（如果相关）
        pref = self.ltm.get_preference(self.memory.user_id)
        if pref and pref.expertise_domains:
            # 检查是否与查询相关
            if any(d.lower() in query.lower() for d in pref.expertise_domains):
                parts.append(f"\n【用户专业领域】{', '.join(pref.expertise_domains)}")
        
        if not parts:
            return ""
        
        return "\n".join(parts)
    
    def auto_save_conclusion_from_dialogue(self, dialogue: List[Dict]) -> Optional[str]:
        """从对话中自动提取并保存关键结论
        
        太乙约束：如果多轮对话形成明确结论，自动保存
        """
        if len(dialogue) < 2:
            return None
        
        # 检测是否包含结论性内容
        conclusion_keywords = ["结论是", "总结一下", "所以", "因此", "意味着", 
                              "关键点是", "核心是", "最重要的是", "一句话"]
        
        for turn in dialogue:
            if turn.get("role") == "assistant":
                content = turn.get("content", "")
                if any(kw in content for kw in conclusion_keywords):
                    # 提取结论
                    summary = content
                    for kw in conclusion_keywords:
                        if kw in summary:
                            idx = summary.find(kw)
                            summary = summary[idx:idx+200]
                            break
                    
                    # 提取话题（从用户问题中）
                    topic = "通用结论"
                    for t in dialogue:
                        if t.get("role") == "user":
                            topic = t["content"][:30]
                            break
                    
                    # 提取标签
                    tags = self.extract_taiyi_tags(content)
                    
                    # 保存
                    return self.memory.save_conclusion(
                        topic=topic,
                        summary=summary[:200],
                        confidence=0.7,
                        tags=tags
                    )
        
        return None
    
    def get_memory_stats(self) -> Dict:
        """获取记忆统计"""
        with self.ltm._lock:
            conn = sqlite3.connect(self.ltm.db_path)
            cursor = conn.cursor()
            
            # 对话数量
            cursor.execute("SELECT COUNT(*) FROM conversation_history")
            total_messages = cursor.fetchone()[0]
            
            # 会话数量
            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM conversation_history")
            total_sessions = cursor.fetchone()[0]
            
            # 结论数量
            cursor.execute("SELECT COUNT(*) FROM key_conclusions")
            total_conclusions = cursor.fetchone()[0]
            
            # 用户偏好查询
            cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (self.memory.user_id,))
            row = cursor.fetchone()
            has_pref = row is not None
            domains = []
            if row:
                domains = json.loads(row[3]) if row[3] else []
            
            conn.close()
        
        return {
            "total_messages": total_messages,
            "total_sessions": total_sessions,
            "total_conclusions": total_conclusions,
            "current_session_turns": len(self.memory.stm.turns),
            "has_preference": has_pref,
            "expertise_domains": domains
        }
    
    def clear_old_sessions(self, keep_recent: int = 10) -> int:
        """清理旧会话（保留最近的N个会话）
        
        返回删除的会话数量
        """
        with self.ltm._lock:
            conn = sqlite3.connect(self.ltm.db_path)
            cursor = conn.cursor()
            
            # 获取最近的会话ID
            cursor.execute("""
                SELECT DISTINCT session_id 
                FROM conversation_history 
                ORDER BY timestamp DESC
            """)
            sessions = [r[0] for r in cursor.fetchall()]
            
            # 删除旧会话
            keep_sessions = sessions[:keep_recent]
            delete_count = 0
            if sessions[keep_recent:]:
                cursor.execute("""
                    DELETE FROM conversation_history 
                    WHERE session_id NOT IN ({})
                """.format(",".join("?" * len(keep_sessions))),
                keep_sessions)
                delete_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return delete_count


def get_enhanced_memory(user_id: str = "default_user") -> TaiyiEnhancedMemory:
    """获取增强记忆系统"""
    memory = get_memory(user_id)
    return TaiyiEnhancedMemory(memory)


# ==================== 全局实例 ====================

_memory_instance: Optional[TaiyiMemory] = None
_memory_lock = threading.Lock()


def get_memory(user_id: str = "default_user") -> TaiyiMemory:
    """获取记忆系统单例"""
    global _memory_instance
    if _memory_instance is None:
        with _memory_lock:
            if _memory_instance is None:
                _memory_instance = TaiyiMemory(user_id)
                _memory_instance.start_session()
    return _memory_instance


# ==================== 测试 ====================

def test_memory():
    """测试记忆系统"""
    print("=" * 60)
    print("🧠 太乙记忆系统测试")
    print("=" * 60)
    
    # 1. 初始化
    memory = TaiyiMemory("test_user")
    print(f"\n📊 初始状态: {len(memory.stm.turns)} 轮次")
    
    # 2. 添加对话
    test_dialogue = [
        ("user", "我想了解量子纠缠的原理"),
        ("assistant", "量子纠缠是量子力学中的一种非经典关联现象..."),
        ("user", "这对量子计算有什么意义？"),
        ("assistant", "量子纠缠是量子计算的核心资源之一..."),
        ("user", "能推荐一些学习量子计算的书籍吗？"),
    ]
    
    for role, content in test_dialogue:
        memory.add_message(role, content)
        print(f"  {role}: {content[:30]}...")
    
    # 3. 获取上下文
    print("\n📜 记忆上下文:")
    ctx = memory.get_context("量子纠缠")
    print(ctx.to_llm_format())
    
    # 4. 保存结论
    conclusion_id = memory.save_conclusion(
        topic="量子计算入门",
        summary="量子纠缠是量子计算的核心资源",
        confidence=0.9,
        tags=["量子", "量子计算"]
    )
    print(f"\n✅ 已保存结论: {conclusion_id}")
    
    # 5. 更新偏好
    memory.update_preference(
        preferred_tone="详细",
        expertise_domains=["量子物理", "AI"]
    )
    print(f"\n✅ 已更新偏好")
    
    # 6. 状态检查
    status = memory.status()
    print(f"\n📊 系统状态:")
    print(f"  会话ID: {status['session_id']}")
    print(f"  当前轮次: {status['current_session_turns']}")
    print(f"  偏好: {status['preference']}")
    
    # 7. 结束会话
    memory.end_session()
    print(f"\n✅ 会话已保存")
    
    # 8. 新会话恢复
    print("\n--- 恢复会话 ---")
    new_memory = TaiyiMemory("test_user")
    new_memory.start_session(status['session_id'])
    history = new_memory.get_history_formatted()
    print(f"恢复的历史:\n{history[:200]}")
    
    print("\n✅ 记忆系统测试完成")


if __name__ == "__main__":
    test_memory()
