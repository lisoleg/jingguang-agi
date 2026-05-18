"""
太乙AI工具框架 - 知识图谱系统
KnowledgeGraph: 实体、关系、属性管理，支持图查询、推理与可视化

Author: 太乙AGI系统
"""

import json
import uuid
import sqlite3
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
import threading
import hashlib


class EntityType(Enum):
    """实体类型"""
    CONCEPT = "concept"           # 概念
    PERSON = "person"             # 人物
    ORGANIZATION = "organization" # 组织
    LOCATION = "location"         # 地点
    EVENT = "event"              # 事件
    DOCUMENT = "document"         # 文档
    TOOL = "tool"                # 工具
    TASK = "task"                # 任务
    CODE = "code"                # 代码
    PROPERTY = "property"        # 属性值
    UNKNOWN = "unknown"


class RelationType(Enum):
    """关系类型"""
    IS_A = "is_a"                # 是...（继承关系）
    PART_OF = "part_of"          # 是...的一部分
    HAS_PROPERTY = "has_property" # 有属性
    RELATED_TO = "related_to"    # 与...相关
    CAUSED_BY = "caused_by"      # 由...引起
    LEADS_TO = "leads_to"        # 导致
    USES = "uses"                # 使用
    DEPENDS_ON = "depends_on"    # 依赖于
    SIMILAR_TO = "similar_to"    # 类似于
    CONTRADICTS = "contradicts"  # 与...矛盾
    BELONGS_TO = "belongs_to"    # 属于
    DEFINED_IN = "defined_in"     # 定义于
    IMPLEMENTS = "implements"     # 实现


@dataclass
class Entity:
    """实体"""
    id: str
    name: str
    entity_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    confidence: float = 1.0  # 置信度 0-1
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        return cls(**data)
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class Relation:
    """关系"""
    id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    weight: float = 1.0  # 关系权重
    created_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relation":
        return cls(**data)


@dataclass 
class GraphQuery:
    """图查询结果"""
    entities: List[Entity]
    relations: List[Relation]
    paths: List[List[Tuple[str, str]]] = field(default_factory=list)  # 路径


class KnowledgeGraph:
    """
    知识图谱系统 - 使用持久化SQLite连接
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent / ".knowledge_graph.db"
        
        self.db_path = str(db_path)
        self.lock = threading.RLock()
        
        # 使用持久化连接（修复 :memory: 问题）
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_database()
        
        # 缓存
        self._entity_cache: Dict[str, Entity] = {}
        self._cache_max_size = 500
    
    def _init_database(self):
        """初始化数据库"""
        cursor = self._conn.cursor()
        
        # 实体表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                description TEXT DEFAULT '',
                aliases TEXT DEFAULT '[]',
                confidence REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                confidence REAL DEFAULT 1.0,
                weight REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES entities(id),
                FOREIGN KEY (target_id) REFERENCES entities(id)
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type)")
        
        self._conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取持久化连接"""
        return self._conn
    
    # ===== 实体操作 =====
    
    def create_entity(
        self,
        name: str,
        entity_type: str,
        properties: Dict[str, Any] = None,
        description: str = "",
        aliases: List[str] = None,
        confidence: float = 1.0,
        entity_id: str = None
    ) -> Entity:
        """创建实体"""
        with self.lock:
            if entity_id is None:
                entity_id = self._generate_entity_id(name)
            
            now = datetime.now().isoformat()
            
            entity = Entity(
                id=entity_id,
                name=name,
                entity_type=entity_type,
                properties=properties or {},
                description=description,
                aliases=aliases or [],
                confidence=confidence,
                created_at=now,
                updated_at=now
            )
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO entities 
                (id, name, entity_type, properties, description, aliases, confidence, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.id, entity.name, entity.entity_type,
                json.dumps(entity.properties), entity.description,
                json.dumps(entity.aliases), entity.confidence,
                entity.created_at, entity.updated_at
            ))
            conn.commit()
            
            self._entity_cache[entity.id] = entity
            return entity
    
    def get_entity(self, entity_id: str, use_cache: bool = True) -> Optional[Entity]:
        """获取实体"""
        with self.lock:
            if use_cache and entity_id in self._entity_cache:
                return self._entity_cache[entity_id]
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
            row = cursor.fetchone()
            
            if row:
                entity = Entity(
                    id=row[0], name=row[1], entity_type=row[2],
                    properties=json.loads(row[3]), description=row[4],
                    aliases=json.loads(row[5]), confidence=row[6],
                    created_at=row[7], updated_at=row[8]
                )
                
                if len(self._entity_cache) < self._cache_max_size:
                    self._entity_cache[entity.id] = entity
                
                return entity
            
            return None
    
    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """通过名称查找实体"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM entities WHERE name = ? OR aliases LIKE ?",
            (name, f"%\"{name}\"%")
        )
        row = cursor.fetchone()
        
        if row:
            return self.get_entity(row[0])
        return None
    
    def update_entity(
        self,
        entity_id: str,
        name: str = None,
        properties: Dict[str, Any] = None,
        description: str = None,
        aliases: List[str] = None,
        confidence: float = None
    ) -> Optional[Entity]:
        """更新实体"""
        with self.lock:
            entity = self.get_entity(entity_id, use_cache=False)
            if not entity:
                return None
            
            if name is not None:
                entity.name = name
            if properties is not None:
                entity.properties.update(properties)
            if description is not None:
                entity.description = description
            if aliases is not None:
                entity.aliases = aliases
            if confidence is not None:
                entity.confidence = confidence
            
            entity.updated_at = datetime.now().isoformat()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE entities 
                SET name = ?, entity_type = ?, properties = ?, description = ?, 
                    aliases = ?, confidence = ?, updated_at = ?
                WHERE id = ?
            """, (
                entity.name, entity.entity_type,
                json.dumps(entity.properties), entity.description,
                json.dumps(entity.aliases), entity.confidence,
                entity.updated_at, entity.id
            ))
            conn.commit()
            
            # 更新缓存
            if entity_id in self._entity_cache:
                self._entity_cache[entity_id] = entity
            
            return entity
    
    def delete_entity(self, entity_id: str):
        """删除实体及其所有关系"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 删除相关关系
            cursor.execute(
                "DELETE FROM relations WHERE source_id = ? OR target_id = ?",
                (entity_id, entity_id)
            )
            
            # 删除实体
            cursor.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            
            conn.commit()
            
            # 清理缓存
            if entity_id in self._entity_cache:
                del self._entity_cache[entity_id]
    
    def search_entities(
        self,
        name_pattern: str = None,
        entity_type: str = None,
        property_filter: Dict[str, Any] = None,
        limit: int = 50
    ) -> List[Entity]:
        """搜索实体"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = "SELECT * FROM entities WHERE 1=1"
            params = []
            
            if name_pattern:
                sql += " AND (name LIKE ? OR aliases LIKE ?)"
                params.extend([f"%{name_pattern}%", f"%{name_pattern}%"])
            
            if entity_type:
                sql += " AND entity_type = ?"
                params.append(entity_type)
            
            sql += " LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            entities = []
            for row in rows:
                entity = Entity(
                    id=row[0], name=row[1], entity_type=row[2],
                    properties=json.loads(row[3]), description=row[4],
                    aliases=json.loads(row[5]), confidence=row[6],
                    created_at=row[7], updated_at=row[8]
                )
                
                # 属性过滤
                if property_filter:
                    match = all(
                        entity.properties.get(k) == v 
                        for k, v in property_filter.items()
                    )
                    if match:
                        entities.append(entity)
                else:
                    entities.append(entity)
            
            return entities
    
    # ===== 关系操作 =====
    
    def create_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Dict[str, Any] = None,
        confidence: float = 1.0,
        weight: float = 1.0,
        relation_id: str = None
    ) -> Optional[Relation]:
        """创建关系"""
        with self.lock:
            # 验证实体存在
            if not self.get_entity(source_id, use_cache=False):
                return None
            if not self.get_entity(target_id, use_cache=False):
                return None
            
            if relation_id is None:
                relation_id = str(uuid.uuid4())[:12]
            
            now = datetime.now().isoformat()
            
            relation = Relation(
                id=relation_id,
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                properties=properties or {},
                confidence=confidence,
                weight=weight,
                created_at=now
            )
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO relations 
                (id, source_id, target_id, relation_type, properties, confidence, weight, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                relation.id, relation.source_id, relation.target_id,
                relation.relation_type, json.dumps(relation.properties),
                relation.confidence, relation.weight, relation.created_at
            ))
            conn.commit()
            
            return relation
    
    def get_relations(
        self,
        entity_id: str,
        direction: str = "both"  # out, in, both
    ) -> List[Relation]:
        """获取实体的关系"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if direction == "out":
                cursor.execute(
                    "SELECT * FROM relations WHERE source_id = ?",
                    (entity_id,)
                )
            elif direction == "in":
                cursor.execute(
                    "SELECT * FROM relations WHERE target_id = ?",
                    (entity_id,)
                )
            else:  # both
                cursor.execute(
                    "SELECT * FROM relations WHERE source_id = ? OR target_id = ?",
                    (entity_id, entity_id)
                )
            
            rows = cursor.fetchall()
            
            return [
                Relation(
                    id=row[0], source_id=row[1], target_id=row[2],
                    relation_type=row[3], properties=json.loads(row[4]),
                    confidence=row[5], weight=row[6], created_at=row[7]
                )
                for row in rows
            ]
    
    def delete_relation(self, relation_id: str):
        """删除关系"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relations WHERE id = ?", (relation_id,))
            conn.commit()
    
    # ===== 图查询 =====
    
    def get_neighbors(
        self,
        entity_id: str,
        relation_type: str = None,
        depth: int = 1,
        max_hops: int = 2
    ) -> Dict[str, List[Entity]]:
        """获取邻居实体"""
        with self.lock:
            visited: Set[str] = {entity_id}
            current_level: Set[str] = {entity_id}
            
            result: Dict[str, List[Entity]] = {}
            
            for hop in range(1, max_hops + 1):
                next_level: Set[str] = set()
                
                for eid in current_level:
                    relations = self.get_relations(eid, direction="out")
                    neighbors = []
                    
                    for rel in relations:
                        neighbor = rel.target_id
                        if neighbor not in visited:
                            neighbor_entity = self.get_entity(neighbor)
                            if neighbor_entity:
                                neighbors.append(neighbor_entity)
                                next_level.add(neighbor)
                                visited.add(neighbor)
                    
                if neighbors:
                    result[f"hop_{hop}"] = neighbors
                
                current_level = next_level
            
            return result
    
    def find_shortest_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> List[Tuple[str, str]]:
        """查找两实体间的最短路径"""
        with self.lock:
            from collections import deque
            
            queue = deque([(source_id, [(source_id, "", "")])])
            visited = {source_id}
            
            while queue:
                current, path = queue.popleft()
                
                if len(path) > max_depth:
                    continue
                
                if current == target_id:
                    return path[1:]  # 去掉起始节点
                
                relations = self.get_relations(current, direction="out")
                for rel in relations:
                    neighbor = rel.target_id
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = path + [(current, rel.relation_type, neighbor)]
                        queue.append((neighbor, new_path))
            
            return []
    
    # ===== 统计与导出 =====
    
    def get_stats(self) -> Dict[str, Any]:
        """获取图谱统计"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM entities")
        entity_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relations")
        relation_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT entity_type, COUNT(*) 
            FROM entities 
            GROUP BY entity_type
        """)
        by_type = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT relation_type, COUNT(*) 
            FROM relations 
            GROUP BY relation_type
        """)
        by_relation = dict(cursor.fetchall())
        
        return {
            "entity_count": entity_count,
            "relation_count": relation_count,
            "entities_by_type": by_type,
            "relations_by_type": by_relation,
            "cache_size": len(self._entity_cache)
        }
    
    def export_to_json(self, filepath: str):
        """导出图谱到JSON"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM entities")
        entities = []
        for row in cursor.fetchall():
            entities.append({
                "id": row[0], "name": row[1], "entity_type": row[2],
                "properties": json.loads(row[3]), "description": row[4],
                "aliases": json.loads(row[5]), "confidence": row[6]
            })
        
        cursor.execute("SELECT * FROM relations")
        relations = []
        for row in cursor.fetchall():
            relations.append({
                "id": row[0], "source_id": row[1], "target_id": row[2],
                "relation_type": row[3], "properties": json.loads(row[4]),
                "confidence": row[5], "weight": row[6]
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "entities": entities,
                "relations": relations,
                "exported_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def _generate_entity_id(self, name: str) -> str:
        """生成实体ID"""
        hash_input = f"{name}:{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


# ===== 太乙工具注册 =====

_kg_instance = None

def get_knowledge_graph() -> KnowledgeGraph:
    global _kg_instance
    if _kg_instance is None:
        _kg_instance = KnowledgeGraph()
    return _kg_instance


def register_knowledge_graph_tools(registry):
    """向工具注册表注册知识图谱相关工具"""
    
    kg = get_knowledge_graph()
    
    def tool_create_entity(
        name: str,
        entity_type: str,
        properties: str = "{}",
        description: str = "",
        aliases: str = "[]"
    ) -> str:
        entity = kg.create_entity(
            name=name,
            entity_type=entity_type,
            properties=json.loads(properties),
            description=description,
            aliases=json.loads(aliases)
        )
        return json.dumps({"entity_id": entity.id, "name": entity.name}, ensure_ascii=False)
    
    def tool_create_relation(
        source_name: str,
        target_name: str,
        relation_type: str,
        properties: str = "{}"
    ) -> str:
        source = kg.get_entity_by_name(source_name)
        if not source:
            source = kg.create_entity(name=source_name, entity_type=EntityType.CONCEPT.value)
        
        target = kg.get_entity_by_name(target_name)
        if not target:
            target = kg.create_entity(name=target_name, entity_type=EntityType.CONCEPT.value)
        
        relation = kg.create_relation(
            source_id=source.id,
            target_id=target.id,
            relation_type=relation_type,
            properties=json.loads(properties)
        )
        
        if relation:
            return json.dumps({"relation_id": relation.id}, ensure_ascii=False)
        else:
            return json.dumps({"error": "Failed to create relation"}, ensure_ascii=False)
    
    def tool_search_entities(
        name_pattern: str = None,
        entity_type: str = None,
        limit: int = 20
    ) -> str:
        entities = kg.search_entities(
            name_pattern=name_pattern,
            entity_type=entity_type,
            limit=limit
        )
        
        return json.dumps({
            "count": len(entities),
            "entities": [e.to_dict() for e in entities]
        }, ensure_ascii=False, indent=2)
    
    def tool_get_neighbors(entity_name: str, max_hops: int = 2) -> str:
        entity = kg.get_entity_by_name(entity_name)
        if not entity:
            return json.dumps({"error": f"Entity '{entity_name}' not found"}, ensure_ascii=False)
        
        neighbors = kg.get_neighbors(entity.id, max_hops=max_hops)
        
        result = {}
        for hop, entities in neighbors.items():
            result[hop] = [
                {"id": e.id, "name": e.name, "type": e.entity_type}
                for e in entities
            ]
        
        return json.dumps({
            "center": entity.name,
            "neighbors": result
        }, ensure_ascii=False, indent=2)
    
    def tool_find_path(source_name: str, target_name: str) -> str:
        source = kg.get_entity_by_name(source_name)
        target = kg.get_entity_by_name(target_name)
        
        if not source or not target:
            return json.dumps({"error": "Entity not found"}, ensure_ascii=False)
        
        path = kg.find_shortest_path(source.id, target.id)
        
        path_info = []
        for item in path:
            if len(item) == 3:
                src, rel, tgt = item
                src_entity = kg.get_entity(src)
                tgt_entity = kg.get_entity(tgt)
                path_info.append({
                    "from": src_entity.name if src_entity else src,
                    "relation": rel,
                    "to": tgt_entity.name if tgt_entity else tgt
                })
        
        return json.dumps({
            "source": source_name,
            "target": target_name,
            "path": path_info,
            "length": len(path)
        }, ensure_ascii=False, indent=2)
    
    def tool_get_stats() -> str:
        return json.dumps(kg.get_stats(), ensure_ascii=False, indent=2)
    
    # 注册工具
    registry.register(
        name="create_entity",
        func=tool_create_entity,
        description="创建知识图谱实体",
        parameters={
            "name": {"type": "string", "description": "实体名称"},
            "entity_type": {"type": "string", "description": "实体类型"},
            "properties": {"type": "string", "description": "属性JSON"},
            "description": {"type": "string", "description": "描述"},
            "aliases": {"type": "string", "description": "别名列表JSON"}
        }
    )
    
    registry.register(
        name="create_relation",
        func=tool_create_relation,
        description="创建实体间的关系",
        parameters={
            "source_name": {"type": "string", "description": "源实体名称"},
            "target_name": {"type": "string", "description": "目标实体名称"},
            "relation_type": {"type": "string", "description": "关系类型"},
            "properties": {"type": "string", "description": "属性JSON"}
        }
    )
    
    registry.register(
        name="search_entities",
        func=tool_search_entities,
        description="搜索知识图谱实体",
        parameters={
            "name_pattern": {"type": "string", "description": "名称模糊匹配"},
            "entity_type": {"type": "string", "description": "实体类型"},
            "limit": {"type": "integer", "description": "返回数量", "default": 20}
        }
    )
    
    registry.register(
        name="get_neighbors",
        func=tool_get_neighbors,
        description="获取实体的邻居",
        parameters={
            "entity_name": {"type": "string", "description": "实体名称"},
            "max_hops": {"type": "integer", "description": "最大跳数", "default": 2}
        }
    )
    
    registry.register(
        name="find_path",
        func=tool_find_path,
        description="查找两实体间的最短路径",
        parameters={
            "source_name": {"type": "string", "description": "源实体名称"},
            "target_name": {"type": "string", "description": "目标实体名称"}
        }
    )
    
    registry.register(
        name="get_graph_stats",
        func=tool_get_stats,
        description="获取知识图谱统计信息"
    )


if __name__ == "__main__":
    # 单元测试
    import tempfile, os
    
    tmp_db = tempfile.mkstemp(suffix='.db')[1]
    kg = KnowledgeGraph(tmp_db)
    
    # 测试1: 创建实体
    print("=== 测试1: 创建实体 ===")
    e1 = kg.create_entity("Python", "concept", {"version": "3.10"}, "编程语言")
    e2 = kg.create_entity("Machine Learning", "concept", {}, "机器学习")
    e3 = kg.create_entity("Deep Learning", "concept", {}, "深度学习")
    e4 = kg.create_entity("TensorFlow", "tool", {"developer": "Google"}, "深度学习框架")
    print(f"Created: {e1.id}, {e2.id}, {e3.id}, {e4.id}")
    
    # 测试2: 创建关系
    print("\n=== 测试2: 创建关系 ===")
    r1 = kg.create_relation(e1.id, e2.id, "is_used_in")
    r2 = kg.create_relation(e2.id, e3.id, "is_a")
    r3 = kg.create_relation(e3.id, e4.id, "uses")
    print(f"Created relations: {r1.id}, {r2.id}, {r3.id}")
    
    # 测试3: 搜索实体
    print("\n=== 测试3: 搜索实体 ===")
    results = kg.search_entities(name_pattern="Learn")
    print(f"Found {len(results)} entities")
    for e in results:
        print(f"  - {e.name} ({e.entity_type})")
    
    # 测试4: 获取邻居
    print("\n=== 测试4: 获取邻居 ===")
    neighbors = kg.get_neighbors(e2.id, max_hops=2)
    for hop, entities in neighbors.items():
        print(f"  {hop}: {[e.name for e in entities]}")
    
    # 测试5: 查找路径
    print("\n=== 测试5: 查找路径 ===")
    path = kg.find_shortest_path(e1.id, e4.id)
    print(f"Path length: {len(path)}")
    
    # 测试6: 统计
    print("\n=== 测试6: 统计 ===")
    stats = kg.get_stats()
    print(json.dumps(stats, indent=2))
    
    # 清理
    os.unlink(tmp_db)
