# -*- coding: utf-8 -*-
"""
太乙AGI v7.2 - M85-M87: OpenHuman扩展模块整合
M85: DigitalLifeFusion - 数字生活融合引擎
M86: ObsidianCompatLayer - Obsidian兼容导出层
M87: ZeroTrainingContext - 零训练期认知系统

作者: 太乙AGI团队
日期: 2026-05-19
参考: OpenHuman (https://github.com/tinyhumansai/openhuman)
"""

import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ==================== M85: DigitalLifeFusion ====================

class PrivacyLevel(Enum):
    """隐私级别"""
    PUBLIC = 1
    INTERNAL = 2
    CONFIDENTIAL = 3
    RESTRICTED = 4
    PERSONAL = 5


@dataclass
class UnifiedDataRecord:
    """统一数据格式"""
    record_id: str
    source: str  # 来源服务
    source_id: str  # 原始ID
    content: str
    content_type: str  # 'text', 'code', 'image', 'link'
    timestamp: float
    privacy_level: PrivacyLevel = PrivacyLevel.PERSONAL
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceConnection:
    """服务连接状态"""
    service_name: str
    connected: bool
    last_sync: Optional[float] = None
    record_count: int = 0
    status: str = "active"


class DigitalLifeFusion:
    """
    M85: 数字生活融合引擎
    
    实现OpenHuman的118+ OAuth集成：
    - OAuth一键授权
    - 统一数据格式
    - 隐私保护
    
    定理T60: 数字生活融合定理 - Context完整度 = f(连接服务数)
    """
    
    # 支持的服务类别
    SERVICE_CATEGORIES = {
        'email': ['gmail', 'outlook', 'qqmail'],
        'notion': ['notion', '印象笔记', 'roam'],
        'code': ['github', 'gitlab', 'gitee', 'jira'],
        'chat': ['slack', 'discord', '钉钉', '企业微信', '飞书'],
        'calendar': ['google_calendar', 'apple_calendar'],
        'social': ['twitter', '微信', '微信读书'],
        'cloud': ['dropbox', 'onedrive', '微云'],
        'productivity': ['notion', 'trello', 'asana', 'monday'],
        'finance': ['stripe', '支付宝', '微信支付'],
        'health': ['apple_health', 'google_fit']
    }
    
    # 隐私敏感词
    PRIVACY_SENSITIVE_PATTERNS = [
        'password', '密码', 'secret', '密钥', 'token', '私钥',
        '银行卡', 'credit card', 'ssn', '身份证'
    ]
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.connected_services: Dict[str, ServiceConnection] = {}
        self.unified_data: List[UnifiedDataRecord] = []
        self.privacy_config = {
            'default_level': PrivacyLevel.PERSONAL,
            'auto_detect_sensitive': True
        }
    
    def connect_service(self, service_name: str) -> Dict:
        """
        连接服务（OAuth流程）
        
        Returns:
            授权URL，等待用户授权
        """
        # 检查服务是否支持
        is_supported = any(service_name in cats for cats in self.SERVICE_CATEGORIES.values())
        
        if not is_supported:
            return {
                'success': False,
                'error': f'Service {service_name} not supported'
            }
        
        # 返回授权URL（简化版本）
        auth_url = f"https://oauth.{service_name}.com/authorize?client_id=taiji_agi"
        
        self.connected_services[service_name] = ServiceConnection(
            service_name=service_name,
            connected=True,
            status="pending_auth"
        )
        
        return {
            'success': True,
            'auth_url': auth_url,
            'service': service_name
        }
    
    def complete_auth(self, service_name: str, auth_code: str) -> bool:
        """完成OAuth授权"""
        if service_name in self.connected_services:
            self.connected_services[service_name].status = "active"
            self.connected_services[service_name].last_sync = time.time()
            return True
        return False
    
    def disconnect_service(self, service_name: str) -> bool:
        """断开服务连接"""
        if service_name in self.connected_services:
            del self.connected_services[service_name]
            # 从unified_data中移除该服务的数据
            self.unified_data = [d for d in self.unified_data if d.source != service_name]
            return True
        return False
    
    def fetch_service_data(self, service_name: str) -> List[Dict]:
        """从服务获取数据（简化版本）"""
        # 实际应调用各服务的API
        if service_name not in self.connected_services:
            return []
        
        # 模拟返回数据
        return [
            {'id': f'{service_name}_1', 'content': f'{service_name}数据1', 'type': 'text'},
            {'id': f'{service_name}_2', 'content': f'{service_name}数据2', 'type': 'text'}
        ]
    
    def unify_data(self, raw_data: List[Dict], source: str) -> List[UnifiedDataRecord]:
        """
        统一数据格式
        
        将不同服务的数据转换为统一格式
        """
        unified = []
        
        for item in raw_data:
            record = UnifiedDataRecord(
                record_id=self._generate_record_id(item, source),
                source=source,
                source_id=item.get('id', ''),
                content=item.get('content', ''),
                content_type=item.get('type', 'text'),
                timestamp=item.get('timestamp', time.time()),
                metadata=item.get('metadata', {})
            )
            
            # 隐私级别检测
            if self.privacy_config['auto_detect_sensitive']:
                record.privacy_level = self._detect_privacy_level(record.content)
            
            unified.append(record)
        
        return unified
    
    def _generate_record_id(self, item: Dict, source: str) -> str:
        """生成唯一记录ID"""
        data = f"{source}:{item.get('id', '')}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _detect_privacy_level(self, content: str) -> PrivacyLevel:
        """检测隐私级别"""
        content_lower = content.lower()
        
        for pattern in self.PRIVACY_SENSITIVE_PATTERNS:
            if pattern.lower() in content_lower:
                return PrivacyLevel.RESTRICTED
        
        # 默认级别
        return self.privacy_config['default_level']
    
    def privacy_filter(self, data: List[UnifiedDataRecord], 
                      max_level: PrivacyLevel = PrivacyLevel.PERSONAL) -> List[UnifiedDataRecord]:
        """
        隐私过滤
        
        移除超过指定隐私级别的数据
        """
        return [d for d in data if d.privacy_level.value <= max_level.value]
    
    def query_cross_service(self, query: str) -> List[UnifiedDataRecord]:
        """
        跨服务查询
        
        在所有已连接服务的数据中搜索
        """
        results = []
        query_lower = query.lower()
        
        for record in self.unified_data:
            if query_lower in record.content.lower():
                results.append(record)
        
        # 按时间排序
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        return results
    
    def merge_results(self, results: List[UnifiedDataRecord]) -> Dict:
        """合并跨服务查询结果"""
        return {
            'total': len(results),
            'sources': list(set(r.source for r in results)),
            'records': [r.__dict__ for r in results[:50]],  # 最多50条
            'merge_timestamp': time.time()
        }
    
    def get_state(self) -> Dict:
        """获取数字生活融合状态"""
        return {
            'connected_services': {
                name: conn.__dict__ 
                for name, conn in self.connected_services.items()
            },
            'total_services': len(self.connected_services),
            'total_records': len(self.unified_data),
            'theorem_T60': {
                'context_completeness': self._compute_context_completeness(),
                'service_count': len(self.connected_services)
            }
        }
    
    def _compute_context_completeness(self) -> float:
        """计算上下文完整度（定理T60）"""
        # 简化：完整度 = 1 - e^(-服务数/5)
        import math
        n = len(self.connected_services)
        return 1 - math.exp(-n / 5)


# ==================== M86: ObsidianCompatLayer ====================

import os
import re


@dataclass
class ObsidianNote:
    """Obsidian笔记"""
    filename: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)  # 出链
    backlinks: List[str] = field(default_factory=list)  # 反链
    created: float = field(default_factory=time.time)
    modified: float = field(default_factory=time.time)


class ObsidianCompatLayer:
    """
    M86: Obsidian兼容导出层
    
    实现OpenHuman的Obsidian兼容：
    - Wiki链接语法 [[link|display]]
    - MOC (Map of Content)
    - Tags自动提取
    - 双向链接
    """
    
    # Wiki链接正则
    WIKI_LINK_PATTERN = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    # Tag正则
    TAG_PATTERN = re.compile(r'#[\w\-/]+')
    # Markdown链接正则
    MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    
    def __init__(self, output_dir: str = "./knowledge_base"):
        self.output_dir = output_dir
        self.notes: Dict[str, ObsidianNote] = {}
        self.link_graph: Dict[str, List[str]] = {}  # forward links
        self.backlink_graph: Dict[str, List[str]] = {}  # backlinks
    
    def create_wiki_link(self, target: str, display: Optional[str] = None) -> str:
        """创建Wiki链接 [[target|display]]"""
        if display and display != target:
            return f"[[{target}|{display}]]"
        return f"[[{target}]]"
    
    def create_wiki_link_auto(self, target: str) -> str:
        """自动创建Wiki链接（使用clean name作为显示名）"""
        clean = self._clean_filename(target)
        if clean != target:
            return f"[[{target}|{clean}]]"
        return f"[[{target}]]"
    
    def _clean_filename(self, name: str) -> str:
        """清理文件名"""
        # 移除特殊字符
        clean = re.sub(r'[^\w\s\-\u4e00-\u9fff]', '', name)
        # 空格替换为-
        clean = clean.strip().replace(' ', '-')
        return clean[:50]  # 限制长度
    
    def extract_tags(self, content: str) -> List[str]:
        """从内容中提取Tags"""
        tags = self.TAG_PATTERN.findall(content)
        # 清理tag
        tags = [t[1:] if t.startswith('#') else t for t in tags]
        return list(set(tags))
    
    def extract_links(self, content: str) -> List[str]:
        """从内容中提取Wiki链接"""
        matches = self.WIKI_LINK_PATTERN.findall(content)
        return [m[0] for m in matches]
    
    def build_backlinks(self, note_id: str):
        """构建反向链接"""
        if note_id not in self.backlink_graph:
            self.backlink_graph[note_id] = []
        
        for note_name, note in self.notes.items():
            if note_id in note.links:
                self.backlink_graph[note_id].append(note_name)
    
    def write_note(self, note: ObsidianNote):
        """写入Obsidian笔记"""
        # 确保目录存在
        note_dir = os.path.join(self.output_dir, 'notes')
        os.makedirs(note_dir, exist_ok=True)
        
        # 生成文件名
        filename = self._clean_filename(note.filename)
        filepath = os.path.join(note_dir, f"{filename}.md")
        
        # 格式化内容
        content = self._format_as_obsidian(note)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新索引
        self.notes[filename] = note
    
    def _format_as_obsidian(self, note: ObsidianNote) -> str:
        """格式化为Obsidian笔记"""
        lines = [
            "---",
            f"created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(note.created))}",
            f"modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(note.modified))}",
            ("tags: [" + ", ".join('"' + t + '"' for t in note.tags) + "]") if note.tags else "tags: []",
            ("links: [" + ", ".join('"' + l + '"' for l in note.links) + "]") if note.links else "links: []",
            "---",
            "",
            f"# {note.title}",
            "",
            note.content,
        ]
        
        # 添加反向链接
        if self.backlink_graph.get(note.filename):
            lines.extend([
                "",
                "---",
                "## 反向链接",
                ""
            ])
            for source in self.backlink_graph[note.filename]:
                lines.append(f"- [[{source}]]")
        
        return '\n'.join(lines)
    
    def create_moc(self, title: str, notes: List[str], output_name: str = "00_MOC") -> ObsidianNote:
        """
        创建Map of Content索引
        
        Args:
            title: MOC标题
            notes: 包含的笔记列表
            output_name: 输出文件名
        """
        lines = [
            f"# {title}",
            "",
            f"> 创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 索引",
            ""
        ]
        
        for note_name in notes:
            clean = self._clean_filename(note_name)
            lines.append(f"- [[{note_name}|{clean}]]")
        
        note = ObsidianNote(
            filename=output_name,
            title=title,
            content='\n'.join(lines),
            tags=['MOC', '索引']
        )
        
        self.write_note(note)
        return note
    
    def export_from_memory_tree(self, memory_tree) -> Dict[str, str]:
        """
        从记忆树导出为Obsidian格式
        
        Args:
            memory_tree: MemoryTreeEngine实例
        
        Returns:
            生成的笔记映射
        """
        generated = {}
        
        # Layer 1: 近期记忆
        layer1_dir = os.path.join(self.output_dir, 'layer1_recent')
        os.makedirs(layer1_dir, exist_ok=True)
        
        for i, chunk in enumerate(memory_tree.layer1_recent):
            note = ObsidianNote(
                filename=f"{chunk.timestamp}_{i}",
                title=f"近期记忆 {time.strftime('%Y-%m-%d', time.localtime(chunk.timestamp))}",
                content=chunk.content,
                tags=chunk.tags,
                created=chunk.timestamp,
                modified=chunk.timestamp
            )
            self.write_note(note)
            generated[chunk.chunk_id] = os.path.join(layer1_dir, f"{note.filename}.md")
        
        # Layer 2: 月度摘要
        layer2_dir = os.path.join(self.output_dir, 'layer2_monthly')
        os.makedirs(layer2_dir, exist_ok=True)
        
        for chunk in memory_tree.layer2_monthly:
            theme = chunk.source.replace('layer2_summary:', '')
            note = ObsidianNote(
                filename=f"monthly_{theme}",
                title=f"月度摘要: {theme}",
                content=chunk.content,
                tags=['monthly', 'summary'] + chunk.tags,
                created=chunk.timestamp,
                modified=chunk.timestamp
            )
            self.write_note(note)
            generated[chunk.chunk_id] = os.path.join(layer2_dir, f"{note.filename}.md")
        
        # Layer 3: 年度概览
        layer3_dir = os.path.join(self.output_dir, 'layer3_yearly')
        os.makedirs(layer3_dir, exist_ok=True)
        
        for chunk in memory_tree.layer3_yearly:
            theme = chunk.source.replace('layer3_overview:', '')
            note = ObsidianNote(
                filename=f"yearly_{theme}",
                title=f"年度概览: {theme}",
                content=chunk.content,
                tags=['yearly', 'overview'] + chunk.tags,
                created=chunk.timestamp,
                modified=chunk.timestamp
            )
            self.write_note(note)
            generated[chunk.chunk_id] = os.path.join(layer3_dir, f"{note.filename}.md")
        
        # 生成MOC
        self.create_moc(
            title="记忆库总览 | Memory Tree MOC",
            notes=[n.filename for n in self.notes.values() if n.filename != "00_MOC"],
            output_name="00_Memory_Tree_MOC"
        )
        
        return generated
    
    def get_state(self) -> Dict:
        """获取导出状态"""
        return {
            'output_dir': self.output_dir,
            'total_notes': len(self.notes),
            'link_graph_size': len(self.link_graph),
            'backlink_graph_size': len(self.backlink_graph)
        }


# ==================== M87: ZeroTrainingContext ====================

@dataclass
class ColdStartResult:
    """冷启动结果"""
    status: str
    timeline: List[Tuple[int, str]]  # (step, description)
    context_completeness: float
    services_connected: int
    memory_chunks: int


class ZeroTrainingContext:
    """
    M87: 零训练期认知系统
    
    实现OpenHuman的"零训练期认知"：
    - 首次连接即有完整上下文
    - 自适应学习速率
    - 个性化记忆
    
    定理T56: 零训练期认知定理 - 上下文完整度 ∝ ln(t+1)
    """
    
    COLD_START_STEPS = [
        (0, "连接OAuth服务"),
        (1, "拉取关键数据"),
        (2, "TokenJuice压缩"),
        (3, "构建记忆树"),
        (4, "生成用户画像")
    ]
    
    def __init__(self, 
                 memory_tree_engine=None,
                 token_juice_compressor=None,
                 digital_life_fusion=None):
        self.memory_engine = memory_tree_engine
        self.token_juice = token_juice_compressor
        self.digital_life = digital_life_fusion
        
        self.user_profile = {
            'interests': [],
            'expertise': [],
            'communication_style': 'balanced',
            'cognitive_load': 'medium',
            'adaptation_rate': 0.1,
            'cold_start_complete': False
        }
        
        self.sync_count = 0
        self.adaptation_rate = 0.1
    
    def cold_start(self, user_id: str) -> ColdStartResult:
        """
        冷启动：快速建立基础上下文
        
        目标：几分钟内建立完整上下文
        """
        timeline = []
        
        # Step 0: 连接OAuth服务
        timeline.append((0, "连接OAuth服务"))
        if self.digital_life:
            services = list(self.digital_life.connected_services.keys())
        else:
            services = []
        
        # Step 1: 拉取关键数据
        timeline.append((1, "拉取关键数据"))
        all_data = []
        if self.digital_life:
            for service in services:
                data = self.digital_life.fetch_service_data(service)
                all_data.extend(data)
        
        # Step 2: TokenJuice压缩
        timeline.append((2, "TokenJuice压缩"))
        if self.token_juice:
            compressed_data = []
            for item in all_data:
                content = item.get('content', '')
                result = self.token_juice.compress(content)
                compressed_data.append(result.compressed)
        else:
            compressed_data = [d.get('content', '') for d in all_data]
        
        # Step 3: 构建记忆树
        timeline.append((3, "构建记忆树"))
        if self.memory_engine:
            user_data = {'cold_start': compressed_data}
            self.memory_engine.build_tree(user_data)
        
        # Step 4: 生成用户画像
        timeline.append((4, "生成用户画像"))
        self._generate_profile(compressed_data)
        self.user_profile['cold_start_complete'] = True
        
        # 计算上下文完整度
        # 定理T56: C(t) ∝ ln(t+1), t=同步次数（首次=1）
        context_completeness = self._compute_completeness(1)
        
        return ColdStartResult(
            status='cold_start_complete',
            timeline=timeline,
            context_completeness=context_completeness,
            services_connected=len(services),
            memory_chunks=len(compressed_data)
        )
    
    def adaptive_update(self, interaction: Dict, feedback: Optional[Dict] = None):
        """
        自适应更新：基于交互调整上下文
        
        Args:
            interaction: 当前交互
            feedback: 用户反馈
        """
        self.sync_count += 1
        
        # 更新用户画像
        if feedback:
            # 根据反馈调整
            helpfulness = feedback.get('helpfulness', 0.5)
            
            if helpfulness < 0.3:
                # 低帮助性，降低权重
                self.user_profile['adaptation_rate'] *= 0.9
            elif helpfulness > 0.8:
                # 高帮助性，记住这个模式
                topics = interaction.get('topics', [])
                self.user_profile['interests'].extend(topics)
        
        # 更新上下文完整度
        completeness = self._compute_completeness(self.sync_count)
        
        return {
            'sync_count': self.sync_count,
            'context_completeness': completeness,
            'profile_updated': True
        }
    
    def _generate_profile(self, data: List[str]):
        """生成用户画像"""
        all_text = ' '.join(data)
        
        # 简单关键词提取
        interest_keywords = [
            '编程', 'AI', '技术', '设计', '商业', '金融',
            'science', 'tech', 'design', 'business', 'finance'
        ]
        
        for kw in interest_keywords:
            if kw in all_text:
                self.user_profile['interests'].append(kw)
        
        # 去重
        self.user_profile['interests'] = list(set(self.user_profile['interests']))
    
    def _compute_completeness(self, t: int) -> float:
        """
        计算上下文完整度
        
        定理T56: C(t) = min(0.95, 0.5 * ln(t+1))
        """
        import math
        completeness = 0.5 * math.log(t + 1)
        return min(0.95, completeness)
    
    def query_with_context(self, query: str) -> Dict:
        """
        带上下文的查询
        
        结合记忆树和用户画像生成个性化响应
        """
        # 从记忆树检索
        if self.memory_engine:
            relevant_chunks = self.memory_engine.query_context(query, top_k=5)
        else:
            relevant_chunks = []
        
        # 结合用户画像
        context = {
            'query': query,
            'relevant_memories': [c.content for c in relevant_chunks],
            'user_profile': self.user_profile,
            'context_completeness': self._compute_completeness(self.sync_count)
        }
        
        return context
    
    def get_state(self) -> Dict:
        """获取零训练期认知状态"""
        return {
            'cold_start_complete': self.user_profile['cold_start_complete'],
            'sync_count': self.sync_count,
            'context_completeness': self._compute_completeness(self.sync_count),
            'user_profile': self.user_profile,
            'theorem_T56': {
                'value': self._compute_completeness(self.sync_count),
                'formula': 'C(t) = min(0.95, 0.5 * ln(t+1))'
            }
        }


# ==================== 工厂函数 ====================

def create_digital_life_fusion(user_id: str = "default") -> DigitalLifeFusion:
    """M85工厂函数"""
    return DigitalLifeFusion(user_id=user_id)


def create_obsidian_compat_layer(output_dir: str = "./knowledge_base") -> ObsidianCompatLayer:
    """M86工厂函数"""
    return ObsidianCompatLayer(output_dir=output_dir)


def create_zero_training_context(memory_engine=None, 
                                  token_juice=None,
                                  digital_life=None) -> ZeroTrainingContext:
    """M87工厂函数"""
    return ZeroTrainingContext(
        memory_tree_engine=memory_engine,
        token_juice_compressor=token_juice,
        digital_life_fusion=digital_life
    )


# 全局单例 — M85 DigitalLifeFusion为主入口
_m85_instance: Optional['DigitalLifeFusion'] = None

def get_instance() -> 'DigitalLifeFusion':
    """获取M85 DigitalLifeFusion全局单例"""
    global _m85_instance
    if _m85_instance is None:
        _m85_instance = DigitalLifeFusion()
    return _m85_instance

def get_state() -> Dict:
    """模块级get_state，与其他模块统一"""
    return get_instance().get_state()


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("M85-M87 OpenHuman扩展模块测试")
    print("=" * 60)
    
    # M85测试
    print("\n【M85: DigitalLifeFusion】")
    dlf = DigitalLifeFusion()
    
    # 连接服务
    result = dlf.connect_service("gmail")
    print(f"连接Gmail: {result}")
    
    # 获取状态
    state = dlf.get_state()
    print(f"连接服务数: {state['total_services']}")
    print(f"定理T60上下文完整度: {state['theorem_T60']['context_completeness']:.2%}")
    
    # M86测试
    print("\n【M86: ObsidianCompatLayer】")
    obsidian = ObsidianCompatLayer(output_dir="./test_knowledge")
    
    # 创建Wiki链接
    link = obsidian.create_wiki_link("测试笔记", "测试")
    print(f"Wiki链接: {link}")
    
    # 创建笔记
    note = ObsidianNote(
        filename="test_note",
        title="测试笔记",
        content="# 测试内容\n\n这是一个测试。\n\n#test #示例",
        tags=['test', 'example']
    )
    obsidian.write_note(note)
    
    state = obsidian.get_state()
    print(f"生成的笔记数: {state['total_notes']}")
    
    # M87测试
    print("\n【M87: ZeroTrainingContext】")
    ztc = ZeroTrainingContext()
    
    # 冷启动
    result = ztc.cold_start("test_user")
    print(f"冷启动状态: {result.status}")
    print(f"上下文完整度: {result.context_completeness:.2%}")
    
    state = ztc.get_state()
    print(f"定理T56: {state['theorem_T56']}")
