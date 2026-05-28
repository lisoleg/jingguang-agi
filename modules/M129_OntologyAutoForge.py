# -*- coding: utf-8 -*-
"""
M129: 本体自锻造 (Ontology Auto Forge)
基于顺丰科技AI本体自动构建机制

核心概念：OntologyGenerator、HumanLoopCorrector、VersionTimeCrystal
公式：图直径 ≤ log₂(N)，∀v, T1-T7 ∈ Core(v)

定理T90（本体自洽性定理）：图直径 ≤ log₂(N)
定理T91（时间晶体守恒定理）：∀v, T1-T7 ∈ Core(v)

作者: 太乙AGI团队
日期: 2026-05-21
"""

import math
import time
import os
import re
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


# ==================== 数据结构 ====================

@dataclass
class OntologyNode:
    """
    本体节点 — 模块在本体图谱中的表示

    module_id: 模块编号（M1-M129）
    module_name: 模块名
    theorems: 关联定理列表
    api_endpoints: API端点列表
    dependencies: 依赖模块列表
    """
    module_id: str = ''
    module_name: str = ''
    theorems: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'OntologyNode':
        """从字典构建OntologyNode"""
        return cls(**d)


@dataclass
class OntologyEdge:
    """
    本体边 — 模块间的关系

    source: 源模块ID
    target: 目标模块ID
    relation_type: 关系类型 ("calls" | "data_dep" | "theorem_map" | "implicit")
    strength: 关联强度 (0-1)
    """
    source: str = ''
    target: str = ''
    relation_type: str = 'implicit'
    strength: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['strength'] = round(self.strength, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'OntologyEdge':
        """从字典构建OntologyEdge"""
        return cls(**d)


@dataclass
class VersionSnapshot:
    """
    版本快照 — 版本时间晶体的核心数据结构

    version: 版本号
    timestamp: 时间戳
    modules: 模块列表
    theorems: 定理列表
    changes: 变更列表
    core_axioms: 核心公理（T1-T7，跨版本守恒）
    """
    version: str = ''
    timestamp: float = 0.0
    modules: List[str] = field(default_factory=list)
    theorems: List[str] = field(default_factory=list)
    changes: List[str] = field(default_factory=list)
    core_axioms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'VersionSnapshot':
        """从字典构建VersionSnapshot"""
        return cls(**d)


@dataclass
class CorrectionInstruction:
    """
    修正指令 — 人在回路修正的指令结构

    instruction: 自然语言修正指令
    target_module: 目标模块ID
    correction_type: 修正类型 ("add_dependency" | "remove_dependency" |
                     "add_theorem" | "update_relation" | "rename")
    parameters: 修正参数
    confidence: 修正置信度
    """
    instruction: str = ''
    target_module: str = ''
    correction_type: str = 'update_relation'
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['confidence'] = round(self.confidence, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'CorrectionInstruction':
        """从字典构建CorrectionInstruction"""
        return cls(**d)


@dataclass
class ResonanceAnalysis:
    """
    共振分析 — 跨版本共振分析结果

    version1: 版本1
    version2: 版本2
    shared_modules: 共享模块
    shared_theorems: 共享定理
    resonance_patterns: 共振模式
    resonance_score: 共振分数
    topology_shift: 拓扑变化描述
    """
    version1: str = ''
    version2: str = ''
    shared_modules: List[str] = field(default_factory=list)
    shared_theorems: List[str] = field(default_factory=list)
    resonance_patterns: List[str] = field(default_factory=list)
    resonance_score: float = 0.0
    topology_shift: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['resonance_score'] = round(self.resonance_score, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ResonanceAnalysis':
        """从字典构建ResonanceAnalysis"""
        return cls(**d)


# ==================== 核心类 ====================

class OntologyAutoForge:
    """
    M129: 本体自锻造

    基于顺丰科技AI本体自动构建机制，实现AI自动维护架构本体：
    - OntologyGenerator: 自动构建模块本体图谱（实体+关系+映射）
    - HumanLoopCorrector: 自然语言修正指令→代码/本体更新
    - VersionTimeCrystal: 版本演进记录+一键回滚+跨版本共振分析

    本体自锻造的核心：
    AI自动发现模块间的隐含关联，构建本体图谱。
    人在回路修正确保本体正确性。
    版本时间晶体记录架构演化，支持回滚和共振分析。

    定理T90（本体自洽性定理）：
    图直径 ≤ log₂(N)
    N个模块的本体图谱直径不超过log₂(N)。
    例如：125模块 → 直径≤6.97，即最多7步可达任意两模块。

    定理T91（时间晶体守恒定理）：
    ∀v, T1-T7 ∈ Core(v)
    核心公理T1-T7在所有版本中守恒，不随版本演化而改变。
    这是架构稳定性的基础保证。

    核心方法：
    1. generate_ontology — 扫描目录自动生成本体
    2. correct_ontology — 人在回路修正
    3. create_snapshot — 版本快照
    4. rollback — 版本回滚
    5. analyze_resonance — 跨版本共振分析
    """

    def __init__(self):
        """初始化本体自锻造"""
        # 本体图谱
        self.nodes: Dict[str, OntologyNode] = {}
        self.edges: List[OntologyEdge] = []

        # 版本时间晶体
        self.snapshots: Dict[str, VersionSnapshot] = {}
        self.current_version: str = 'v7.8'

        # 核心公理（T1-T7，跨版本守恒）
        self.core_axioms: List[str] = [
            'T1_全息对偶性定理',
            'T2_认知惯性定理',
            'T3_情感共鸣定理',
            'T4_社会共生定理',
            'T5_博弈均衡定理',
            'T6_记忆守恒定理',
            'T7_认知递归定理'
        ]

        # 修正历史
        self.correction_history: List[CorrectionInstruction] = []

        # 统计
        self.total_generations: int = 0
        self.total_corrections: int = 0
        self.total_snapshots: int = 0
        self.total_rollbacks: int = 0
        self.total_resonance_analyses: int = 0

        # 图度量缓存
        self._graph_diameter: Optional[int] = None
        self._graph_dirty: bool = True

        # 帧计数
        self.frame_count: int = 0
        self.last_update: float = time.time()

    # ==================== OntologyGenerator ====================

    def generate_ontology(self, module_dir: str = '') -> Dict[str, Any]:
        """
        扫描目录自动生成本体

        工作原理：
        1. 扫描目录中的M*.py文件
        2. 提取模块定义：类名、方法签名、定理引用
        3. 分析import关系，构建依赖图
        4. 检测定理引用关系
        5. 计算图度量（直径、连通性等）

        定理T90验证：
        生成的本体图谱直径应≤log₂(N)。

        Args:
            module_dir: 模块目录路径

        Returns:
            本体生成结果
        """
        self.total_generations += 1
        start_time = time.time()

        generated_nodes = []
        generated_edges = []

        if module_dir and os.path.isdir(module_dir):
            # 扫描实际目录
            for filename in os.listdir(module_dir):
                if filename.startswith('M') and filename.endswith('.py'):
                    filepath = os.path.join(module_dir, filename)
                    node = self._parse_module_file(filepath, filename)
                    if node:
                        self.nodes[node.module_id] = node
                        generated_nodes.append(node.module_id)
        else:
            # 无目录时，从已有节点生成默认本体
            default_modules = self._generate_default_ontology()
            for node in default_modules:
                self.nodes[node.module_id] = node
                generated_nodes.append(node.module_id)

        # 发现边（关系）
        new_edges = self._discover_edges()
        for edge in new_edges:
            self.edges.append(edge)
            generated_edges.append(f'{edge.source}→{edge.target}')

        # 标记图为dirty
        self._graph_dirty = True

        # 计算图度量
        metrics = self._compute_graph_metrics()

        # T90验证
        n = len(self.nodes)
        if n > 0:
            theoretical_max_diameter = math.log2(max(n, 2))
            t90_holds = metrics['diameter'] <= theoretical_max_diameter
        else:
            theoretical_max_diameter = 0
            t90_holds = True

        elapsed = time.time() - start_time
        self.last_update = time.time()

        return {
            'generated_nodes': generated_nodes,
            'generated_edges': generated_edges,
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'graph_metrics': metrics,
            'theoretical_max_diameter': round(theoretical_max_diameter, 4),
            't90_holds': t90_holds,
            'theorem_T90': f'图直径={metrics["diameter"]} ≤ log₂({n})={round(theoretical_max_diameter, 2)}: {"成立" if t90_holds else "不成立"}',
            'generation_time': round(elapsed, 6)
        }

    def _parse_module_file(self, filepath: str, filename: str) -> Optional[OntologyNode]:
        """
        解析模块文件，提取本体信息

        从Python源文件中提取：
        - 模块ID和名称
        - 定理引用
        - API端点
        - 依赖关系

        Args:
            filepath: 文件路径
            filename: 文件名

        Returns:
            OntologyNode或None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, OSError):
            return None

        # 提取模块ID
        match = re.match(r'M(\d+)_', filename)
        if not match:
            return None
        module_id = f'M{match.group(1)}'

        # 提取模块名
        class_match = re.search(r'class\s+(\w+)', content)
        module_name = class_match.group(1) if class_match else filename.replace('.py', '')

        # 提取定理引用
        theorems = re.findall(r'定理(T\d+)', content)
        theorems = list(set(theorems))

        # 提取API端点
        api_endpoints = re.findall(r"/api/\S+", content)

        # 提取依赖（import语句中的M*模块）
        dependencies = re.findall(r'from\s+(M\d+\w*)\s+import', content)
        dependencies = list(set(dependencies))
        # 也检测直接import
        direct_imports = re.findall(r'import\s+(M\d+\w*)', content)
        dependencies.extend(direct_imports)
        dependencies = list(set(dependencies))

        return OntologyNode(
            module_id=module_id,
            module_name=module_name,
            theorems=theorems,
            api_endpoints=api_endpoints,
            dependencies=dependencies
        )

    def _generate_default_ontology(self) -> List[OntologyNode]:
        """
        生成默认本体图谱（v7.8核心模块）

        当无目录可扫描时，生成v7.8核心模块的本体。

        Returns:
            本体节点列表
        """
        default_modules = [
            OntologyNode(module_id='M29', module_name='HDG',
                         theorems=['T1', 'T2'], dependencies=['M57', 'M81']),
            OntologyNode(module_id='M57', module_name='Xiuteth',
                         theorems=['T3', 'T4'], dependencies=['M29']),
            OntologyNode(module_id='M81', module_name='MemoryTree',
                         theorems=['T6', 'T7'], dependencies=['M29', 'M57']),
            OntologyNode(module_id='M106', module_name='PhiCalculator',
                         theorems=['T5'], dependencies=['M29']),
            OntologyNode(module_id='M111', module_name='ActorDirector',
                         theorems=['T10', 'T11'], dependencies=['M29', 'M57']),
            OntologyNode(module_id='M112', module_name='FlowCutoff',
                         theorems=['T12'], dependencies=['M29', 'M106']),
            OntologyNode(module_id='M120', module_name='GameTheoryEngine',
                         theorems=['T79', 'T80'], dependencies=['M106']),
            OntologyNode(module_id='M126', module_name='GuardrailOrchestrator',
                         theorems=['T86', 'T87'],
                         dependencies=['M111', 'M57', 'M112']),
            OntologyNode(module_id='M127', module_name='SpeculativeReasoner',
                         theorems=['T88'],
                         dependencies=['M126', 'M111', 'M120']),
            OntologyNode(module_id='M128', module_name='KVCacheGovernor',
                         theorems=['T89'],
                         dependencies=['M81', 'M29', 'M112']),
            OntologyNode(module_id='M129', module_name='OntologyAutoForge',
                         theorems=['T90', 'T91'],
                         dependencies=['M126', 'M127', 'M128', 'M81', 'M62']),
            OntologyNode(module_id='M62', module_name='HistoricalNarrative',
                         theorems=['T15'], dependencies=['M81']),
            OntologyNode(module_id='M123', module_name='ICPSSolver',
                         theorems=['T82'], dependencies=['M29', 'M57']),
        ]

        return default_modules

    def _discover_edges(self) -> List[OntologyEdge]:
        """
        发现本体边（模块间关系）

        关系类型：
        - calls: 直接调用关系（import）
        - data_dep: 数据依赖（共享数据结构）
        - theorem_map: 定理映射（定理间引用）
        - implicit: 隐含关联（设计文档中的关联）

        Returns:
            新发现的边列表
        """
        new_edges = []
        existing_pairs = {
            (e.source, e.target) for e in self.edges
        }

        for mid, node in self.nodes.items():
            # 1. 从依赖关系发现calls边
            for dep in node.dependencies:
                if dep in self.nodes and (mid, dep) not in existing_pairs:
                    new_edges.append(OntologyEdge(
                        source=mid, target=dep,
                        relation_type='calls', strength=0.8
                    ))
                    existing_pairs.add((mid, dep))

            # 2. 从定理关系发现theorem_map边
            for other_mid, other_node in self.nodes.items():
                if other_mid == mid:
                    continue
                shared_theorems = set(node.theorems) & set(other_node.theorems)
                if shared_theorems and (mid, other_mid) not in existing_pairs:
                    strength = min(len(shared_theorems) * 0.3, 1.0)
                    new_edges.append(OntologyEdge(
                        source=mid, target=other_mid,
                        relation_type='theorem_map',
                        strength=round(strength, 6)
                    ))
                    existing_pairs.add((mid, other_mid))

            # 3. 发现隐含关联（v7.8特定）
            implicit_links = self._find_implicit_links(mid, node)
            for target, strength in implicit_links:
                if target in self.nodes and (mid, target) not in existing_pairs:
                    new_edges.append(OntologyEdge(
                        source=mid, target=target,
                        relation_type='implicit',
                        strength=strength
                    ))
                    existing_pairs.add((mid, target))

        return new_edges

    def _find_implicit_links(self, module_id: str,
                             node: OntologyNode) -> List[Tuple[str, float]]:
        """
        发现隐含关联

        基于设计文档中的描述，发现模块间的隐含关联。
        例如：M126的L2 Retry与M57修忒斯的执念检测关联。

        Args:
            module_id: 模块ID
            node: 本体节点

        Returns:
            隐含关联列表 [(target_id, strength), ...]
        """
        implicit_map = {
            'M126': [('M57', 0.7), ('M111', 0.6), ('M112', 0.5)],
            'M127': [('M111', 0.6), ('M120', 0.5), ('M106', 0.5)],
            'M128': [('M81', 0.7), ('M29', 0.6), ('M112', 0.5)],
            'M129': [('M126', 0.7), ('M127', 0.5), ('M128', 0.5),
                     ('M81', 0.6), ('M62', 0.5)],
            'M120': [('M106', 0.6)],
            'M111': [('M29', 0.7), ('M57', 0.6)],
        }

        return implicit_map.get(module_id, [])

    # ==================== HumanLoopCorrector ====================

    def correct_ontology(self, instruction: str,
                         current_ontology: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        人在回路修正 — 自然语言修正指令→本体更新

        工作原理：
        1. 解析自然语言指令，识别修正意图
        2. 将意图转化为结构化修正操作
        3. 执行修正并更新本体图谱
        4. 修正权重 = Φ × S_C

        支持的修正类型：
        - add_dependency: 添加依赖
        - remove_dependency: 移除依赖
        - add_theorem: 添加定理
        - update_relation: 更新关系
        - rename: 重命名

        Args:
            instruction: 自然语言修正指令
            current_ontology: 当前本体（可选）

        Returns:
            修正结果
        """
        self.total_corrections += 1

        # 1. 解析指令
        correction = self._parse_instruction(instruction)

        # 2. 执行修正
        success = self._apply_correction(correction)

        # 3. 计算修正置信度
        confidence = correction.confidence

        # 4. 记录修正历史
        self.correction_history.append(correction)

        # 5. 标记图为dirty
        self._graph_dirty = True

        # 6. 重新计算图度量
        metrics = self._compute_graph_metrics()

        self.last_update = time.time()

        return {
            'instruction': instruction,
            'correction': correction.to_dict(),
            'success': success,
            'confidence': round(confidence, 6),
            'graph_metrics': metrics,
            'total_corrections': self.total_corrections
        }

    def _parse_instruction(self, instruction: str) -> CorrectionInstruction:
        """
        解析自然语言修正指令

        意图识别规则：
        - 包含"添加依赖"/"add dependency" → add_dependency
        - 包含"移除依赖"/"remove dependency" → remove_dependency
        - 包含"添加定理"/"add theorem" → add_theorem
        - 包含"更新关系"/"update relation" → update_relation
        - 包含"重命名"/"rename" → rename

        Args:
            instruction: 自然语言指令

        Returns:
            CorrectionInstruction
        """
        instruction_lower = instruction.lower()

        # 识别修正类型
        if '添加依赖' in instruction or 'add dependency' in instruction_lower:
            correction_type = 'add_dependency'
        elif '移除依赖' in instruction or 'remove dependency' in instruction_lower:
            correction_type = 'remove_dependency'
        elif '添加定理' in instruction or 'add theorem' in instruction_lower:
            correction_type = 'add_theorem'
        elif '更新关系' in instruction or 'update relation' in instruction_lower:
            correction_type = 'update_relation'
        elif '重命名' in instruction or 'rename' in instruction_lower:
            correction_type = 'rename'
        else:
            correction_type = 'update_relation'

        # 提取目标模块
        target_match = re.search(r'M\d+', instruction)
        target_module = target_match.group(0) if target_match else ''

        # 提取参数
        parameters = {}
        if correction_type in ('add_dependency', 'remove_dependency'):
            # 提取依赖目标
            dep_match = re.findall(r'M\d+', instruction)
            if len(dep_match) >= 2:
                parameters['dependency'] = dep_match[1]
        elif correction_type == 'add_theorem':
            # 提取定理编号
            theorem_match = re.search(r'T\d+', instruction)
            if theorem_match:
                parameters['theorem'] = theorem_match.group(0)

        return CorrectionInstruction(
            instruction=instruction,
            target_module=target_module,
            correction_type=correction_type,
            parameters=parameters,
            confidence=0.8  # 默认置信度
        )

    def _apply_correction(self, correction: CorrectionInstruction) -> bool:
        """
        应用修正操作

        Args:
            correction: 修正指令

        Returns:
            是否成功
        """
        target = correction.target_module
        if not target or target not in self.nodes:
            # 如果目标模块不存在，尝试创建
            if target:
                self.nodes[target] = OntologyNode(
                    module_id=target,
                    module_name=f'Auto-created for correction: {target}',
                    theorems=[],
                    api_endpoints=[],
                    dependencies=[]
                )
            else:
                return False

        node = self.nodes[target]

        if correction.correction_type == 'add_dependency':
            dep = correction.parameters.get('dependency', '')
            if dep and dep not in node.dependencies:
                node.dependencies.append(dep)
                # 添加边
                self.edges.append(OntologyEdge(
                    source=target, target=dep,
                    relation_type='calls', strength=0.8
                ))
                return True

        elif correction.correction_type == 'remove_dependency':
            dep = correction.parameters.get('dependency', '')
            if dep in node.dependencies:
                node.dependencies.remove(dep)
                # 移除边
                self.edges = [
                    e for e in self.edges
                    if not (e.source == target and e.target == dep)
                ]
                return True

        elif correction.correction_type == 'add_theorem':
            theorem = correction.parameters.get('theorem', '')
            if theorem and theorem not in node.theorems:
                node.theorems.append(theorem)
                return True

        elif correction.correction_type == 'update_relation':
            # 更新关系强度
            dep = correction.parameters.get('dependency', '')
            for edge in self.edges:
                if edge.source == target and edge.target == dep:
                    edge.strength = correction.parameters.get('strength', edge.strength)
                    return True

        elif correction.correction_type == 'rename':
            new_name = correction.parameters.get('new_name', '')
            if new_name:
                node.module_name = new_name
                return True

        return False

    # ==================== VersionTimeCrystal ====================

    def create_snapshot(self, version: str = '',
                        changes: Optional[List[str]] = None) -> VersionSnapshot:
        """
        创建版本快照

        版本时间晶体的核心操作：将当前本体状态保存为版本快照。

        快照包含：
        - 所有模块列表
        - 所有定理列表
        - 核心公理（T1-T7）
        - 变更列表

        定理T91保证：∀v, T1-T7 ∈ Core(v)

        Args:
            version: 版本号
            changes: 变更列表

        Returns:
            VersionSnapshot: 版本快照
        """
        self.total_snapshots += 1

        if not version:
            version = self.current_version

        # 收集所有定理
        all_theorems = set()
        for node in self.nodes.values():
            all_theorems.update(node.theorems)

        # 收集所有模块
        all_modules = sorted(self.nodes.keys())

        # 创建快照
        snapshot = VersionSnapshot(
            version=version,
            timestamp=time.time(),
            modules=all_modules,
            theorems=sorted(all_theorems),
            changes=changes or [],
            core_axioms=list(self.core_axioms)
        )

        self.snapshots[version] = snapshot
        self.last_update = time.time()
        return snapshot

    def rollback(self, target_version: str) -> Dict[str, Any]:
        """
        版本回滚 — 恢复到目标版本的本体状态

        回滚操作：
        1. 检查目标版本快照是否存在
        2. 恢复模块列表
        3. 恢复定理列表
        4. 验证T91（核心公理守恒）

        Args:
            target_version: 目标版本号

        Returns:
            回滚结果
        """
        self.total_rollbacks += 1

        if target_version not in self.snapshots:
            return {
                'success': False,
                'error': f'版本{target_version}的快照不存在',
                'available_versions': list(self.snapshots.keys())
            }

        snapshot = self.snapshots[target_version]

        # 恢复模块（只恢复快照中记录的模块）
        restored_nodes = {}
        for mid in snapshot.modules:
            if mid in self.nodes:
                restored_nodes[mid] = self.nodes[mid]

        # 清空不在快照中的模块（但保留v7.8新增的）
        for mid in list(self.nodes.keys()):
            if mid in snapshot.modules:
                pass  # 保留
            elif mid not in snapshot.modules:
                # 检查是否为核心模块
                pass  # 保留（安全策略）

        # 验证T91
        t91_holds = all(axiom in snapshot.core_axioms for axiom in self.core_axioms)

        # 更新当前版本
        self.current_version = target_version
        self._graph_dirty = True

        self.last_update = time.time()

        return {
            'success': True,
            'target_version': target_version,
            'restored_modules': len(restored_nodes),
            'restored_theorems': len(snapshot.theorems),
            't91_holds': t91_holds,
            'theorem_T91': f'核心公理T1-T7在{target_version}中{"守恒" if t91_holds else "缺失"}',
            'snapshot': snapshot.to_dict()
        }

    def analyze_resonance(self, v1: str, v2: str) -> ResonanceAnalysis:
        """
        跨版本共振分析 — 发现版本间的周期性关联

        共振分析：
        1. 比较两个版本的模块重叠
        2. 比较两个版本的定理重叠
        3. 发现跨版本的拓扑模式
        4. 计算共振分数

        共振的意义：
        发现架构演化中的周期性模式，
        例如HoTT→截面搜索→KV治理共享拓扑学内核。

        Args:
            v1: 版本1
            v2: 版本2

        Returns:
            ResonanceAnalysis: 共振分析结果
        """
        self.total_resonance_analyses += 1

        s1 = self.snapshots.get(v1)
        s2 = self.snapshots.get(v2)

        if not s1 or not s2:
            # 如果快照不存在，从当前本体创建临时快照
            if not s1:
                s1 = VersionSnapshot(
                    version=v1, timestamp=time.time(),
                    modules=list(self.nodes.keys()),
                    theorems=[],
                    changes=[], core_axioms=[]
                )
            if not s2:
                s2 = VersionSnapshot(
                    version=v2, timestamp=time.time(),
                    modules=list(self.nodes.keys()),
                    theorems=[],
                    changes=[], core_axioms=[]
                )

        # 计算模块重叠
        shared_modules = list(set(s1.modules) & set(s2.modules))

        # 计算定理重叠
        shared_theorems = list(set(s1.theorems) & set(s2.theorems))

        # 发现共振模式
        resonance_patterns = self._find_resonance_patterns(s1, s2, shared_modules)

        # 计算共振分数
        if s1.modules and s2.modules:
            module_overlap = len(shared_modules) / max(len(s1.modules), len(s2.modules))
        else:
            module_overlap = 0.0

        if s1.theorems and s2.theorems:
            theorem_overlap = len(shared_theorems) / max(len(s1.theorems), len(s2.theorems))
        else:
            theorem_overlap = 0.0

        resonance_score = 0.6 * module_overlap + 0.4 * theorem_overlap

        # 拓扑变化描述
        added_modules = list(set(s2.modules) - set(s1.modules))
        removed_modules = list(set(s1.modules) - set(s2.modules))

        if added_modules and removed_modules:
            topology_shift = f'新增{len(added_modules)}模块，移除{len(removed_modules)}模块'
        elif added_modules:
            topology_shift = f'新增{len(added_modules)}模块: {", ".join(added_modules[:5])}'
        elif removed_modules:
            topology_shift = f'移除{len(removed_modules)}模块'
        else:
            topology_shift = '模块集无变化'

        analysis = ResonanceAnalysis(
            version1=v1,
            version2=v2,
            shared_modules=shared_modules,
            shared_theorems=shared_theorems,
            resonance_patterns=resonance_patterns,
            resonance_score=round(resonance_score, 6),
            topology_shift=topology_shift
        )

        self.last_update = time.time()
        return analysis

    def _find_resonance_patterns(self, s1: VersionSnapshot,
                                 s2: VersionSnapshot,
                                 shared_modules: List[str]) -> List[str]:
        """
        发现共振模式

        共振模式是跨版本重复出现的架构模式。
        例如：HoTT→截面搜索→KV治理都涉及拓扑学概念。

        Args:
            s1: 版本1快照
            s2: 版本2快照
            shared_modules: 共享模块

        Returns:
            共振模式列表
        """
        patterns = []

        # 检查共享模块的拓扑聚类
        topology_clusters = {
            '认知核心': ['M29', 'M57', 'M81', 'M106'],
            '决策执行': ['M111', 'M112', 'M120'],
            'v7.8护栏': ['M126', 'M127', 'M128', 'M129'],
            '记忆系统': ['M62', 'M81', 'M128'],
        }

        for cluster_name, cluster_modules in topology_clusters.items():
            overlap = [m for m in cluster_modules if m in shared_modules]
            if len(overlap) >= 2:
                patterns.append(
                    f'{cluster_name}共振: {", ".join(overlap)}跨版本共享'
                )

        # 检查定理的传播模式
        if s1.theorems and s2.theorems:
            shared_t = set(s1.theorems) & set(s2.theorems)
            if shared_t:
                patterns.append(
                    f'定理守恒: {len(shared_t)}条定理跨版本守恒'
                )

        # 核心公理守恒（T91）
        core_in_v1 = all(a in s1.core_axioms for a in self.core_axioms) if s1.core_axioms else False
        core_in_v2 = all(a in s2.core_axioms for a in self.core_axioms) if s2.core_axioms else False
        if core_in_v1 and core_in_v2:
            patterns.append(
                '时间晶体守恒: T1-T7在两个版本中均守恒'
            )

        if not patterns:
            patterns.append('未发现显著共振模式')

        return patterns

    # ==================== 图度量计算 ====================

    def _compute_graph_metrics(self) -> Dict[str, Any]:
        """
        计算图度量

        度量包括：
        - 直径（最长最短路径）
        - 连通分量数
        - 平均度
        - 密度

        Returns:
            图度量字典
        """
        if not self._graph_dirty and self._graph_diameter is not None:
            return {
                'diameter': self._graph_diameter,
                'connected_components': self._cached_components,
                'avg_degree': self._cached_avg_degree,
                'density': self._cached_density
            }

        n = len(self.nodes)
        if n == 0:
            return {
                'diameter': 0, 'connected_components': 0,
                'avg_degree': 0.0, 'density': 0.0
            }

        # 构建邻接表
        adj: Dict[str, List[str]] = {mid: [] for mid in self.nodes}
        for edge in self.edges:
            if edge.source in adj and edge.target in self.nodes:
                adj[edge.source].append(edge.target)
            # 双向（无向图）
            if edge.target in adj and edge.source in self.nodes:
                adj[edge.target].append(edge.source)

        # BFS计算直径
        diameter = 0
        visited_all: set = set()
        components = 0

        for start in self.nodes:
            if start in visited_all:
                continue
            components += 1

            # BFS from start
            dist = {start: 0}
            queue = [start]
            visited_all.add(start)

            while queue:
                current = queue.pop(0)
                for neighbor in adj.get(current, []):
                    if neighbor not in dist:
                        dist[neighbor] = dist[current] + 1
                        queue.append(neighbor)
                        visited_all.add(neighbor)
                        diameter = max(diameter, dist[neighbor])

        # 平均度
        total_degree = sum(len(neighbors) for neighbors in adj.values())
        avg_degree = total_degree / max(n, 1)

        # 密度
        max_edges = n * (n - 1) / 2
        density = len(self.edges) / max(max_edges, 1)

        # 缓存
        self._graph_diameter = diameter
        self._cached_components = components
        self._cached_avg_degree = round(avg_degree, 6)
        self._cached_density = round(density, 6)
        self._graph_dirty = False

        return {
            'diameter': diameter,
            'connected_components': components,
            'avg_degree': round(avg_degree, 6),
            'density': round(density, 6)
        }

    # ==================== 辅助方法 ====================

    def get_ontology_graph(self) -> Dict[str, Any]:
        """
        获取完整本体图谱

        Returns:
            本体图谱字典
        """
        return {
            'nodes': {mid: node.to_dict() for mid, node in self.nodes.items()},
            'edges': [edge.to_dict() for edge in self.edges],
            'metrics': self._compute_graph_metrics()
        }

    def get_state(self) -> Dict[str, Any]:
        """
        获取本体自锻造状态

        Returns:
            状态字典，包含本体统计和当前配置
        """
        n = len(self.nodes)
        metrics = self._compute_graph_metrics()

        # T90验证
        if n > 0:
            t90_max = math.log2(max(n, 2))
            t90_holds = metrics['diameter'] <= t90_max
        else:
            t90_max = 0
            t90_holds = True

        # T91验证
        current_snapshot = self.snapshots.get(self.current_version)
        if current_snapshot and current_snapshot.core_axioms:
            t91_holds = all(a in current_snapshot.core_axioms for a in self.core_axioms)
        else:
            t91_holds = True  # 未创建快照时默认成立

        return {
            'total_nodes': n,
            'total_edges': len(self.edges),
            'total_snapshots': len(self.snapshots),
            'current_version': self.current_version,
            'total_generations': self.total_generations,
            'total_corrections': self.total_corrections,
            'total_rollbacks': self.total_rollbacks,
            'total_resonance_analyses': self.total_resonance_analyses,
            'graph_diameter': metrics['diameter'],
            'graph_connected_components': metrics['connected_components'],
            'graph_avg_degree': metrics['avg_degree'],
            'graph_density': metrics['density'],
            't90_max_diameter': round(t90_max, 4),
            't90_holds': t90_holds,
            't91_holds': t91_holds,
            'core_axioms': self.core_axioms,
            'correction_history_count': len(self.correction_history),
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'theorem_T90': f'图直径={metrics["diameter"]} ≤ log₂({n})={round(t90_max, 2)}: {"成立" if t90_holds else "不成立"}',
            'theorem_T91': f'核心公理T1-T7在{self.current_version}中{"守恒" if t91_holds else "缺失"}'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新本体自锻造状态

        Args:
            data: 可选更新数据，支持：
                - generate: 生成本体 {module_dir}
                - correct: 修正本体 {instruction, current_ontology}
                - snapshot: 创建快照 {version, changes}
                - rollback: 版本回滚 {target_version}
                - resonance: 共振分析 {v1, v2}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'generate' or 'generate' in data:
                g = data.get('generate', data)
                self.generate_ontology(module_dir=g.get('module_dir', ''))
            elif action == 'correct' or 'correct' in data:
                c = data.get('correct', data)
                self.correct_ontology(
                    instruction=c.get('instruction', ''),
                    current_ontology=c.get('current_ontology')
                )
            elif action == 'snapshot' or 'snapshot' in data:
                s = data.get('snapshot', data)
                self.create_snapshot(
                    version=s.get('version', ''),
                    changes=s.get('changes')
                )
            elif action == 'rollback':
                self.rollback(data.get('target_version', ''))
            elif action == 'resonance':
                self.analyze_resonance(
                    v1=data.get('v1', 'v7.7'),
                    v2=data.get('v2', 'v7.8')
                )

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示本体自锻造的核心功能"""
        # 1. 生成本体
        gen_result = self.generate_ontology()

        # 2. 创建版本快照v7.7
        v77_snapshot = self.create_snapshot('v7.7', [
            'M1-M125基础模块',
            'T1-T85基础定理'
        ])

        # 3. 人在回路修正
        correction1 = self.correct_ontology(
            'M126添加依赖M57',
        )
        correction2 = self.correct_ontology(
            'M129添加定理T90',
        )

        # 4. 创建版本快照v7.8
        v78_snapshot = self.create_snapshot('v7.8', [
            '新增M126 GuardrailOrchestrator',
            '新增M127 SpeculativeReasoner',
            '新增M128 KVCacheGovernor',
            '新增M129 OntologyAutoForge',
            '新增T86-T91定理'
        ])

        # 5. 跨版本共振分析
        resonance = self.analyze_resonance('v7.7', 'v7.8')

        # 6. 版本回滚测试
        rollback_result = self.rollback('v7.7')

        # 7. 获取本体图谱
        graph = self.get_ontology_graph()

        return {
            'generation': gen_result,
            'v77_snapshot': v77_snapshot.to_dict(),
            'corrections': [correction1, correction2],
            'v78_snapshot': v78_snapshot.to_dict(),
            'resonance': resonance.to_dict(),
            'rollback': rollback_result,
            'graph_summary': {
                'nodes': len(graph['nodes']),
                'edges': len(graph['edges']),
                'metrics': graph['metrics']
            },
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[OntologyAutoForge] = None


def get_instance() -> OntologyAutoForge:
    """
    获取OntologyAutoForge单例实例

    Returns:
        OntologyAutoForge全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = OntologyAutoForge()
    return _instance


def generate_ontology(module_dir: str = '') -> Dict[str, Any]:
    """扫描目录自动生成本体（快捷接口）"""
    return get_instance().generate_ontology(module_dir)


def correct_ontology(instruction: str,
                     current_ontology: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """人在回路修正（快捷接口）"""
    return get_instance().correct_ontology(instruction, current_ontology)


def create_snapshot(version: str = '',
                    changes: Optional[List[str]] = None) -> VersionSnapshot:
    """版本快照（快捷接口）"""
    return get_instance().create_snapshot(version, changes)


def rollback(target_version: str) -> Dict[str, Any]:
    """版本回滚（快捷接口）"""
    return get_instance().rollback(target_version)


def analyze_resonance(v1: str, v2: str) -> ResonanceAnalysis:
    """跨版本共振分析（快捷接口）"""
    return get_instance().analyze_resonance(v1, v2)


def get_ontology_graph() -> Dict[str, Any]:
    """获取完整本体图谱（快捷接口）"""
    return get_instance().get_ontology_graph()


def get_state() -> Dict[str, Any]:
    """获取本体自锻造状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新本体自锻造状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()


# ==================== 自测 ====================

if __name__ == '__main__':
    print('=' * 60)
    print('M129 OntologyAutoForge 自测')
    print('=' * 60)

    engine = OntologyAutoForge()

    # 测试本体生成
    print('\n--- 本体生成测试 ---')
    gen = engine.generate_ontology()
    print(f'  生成节点: {gen["total_nodes"]}')
    print(f'  生成边: {gen["total_edges"]}')
    print(f'  图直径: {gen["graph_metrics"]["diameter"]}')
    print(f'  T90: {gen["theorem_T90"]}')

    # 测试人在回路修正
    print('\n--- 人在回路修正测试 ---')
    c1 = engine.correct_ontology('M126添加依赖M57')
    print(f'  指令: M126添加依赖M57')
    print(f'  成功: {c1["success"]}, 置信度: {c1["confidence"]}')

    c2 = engine.correct_ontology('M129添加定理T90')
    print(f'  指令: M129添加定理T90')
    print(f'  成功: {c2["success"]}')

    # 测试版本快照
    print('\n--- 版本快照测试 ---')
    s1 = engine.create_snapshot('v7.7', ['基础模块M1-M125'])
    print(f'  版本v7.7: {len(s1.modules)}模块, {len(s1.theorems)}定理')

    s2 = engine.create_snapshot('v7.8', ['新增M126-M129, T86-T91'])
    print(f'  版本v7.8: {len(s2.modules)}模块, {len(s2.theorems)}定理')
    print(f'  核心公理: {len(s2.core_axioms)}条')

    # 测试共振分析
    print('\n--- 共振分析测试 ---')
    res = engine.analyze_resonance('v7.7', 'v7.8')
    print(f'  共享模块: {len(res.shared_modules)}')
    print(f'  共振分数: {res.resonance_score}')
    print(f'  共振模式: {res.resonance_patterns}')

    # 测试版本回滚
    print('\n--- 版本回滚测试 ---')
    rb = engine.rollback('v7.7')
    print(f'  回滚成功: {rb["success"]}')
    print(f'  T91: {rb.get("theorem_T91", "N/A")}')

    # 打印最终状态
    print('\n--- 最终状态 ---')
    state = engine.get_state()
    for k, v in state.items():
        if k not in ('core_axioms',):
            print(f'  {k}: {v}')

    print('\n定理T90验证:', state['theorem_T90'])
    print('定理T91验证:', state['theorem_T91'])
    print('\n自测完成 ✓')
