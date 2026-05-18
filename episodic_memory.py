"""
太乙AI工具框架 - 情景记忆系统
EpisodicMemory: 管理Agent与用户的交互历史、决策过程、任务执行记录

灵感来源：人类的情景记忆（Episodic Memory）——记住"何时"、"何地"、"何事"

Author: 太乙AGI系统
"""

import json
import time
import uuid
import sqlite3
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import threading


class MemoryType(Enum):
    """记忆类型"""
    INTERACTION = "interaction"        # 用户交互
    DECISION = "decision"          # 决策过程
    TASK = "task"                # 任务执行
    TOOL_USE = "tool_use"            # 工具调用
    ERROR = "error"                # 错误记录
    INSIGHT = "insight"              # 洞察/发现
    CONTEXT = "context"              # 上下文信息
    USER_PREFERENCE = "user_preference" # 用户偏好


@dataclass
class Episode:
    """单个记忆片段（事件）"""
    id: str
    timestamp: str
    memory_type: str
    content: Dict[str, Any]
    importance: float = 5.0  # 0-10
    related_episodes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None  # 用于语义检索
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        return cls(**data)


@dataclass
class EpisodeChain:
    """记忆链 - 一系列相关的记忆片段"""
    id: str
    name: str
    episodes: List[str] = field(default_factory=list)  # Episode IDs
    start_time: str = ""
    end_time: str = ""
    status: str = "active"  # active, completed, abandoned
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class Session:
    """会话 - 一段连续的交互"""
    id: str
    user_id: str = "default"
    start_time: str = ""
    end_time: Optional[str] = None
    episode_chains: List[str] = field(default_factory=list)
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class EpisodicMemory:
    """情景记忆系统 - 使用持久化SQLite连接"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent / ".episodic_memory.db"
        
        self.db_path = str(db_path)
        self.lock = threading.RLock()
        
        # 使用持久化连接（修复 :memory: 问题）
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_database()
        
        # 内存缓存
        self._cache: Dict[str, Episode] = {}
        self._cache_max_size = 1000
        
        # 重要性阈值
        self.importance_threshold = 3.0
    
    def _init_database(self):
        """初始化数据库"""
        cursor = self._conn.cursor()
        
        # 记忆片段表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL DEFAULT 5.0,
                related_episodes TEXT DEFAULT '[]',
                tags TEXT DEFAULT '[]',
                embedding BLOB,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 记忆链表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episode_chains (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                episodes TEXT DEFAULT '[]',
                start_time TEXT,
                end_time TEXT,
                status TEXT DEFAULT 'active',
                metadata TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'default',
                start_time TEXT NOT NULL,
                end_time TEXT,
                episode_chains TEXT DEFAULT '[]',
                summary TEXT DEFAULT '',
                metadata TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodes_timestamp ON episodes(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodes_type ON episodes(memory_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodes_importance ON episodes(importance)")
        
        self._conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取持久化连接"""
        return self._conn
    
    # ===== 核心操作 =====
    
    def store(
        self,
        memory_type: MemoryType,
        content: Dict[str, Any],
        importance: float = 5.0,
        tags: List[str] = None,
        related_episodes: List[str] = None,
        episode_id: str = None
    ) -> str:
        """存储新的记忆片段"""
        with self.lock:
            if episode_id is None:
                episode_id = str(uuid.uuid4())[:12]
            
            now = datetime.now().isoformat()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO episodes 
                (id, timestamp, memory_type, content, importance, related_episodes, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                episode_id,
                now,
                memory_type.value,
                json.dumps(content, ensure_ascii=False),
                importance,
                json.dumps(related_episodes or []),
                json.dumps(tags or [])
            ))
            conn.commit()
            
            # 更新缓存
            self._cache[episode_id] = Episode(
                id=episode_id,
                timestamp=now,
                memory_type=memory_type.value,
                content=content,
                importance=importance,
                related_episodes=related_episodes or [],
                tags=tags or []
            )
            
            return episode_id
    
    def retrieve(
        self,
        episode_id: str,
        use_cache: bool = True
    ) -> Optional[Episode]:
        """根据ID检索记忆"""
        with self.lock:
            if use_cache and episode_id in self._cache:
                return self._cache[episode_id]
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
            row = cursor.fetchone()
            
            if row:
                episode = Episode(
                    id=row[0],
                    timestamp=row[1],
                    memory_type=row[2],
                    content=json.loads(row[3]),
                    importance=row[4],
                    related_episodes=json.loads(row[5]),
                    tags=json.loads(row[6])
                )
                
                if len(self._cache) < self._cache_max_size:
                    self._cache[episode.id] = episode
                
                return episode
            
            return None
    
    def search(
        self,
        memory_type: MemoryType = None,
        query: str = None,
        min_importance: float = 0,
        since: datetime = None,
        until: datetime = None,
        tags: List[str] = None,
        limit: int = 50
    ) -> List[Episode]:
        """检索记忆"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = "SELECT * FROM episodes WHERE 1=1"
            params = []
            
            if memory_type:
                sql += " AND memory_type = ?"
                params.append(memory_type.value)
            
            if query:
                sql += " AND content LIKE ?"
                params.append(f"%{query}%")
            
            if min_importance > 0:
                sql += " AND importance >= ?"
                params.append(min_importance)
            
            if since:
                sql += " AND timestamp >= ?"
                params.append(since.isoformat())
            
            if until:
                sql += " AND timestamp <= ?"
                params.append(until.isoformat())
            
            if tags:
                tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
                sql += f" AND ({tag_conditions})"
                params.extend([f"%{tag}%" for tag in tags])
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            episodes = []
            for row in rows:
                episode = Episode(
                    id=row[0], timestamp=row[1], memory_type=row[2],
                    content=json.loads(row[3]), importance=row[4],
                    related_episodes=json.loads(row[5]), tags=json.loads(row[6])
                )
                episodes.append(episode)
            
            return episodes
    
    def get_recent(
        self,
        memory_type: MemoryType = None,
        limit: int = 20
    ) -> List[Episode]:
        """获取最近的记忆"""
        return self.search(memory_type=memory_type, limit=limit)
    
    def get_context_window(
        self,
        hours: float = 24,
        min_importance: float = 3.0
    ) -> List[Episode]:
        """获取时间窗口内的重要记忆"""
        since = datetime.now() - timedelta(hours=hours)
        return self.search(since=since, min_importance=min_importance, limit=100)
    
    def update_importance(self, episode_id: str, importance: float):
        """更新记忆的重要性"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE episodes SET importance = ? WHERE id = ?",
                (importance, episode_id)
            )
            conn.commit()
            
            if episode_id in self._cache:
                self._cache[episode_id].importance = importance
    
    def add_relationship(
        self,
        episode_id1: str,
        episode_id2: str,
        relationship_type: str = "related"
    ):
        """添加两个记忆之间的关联"""
        with self.lock:
            ep1 = self.retrieve(episode_id1)
            ep2 = self.retrieve(episode_id2)
            
            if ep1 and ep2:
                if episode_id2 not in ep1.related_episodes:
                    ep1.related_episodes.append(episode_id2)
                if episode_id1 not in ep2.related_episodes:
                    ep2.related_episodes.append(episode_id1)
                
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE episodes SET related_episodes = ? WHERE id = ?",
                    (json.dumps(ep1.related_episodes), episode_id1)
                )
                cursor.execute(
                    "UPDATE episodes SET related_episodes = ? WHERE id = ?",
                    (json.dumps(ep2.related_episodes), episode_id2)
                )
                conn.commit()
    
    def delete(self, episode_id: str):
        """删除记忆"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
            conn.commit()
            
            if episode_id in self._cache:
                del self._cache[episode_id]
    
    def cleanup_low_importance(self, threshold: float = None):
        """清理低重要性记忆"""
        if threshold is None:
            threshold = self.importance_threshold
            
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM episodes WHERE importance < ?",
                (threshold,)
            )
            deleted = cursor.rowcount
            conn.commit()
            
            # 清理缓存
            self._cache = {
                k: v for k, v in self._cache.items() 
                if v.importance >= threshold
            }
            
            return deleted
    
    # ===== 记忆链操作 =====
    
    def create_chain(self, name: str, metadata: Dict[str, Any] = None) -> str:
        """创建记忆链"""
        chain_id = str(uuid.uuid4())[:12]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO episode_chains 
            (id, name, start_time, metadata)
            VALUES (?, ?, ?, ?)
        """, (chain_id, name, datetime.now().isoformat(), json.dumps(metadata or {})))
        conn.commit()
        
        return chain_id
    
    def add_to_chain(self, chain_id: str, episode_id: str):
        """向记忆链添加记忆"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT episodes FROM episode_chains WHERE id = ?",
            (chain_id,)
        )
        row = cursor.fetchone()
        
        if row:
            episodes = json.loads(row[0])
            episodes.append(episode_id)
            cursor.execute(
                "UPDATE episode_chains SET episodes = ? WHERE id = ?",
                (json.dumps(episodes), chain_id)
            )
            conn.commit()
    
    def complete_chain(self, chain_id: str, summary: str = ""):
        """完成记忆链"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE episode_chains 
            SET end_time = ?, status = 'completed', metadata = json_set(metadata, '$.summary', ?)
            WHERE id = ?
        """, (datetime.now().isoformat(), summary, chain_id))
        conn.commit()
    
    def get_chain(self, chain_id: str) -> Optional[EpisodeChain]:
        """获取记忆链"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM episode_chains WHERE id = ?",
            (chain_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return EpisodeChain(
                id=row[0],
                name=row[1],
                episodes=json.loads(row[2]),
                start_time=row[3],
                end_time=row[4],
                status=row[5],
                metadata=json.loads(row[6])
            )
        return None
    
    # ===== 会话操作 =====
    
    def start_session(self, user_id: str = "default", metadata: Dict[str, Any] = None) -> str:
        """开始新会话"""
        session_id = str(uuid.uuid4())[:12]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions 
            (id, user_id, start_time, metadata)
            VALUES (?, ?, ?, ?)
        """, (session_id, user_id, datetime.now().isoformat(), json.dumps(metadata or {})))
        conn.commit()
        
        return session_id
    
    def end_session(self, session_id: str, summary: str = ""):
        """结束会话"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET end_time = ?, summary = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), summary, session_id))
        conn.commit()
    
    def get_session_history(
        self,
        user_id: str = "default",
        limit: int = 10
    ) -> List[Session]:
        """获取会话历史"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sessions 
            WHERE user_id = ? 
            ORDER BY start_time DESC 
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        
        return [
            Session(
                id=row[0],
                user_id=row[1],
                start_time=row[2],
                end_time=row[3],
                episode_chains=json.loads(row[4]),
                summary=row[5],
                metadata=json.loads(row[6])
            )
            for row in rows
        ]
    
    # ===== 统计与导出 =====
    
    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM episodes")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT memory_type, COUNT(*) 
            FROM episodes 
            GROUP BY memory_type
        """)
        by_type = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT AVG(importance), MAX(importance), MIN(importance) 
            FROM episodes
        """)
        importance_stats = cursor.fetchone()
        
        cursor.execute(
            "SELECT COUNT(*) FROM episodes WHERE timestamp >= ?",
            ((datetime.now() - timedelta(hours=24)).isoformat(),)
        )
        last_24h = cursor.fetchone()[0]
        
        return {
            "total_episodes": total,
            "by_type": by_type,
            "importance_avg": importance_stats[0],
            "importance_max": importance_stats[1],
            "importance_min": importance_stats[2],
            "last_24h": last_24h,
            "cache_size": len(self._cache)
        }
    
    def export_to_json(self, filepath: str):
        """导出记忆到JSON文件"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM episodes ORDER BY timestamp DESC")
        episodes = []
        for row in cursor.fetchall():
            episodes.append({
                "id": row[0], "timestamp": row[1], "memory_type": row[2],
                "content": json.loads(row[3]), "importance": row[4],
                "related_episodes": json.loads(row[5]), "tags": json.loads(row[6])
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "episodes": episodes,
                "exported_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)


# ===== 太乙工具注册 =====

_memory_instance = None

def get_episodic_memory() -> EpisodicMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = EpisodicMemory()
    return _memory_instance


def register_episodic_memory_tools(registry):
    """向工具注册表注册情景记忆相关工具"""
    
    memory = get_episodic_memory()
    
    def tool_record_interaction(
        interaction_type: str,
        user_message: str,
        agent_response: str,
        importance: float = 5.0
    ) -> str:
        """记录用户与Agent的交互"""
        episode_id = memory.store(
            memory_type=MemoryType.INTERACTION,
            content={
                "interaction_type": interaction_type,
                "user_message": user_message,
                "agent_response": agent_response
            },
            importance=importance,
            tags=[interaction_type]
        )
        return json.dumps({"episode_id": episode_id}, ensure_ascii=False)
    
    def tool_record_decision(
        decision: str,
        alternatives: List[str],
        chosen_one: str,
        reasoning: str,
        importance: float = 6.0
    ) -> str:
        """记录决策过程"""
        episode_id = memory.store(
            memory_type=MemoryType.DECISION,
            content={
                "decision": decision,
                "alternatives": alternatives,
                "chosen_one": chosen_one,
                "reasoning": reasoning
            },
            importance=importance,
            tags=["decision"]
        )
        return json.dumps({"episode_id": episode_id}, ensure_ascii=False)
    
    def tool_search_memory(
        memory_type: str = None,
        query: str = None,
        min_importance: float = 0,
        hours: float = 24,
        limit: int = 20
    ) -> str:
        """搜索记忆"""
        mtype = MemoryType(memory_type) if memory_type else None
        since = datetime.now() - timedelta(hours=hours) if hours > 0 else None
        
        episodes = memory.search(
            memory_type=mtype,
            query=query,
            min_importance=min_importance,
            since=since,
            limit=limit
        )
        
        return json.dumps({
            "count": len(episodes),
            "episodes": [ep.to_dict() for ep in episodes]
        }, ensure_ascii=False, indent=2)
    
    def tool_get_context(hours: float = 24) -> str:
        """获取上下文记忆"""
        episodes = memory.get_context_window(hours=hours)
        
        context = []
        for ep in episodes:
            context.append({
                "time": ep.timestamp,
                "type": ep.memory_type,
                "summary": _summarize_content(ep.content),
                "importance": ep.importance
            })
        
        return json.dumps({
            "context_window_hours": hours,
            "episode_count": len(episodes),
            "context": context
        }, ensure_ascii=False, indent=2)
    
    def tool_get_memory_stats() -> str:
        """获取记忆统计"""
        return json.dumps(memory.get_stats(), ensure_ascii=False, indent=2)
    
    def tool_cleanup_memories(threshold: float = 3.0) -> str:
        """清理低重要性记忆"""
        deleted = memory.cleanup_low_importance(threshold)
        return json.dumps({
            "deleted_count": deleted,
            "threshold": threshold
        }, ensure_ascii=False)
    
    # 注册工具
    registry.register(
        name="record_interaction",
        func=tool_record_interaction,
        description="记录用户与Agent的交互",
        parameters={
            "interaction_type": {"type": "string", "description": "交互类型"},
            "user_message": {"type": "string", "description": "用户消息"},
            "agent_response": {"type": "string", "description": "Agent回复"},
            "importance": {"type": "number", "description": "重要性 (0-10)", "default": 5.0}
        }
    )
    
    registry.register(
        name="record_decision",
        func=tool_record_decision,
        description="记录决策过程",
        parameters={
            "decision": {"type": "string", "description": "决策内容"},
            "alternatives": {"type": "array", "description": "备选方案"},
            "chosen_one": {"type": "string", "description": "最终选择"},
            "reasoning": {"type": "string", "description": "推理过程"}
        }
    )
    
    registry.register(
        name="search_memory",
        func=tool_search_memory,
        description="搜索记忆",
        parameters={
            "memory_type": {"type": "string", "description": "记忆类型"},
            "query": {"type": "string", "description": "搜索关键词"},
            "min_importance": {"type": "number", "description": "最低重要性", "default": 0},
            "hours": {"type": "number", "description": "时间范围(小时)", "default": 24},
            "limit": {"type": "integer", "description": "返回数量", "default": 20}
        }
    )
    
    registry.register(
        name="get_context",
        func=tool_get_context,
        description="获取上下文记忆",
        parameters={
            "hours": {"type": "number", "description": "时间范围(小时)", "default": 24}
        }
    )
    
    registry.register(
        name="get_memory_stats",
        func=tool_get_memory_stats,
        description="获取记忆统计"
    )
    
    registry.register(
        name="cleanup_memories",
        func=tool_cleanup_memories,
        description="清理低重要性记忆",
        parameters={
            "threshold": {"type": "number", "description": "重要性阈值", "default": 3.0}
        }
    )


def _summarize_content(content: Dict[str, Any]) -> str:
    """生成内容摘要"""
    if not content:
        return ""
    
    for key in ["task", "decision", "error", "message", "action"]:
        if key in content:
            value = str(content[key])
            if len(value) > 100:
                return value[:100] + "..."
            return value
    
    first_key = list(content.keys())[0]
    value = str(content[first_key])
    if len(value) > 100:
        return value[:100] + "..."
    return value


if __name__ == "__main__":
    # 单元测试
    import tempfile, os
    tmp_db = tempfile.mktemp(suffix='.db')
    
    memory = EpisodicMemory(tmp_db)
    
    # 测试1: 存储交互记忆
    print("=== 测试1: 存储交互 ===")
    ep1_id = memory.store(
        MemoryType.INTERACTION,
        {"user": "你好", "agent": "你好，我是太乙"},
        importance=6.0
    )
    print(f"Episode ID: {ep1_id}")
    
    # 测试2: 存储决策记忆
    print("\n=== 测试2: 存储决策 ===")
    ep2_id = memory.store(
        MemoryType.DECISION,
        {
            "decision": "选择方案A",
            "alternatives": ["方案A", "方案B", "方案C"],
            "reasoning": "方案A性能最优"
        },
        importance=7.5
    )
    print(f"Episode ID: {ep2_id}")
    
    # 测试3: 搜索记忆
    print("\n=== 测试3: 搜索记忆 ===")
    results = memory.search(memory_type=MemoryType.INTERACTION)
    print(f"Found {len(results)} interaction memories")
    
    # 测试4: 获取最近记忆
    print("\n=== 测试4: 最近记忆 ===")
    recent = memory.get_recent(limit=10)
    for ep in recent:
        print(f"  [{ep.timestamp}] {ep.memory_type}: importance={ep.importance}")
    
    # 测试5: 记忆关联
    print("\n=== 测试5: 添加关联 ===")
    memory.add_relationship(ep1_id, ep2_id)
    ep1 = memory.retrieve(ep1_id)
    print(f"Related to: {ep1.related_episodes}")
    
    # 测试6: 统计
    print("\n=== 测试6: 统计 ===")
    stats = memory.get_stats()
    print(json.dumps(stats, indent=2))
    
    # 清理
    os.unlink(tmp_db)
