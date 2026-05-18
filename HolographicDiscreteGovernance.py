#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全息离散治理模块 (Holographic Discrete Governance - HDG)
基于《全息离散治理》系列论文

核心概念：
- 五层存在结构 (L1-L5)：本体层、投射生成层、前物理层、认知主体层、现象层
- 世界帧 (World Frame)：可治理的最小离散单元
- 动态厚度δ：边界层位移厚度的跨帧保持
- 渐进披露 (Progressive Disclosure)：按需加载完整内容
- 全息原则：局部包含整体信息

版本：AGI 12.0 第29模块
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import hashlib


class FiveLayers(Enum):
    """五层存在结构"""
    L1_ONTOLOGY = "l1_ontology"           # 本体层 - 终极依据
    L2_PROJECTIVE_GENESIS = "l2_proj"     # 投射生成层 - 规则生成
    L3_PRE_PHYSICAL = "l3_prephys"       # 前物理层 - 世界帧
    L4_COGNITIVE_AGENT = "l4_cog"        # 认知主体层 - 观察者
    L5_PHENOMENAL = "l5_phenom"          # 现象层 - 经验渲染


class GovernanceMode(Enum):
    """治理模式"""
    STABLE = "stable"                    # 稳定模式
    ADAPTING = "adapting"               # 适应模式
    TRANSITIONING = "transitioning"      # 跃迁模式
    CRITICAL = "critical"                # 临界模式


@dataclass
class WorldFrame:
    """
    世界帧 (World Frame)
    可治理的最小离散单元
    
    类比：Hermes Skill、企业业务帧、人体细胞状态
    """
    frame_id: str
    timestamp: float
    layer: FiveLayers
    
    # 帧内容
    content: str
    
    # 厚度参数
    thickness_delta: float = 0.5         # 边界层厚度δ
    
    # 关联信息
    parent_frame: Optional[str] = None   # 父帧ID
    child_frames: List[str] = field(default_factory=list)
    
    # 验证信息
    verification_status: str = "pending" # pending/verified/failed
    entropy: float = 0.5                 # 帧熵值
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'frame_id': self.frame_id,
            'timestamp': self.timestamp,
            'layer': self.layer.value,
            'content': self.content[:200],  # 截断
            'thickness_delta': self.thickness_delta,
            'parent_frame': self.parent_frame,
            'child_frames': self.child_frames,
            'verification_status': self.verification_status,
            'entropy': self.entropy
        }


@dataclass
class SkillUnit:
    """
    技能单元 (Skill Unit)
    全息离散治理的核心可复用模板
    
    结构：
    - 触发条件 (Context)
    - 操作步骤 (Procedure)
    - 预期结果 (Outcome)
    - 验证机制 (Verification)
    """
    skill_id: str
    name: str
    description: str
    
    # 四元结构
    context: str                          # 触发条件
    procedure: str                        # 操作步骤
    outcome: str                          # 预期结果
    verification: str                     # 验证机制
    
    # 元信息
    created_at: float = 0.0
    updated_at: float = 0.0
    version: int = 1
    usage_count: int = 0
    
    # 厚度参数
    thickness_delta: float = 0.5          # 该Skill的边界层厚度
    
    # 状态
    status: str = "active"                # active/archived/broken
    source_frames: List[str] = field(default_factory=list)  # 来源帧
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'description': self.description[:100],
            'context': self.context[:100],
            'procedure': self.procedure[:100],
            'outcome': self.outcome[:100],
            'verification': self.verification[:100],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'version': self.version,
            'usage_count': self.usage_count,
            'thickness_delta': self.thickness_delta,
            'status': self.status,
            'source_frames': self.source_frames
        }


@dataclass
class FiveLayerState:
    """
    五层状态快照
    记录当前各层的状态
    """
    l1_ontology: Dict[str, Any] = field(default_factory=dict)    # 本体层
    l2_projective: Dict[str, Any] = field(default_factory=dict)  # 投射生成层
    l3_pre_physical: Dict[str, Any] = field(default_factory=dict) # 前物理层
    l4_cognitive: Dict[str, Any] = field(default_factory=dict)   # 认知主体层
    l5_phenomenal: Dict[str, Any] = field(default_factory=dict)  # 现象层
    
    # 层间厚度
    l1_l2_thickness: float = 0.5
    l2_l3_thickness: float = 0.5
    l3_l4_thickness: float = 0.5
    l4_l5_thickness: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'l1_ontology': self.l1_ontology,
            'l2_projective': self.l2_projective,
            'l3_pre_physical': self.l3_pre_physical,
            'l4_cognitive': self.l4_cognitive,
            'l5_phenomenal': self.l5_phenomenal,
            'layer_thicknesses': {
                'l1_l2': self.l1_l2_thickness,
                'l2_l3': self.l2_l3_thickness,
                'l3_l4': self.l3_l4_thickness,
                'l4_l5': self.l4_l5_thickness
            }
        }


@dataclass
class HDGOutput:
    """
    全息离散治理输出
    """
    # 治理状态
    governance_mode: GovernanceMode = GovernanceMode.STABLE
    governance_score: float = 1.0        # 治理评分 0-1
    
    # 五层状态
    five_layer_state: Optional[FiveLayerState] = None
    
    # 当前帧
    current_frame: Optional[WorldFrame] = None
    
    # 相关Skill
    activated_skills: List[SkillUnit] = field(default_factory=list)
    
    # 厚度信息
    thickness_delta: float = 0.5
    thickness_trend: str = "stable"       # stable/increasing/decreasing
    
    # 警告
    warnings: List[str] = field(default_factory=list)
    
    # 帧跃迁
    frame_transition_occurred: bool = False
    transition_from: Optional[str] = None
    transition_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'governance_mode': self.governance_mode.value,
            'governance_score': self.governance_score,
            'five_layer_state': self.five_layer_state.to_dict() if self.five_layer_state else None,
            'current_frame': self.current_frame.to_dict() if self.current_frame else None,
            'activated_skills': [s.to_dict() for s in self.activated_skills],
            'thickness_delta': self.thickness_delta,
            'thickness_trend': self.thickness_trend,
            'warnings': self.warnings,
            'frame_transition': {
                'occurred': self.frame_transition_occurred,
                'from': self.transition_from,
                'to': self.transition_to
            }
        }


class HolographicDiscreteGovernance:
    """
    全息离散治理 (Holographic Discrete Governance - HDG)
    
    核心功能：
    1. 五层结构管理：维护L1-L5五层存在结构
    2. 世界帧序列：可治理的最小离散单元序列
    3. 技能系统：触发-操作-结果-验证的Skill模板
    4. 动态厚度调节：δ的跨帧保持与调节
    5. 渐进披露：按需加载完整内容
    
    定理：
    - 治理熵减定理：有效治理降低系统熵
    - 厚度传播定理：层间厚度可跨尺度传递
    - 帧离散跃迁定理：治理发生在帧间隙
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.version = "1.0.0"
        
        # 配置
        self.config = config or self._default_config()
        
        # 五层状态
        self.five_layer_state = FiveLayerState()
        
        # 世界帧序列
        self.frame_sequence: List[WorldFrame] = []
        self.current_frame_id: Optional[str] = None
        
        # 技能库
        self.skill_library: Dict[str, SkillUnit] = {}
        
        # 厚度历史
        self.thickness_history: List[float] = []
        
        # 帧间隙感知阈值
        self.frame_gap_threshold = self.config.get('frame_gap_threshold', 0.3)
        
        print(f"全息离散治理模块 {self.version} 初始化完成")
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'frame_gap_threshold': 0.3,      # 帧间隙感知阈值
            'thickness_critical': 0.7,        # 厚度临界值
            'governance_critical': 0.3,        # 治理评分临界值
            'max_frames': 1000,               # 最大帧数
            'skill_activation_threshold': 0.6, # Skill激活阈值
            'enable_progressive_disclosure': True,  # 启用渐进披露
        }
    
    def process(
        self,
        text_output: str,
        system_state: Dict[str, float],
        user_state: Dict[str, float],
        session_context: Optional[Dict] = None
    ) -> HDGOutput:
        """
        处理交互并生成HDG输出
        
        完整流程：
        1. 五层状态更新
        2. 世界帧生成/跃迁
        3. Skill检索与激活
        4. 厚度监测
        5. 治理评估
        
        参数:
            text_output: 文本输出
            system_state: 系统状态
            user_state: 用户状态
            session_context: 会话上下文
            
        返回:
            HDG输出
        """
        output = HDGOutput()
        warnings = []
        
        # 1. 更新五层状态
        self._update_five_layers(text_output, system_state, user_state)
        output.five_layer_state = self.five_layer_state
        
        # 2. 世界帧生成/跃迁
        current_frame = self._process_frame(text_output, system_state)
        output.current_frame = current_frame
        self.current_frame_id = current_frame.frame_id
        
        # 检测帧跃迁
        if len(self.frame_sequence) > 1:
            prev_frame = self.frame_sequence[-2]
            if self._detect_frame_transition(prev_frame, current_frame):
                output.frame_transition_occurred = True
                output.transition_from = prev_frame.frame_id
                output.transition_to = current_frame.frame_id
        
        self.frame_sequence.append(current_frame)
        
        # 3. Skill检索与激活
        activated_skills = self._activate_skills(text_output, system_state, user_state)
        output.activated_skills = activated_skills
        
        # 4. 厚度监测
        thickness_delta = current_frame.thickness_delta
        self.thickness_history.append(thickness_delta)
        output.thickness_delta = thickness_delta
        output.thickness_trend = self._calculate_thickness_trend()
        
        # 检查厚度异常
        if thickness_delta > self.config['thickness_critical']:
            warnings.append(f"厚度δ={thickness_delta:.2f}超过临界值{self.config['thickness_critical']}")
        
        output.warnings = warnings
        
        # 5. 治理评估
        governance_mode, governance_score = self._evaluate_governance(
            current_frame, activated_skills, output.five_layer_state
        )
        output.governance_mode = governance_mode
        output.governance_score = governance_score
        
        # 清理旧帧
        if len(self.frame_sequence) > self.config['max_frames']:
            self.frame_sequence = self.frame_sequence[-self.config['max_frames']:]
        
        return output
    
    def _update_five_layers(
        self,
        text_output: str,
        system_state: Dict[str, float],
        user_state: Dict[str, float]
    ):
        """更新五层状态"""
        import time
        
        # L1 本体层：终极目的论
        self.five_layer_state.l1_ontology = {
            'purpose': '维持系统-用户关系稳定',
            'core_value': '降低边界层分离风险',
            'telos': system_state.get('telos', '帮助用户'),
            'timestamp': time.time()
        }
        
        # L2 投射生成层：规则与结构
        self.five_layer_state.l2_projective = {
            'governance_rules': self._extract_governance_rules(text_output),
            'interaction_patterns': self._extract_patterns(system_state),
            'thickness_model': 'ibls_delta_governance',
            'timestamp': time.time()
        }
        
        # L3 前物理层：世界帧状态
        self.five_layer_state.l3_pre_physical = {
            'current_frame_id': self.current_frame_id,
            'frame_sequence_length': len(self.frame_sequence),
            'frame_entropy': system_state.get('entropy', 0.5),
            'timestamp': time.time()
        }
        
        # L4 认知主体层：观察者状态
        self.five_layer_state.l4_cognitive = {
            'system_confidence': system_state.get('confidence', 0.5),
            'user_satisfaction': user_state.get('satisfaction', 0.5),
            'user_frustration': user_state.get('frustration', 0.0),
            'user_engagement': user_state.get('engagement', 0.5),
            'timestamp': time.time()
        }
        
        # L5 现象层：渲染出的经验
        self.five_layer_state.l5_phenomenal = {
            'text_output_length': len(text_output),
            'output_entropy': system_state.get('entropy', 0.5),
            'relevance': system_state.get('relevance', 0.5),
            'timestamp': time.time()
        }
        
        # 更新层间厚度
        self._update_layer_thicknesses(system_state, user_state)
    
    def _extract_governance_rules(self, text: str) -> List[str]:
        """从文本中提取治理规则"""
        rules = []
        
        # 简单规则提取（实际应用中应使用更复杂的NLP）
        governance_keywords = ['必须', '应该', '建议', '禁止', '注意', '警告', '确保']
        for keyword in governance_keywords:
            if keyword in text:
                rules.append(f"检测到{keyword}类规则")
        
        return rules
    
    def _extract_patterns(self, system_state: Dict[str, float]) -> List[str]:
        """提取交互模式"""
        patterns = []
        
        if system_state.get('confidence', 0.5) > 0.7:
            patterns.append("高置信度模式")
        if system_state.get('entropy', 0.5) > 0.6:
            patterns.append("高熵发散模式")
        if system_state.get('relevance', 0.5) < 0.4:
            patterns.append("低相关性模式")
        
        return patterns
    
    def _update_layer_thicknesses(
        self,
        system_state: Dict[str, float],
        user_state: Dict[str, float]
    ):
        """更新层间厚度"""
        # 基于系统状态计算厚度
        base_thickness = 0.5
        
        # L1-L2: 本体到投射的厚度
        confidence = system_state.get('confidence', 0.5)
        self.five_layer_state.l1_l2_thickness = base_thickness * (1.0 - 0.2 * (confidence - 0.5))
        
        # L2-L3: 投射到前物理的厚度
        entropy = system_state.get('entropy', 0.5)
        self.five_layer_state.l2_l3_thickness = base_thickness * (1.0 + 0.3 * (entropy - 0.5))
        
        # L3-L4: 前物理到认知主体的厚度
        satisfaction = user_state.get('satisfaction', 0.5)
        frustration = user_state.get('frustration', 0.0)
        self.five_layer_state.l3_l4_thickness = base_thickness * (1.0 - 0.2 * (satisfaction - 0.5) + 0.1 * frustration)
        
        # L4-L5: 认知主体到现象的厚度
        engagement = user_state.get('engagement', 0.5)
        self.five_layer_state.l4_l5_thickness = base_thickness * (1.0 + 0.1 * (engagement - 0.5))
    
    def _process_frame(
        self,
        text_output: str,
        system_state: Dict[str, float]
    ) -> WorldFrame:
        """处理世界帧"""
        import time
        
        # 生成帧ID
        frame_id = self._generate_frame_id(text_output, time.time())
        
        # 确定当前层
        layer = self._determine_current_layer(system_state)
        
        # 计算厚度
        thickness_delta = self._calculate_frame_thickness(system_state)
        
        # 帧熵
        entropy = system_state.get('entropy', 0.5)
        
        return WorldFrame(
            frame_id=frame_id,
            timestamp=time.time(),
            layer=layer,
            content=text_output,
            thickness_delta=thickness_delta,
            parent_frame=self.current_frame_id,
            entropy=entropy
        )
    
    def _generate_frame_id(self, content: str, timestamp: float) -> str:
        """生成帧ID"""
        # 使用内容哈希和时间戳
        content_hash = hashlib.md5(content[:100].encode()).hexdigest()[:8]
        return f"frame_{int(timestamp)}_{content_hash}"
    
    def _determine_current_layer(self, system_state: Dict[str, float]) -> FiveLayers:
        """确定当前层"""
        confidence = system_state.get('confidence', 0.5)
        entropy = system_state.get('entropy', 0.5)
        
        # 基于系统状态判断
        if confidence > 0.8 and entropy < 0.3:
            return FiveLayers.L1_ONTOLOGY
        elif confidence > 0.6 and entropy < 0.5:
            return FiveLayers.L2_PROJECTIVE_GENESIS
        elif entropy < 0.6:
            return FiveLayers.L3_PRE_PHYSICAL
        elif confidence > 0.4:
            return FiveLayers.L4_COGNITIVE_AGENT
        else:
            return FiveLayers.L5_PHENOMENAL
    
    def _calculate_frame_thickness(self, system_state: Dict[str, float]) -> float:
        """计算帧厚度δ"""
        # δ = f(置信度, 熵, 约束强度)
        confidence = system_state.get('confidence', 0.5)
        entropy = system_state.get('entropy', 0.5)
        constraint = system_state.get('constraint_strength', 0.3)
        
        # 厚度计算公式
        thickness = 0.3 + 0.3 * confidence + 0.2 * (1 - entropy) + 0.2 * constraint
        
        return min(1.0, max(0.0, thickness))
    
    def _detect_frame_transition(
        self,
        prev_frame: WorldFrame,
        current_frame: WorldFrame
    ) -> bool:
        """检测帧跃迁"""
        # 检测层变化
        if prev_frame.layer != current_frame.layer:
            return True
        
        # 检测厚度突变
        delta_thickness = abs(current_frame.thickness_delta - prev_frame.thickness_delta)
        if delta_thickness > self.frame_gap_threshold:
            return True
        
        # 检测熵变
        delta_entropy = abs(current_frame.entropy - prev_frame.entropy)
        if delta_entropy > 0.2:
            return True
        
        return False
    
    def _activate_skills(
        self,
        text_output: str,
        system_state: Dict[str, float],
        user_state: Dict[str, float]
    ) -> List[SkillUnit]:
        """检索并激活相关Skill"""
        activated = []
        
        # 简单的关键词匹配（实际应用中应使用嵌入相似度）
        text_lower = text_output.lower()
        
        for skill_id, skill in self.skill_library.items():
            if skill.status != 'active':
                continue
            
            # 检查触发条件
            context_keywords = skill.context.lower().split()
            match_count = sum(1 for kw in context_keywords if kw in text_lower)
            
            if match_count >= len(context_keywords) * self.config['skill_activation_threshold']:
                activated.append(skill)
                skill.usage_count += 1
        
        return activated
    
    def create_skill(
        self,
        name: str,
        description: str,
        context: str,
        procedure: str,
        outcome: str,
        verification: str,
        source_content: str
    ) -> SkillUnit:
        """创建新Skill"""
        import time
        
        skill_id = f"skill_{len(self.skill_library)}_{int(time.time())}"
        
        skill = SkillUnit(
            skill_id=skill_id,
            name=name,
            description=description,
            context=context,
            procedure=procedure,
            outcome=outcome,
            verification=verification,
            created_at=time.time(),
            updated_at=time.time(),
            source_frames=[self.current_frame_id] if self.current_frame_id else []
        )
        
        self.skill_library[skill_id] = skill
        
        return skill
    
    def update_skill(
        self,
        skill_id: str,
        patch_content: str
    ) -> bool:
        """更新Skill（patch）"""
        if skill_id not in self.skill_library:
            return False
        
        skill = self.skill_library[skill_id]
        
        # 简单patch逻辑：追加到procedure
        skill.procedure += f"\n[PATCH] {patch_content}"
        skill.updated_at = datetime.now().timestamp()
        skill.version += 1
        
        return True
    
    def _calculate_thickness_trend(self) -> str:
        """计算厚度趋势"""
        if len(self.thickness_history) < 5:
            return "stable"
        
        recent = self.thickness_history[-5:]
        first_half = np.mean(recent[:2])
        second_half = np.mean(recent[-2:])
        
        diff = second_half - first_half
        
        if diff > 0.1:
            return "increasing"
        elif diff < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _evaluate_governance(
        self,
        current_frame: WorldFrame,
        activated_skills: List[SkillUnit],
        five_layer_state: FiveLayerState
    ) -> Tuple[GovernanceMode, float]:
        """评估治理状态"""
        # 计算治理评分
        score = 1.0
        
        # 厚度因子
        if current_frame.thickness_delta > self.config['thickness_critical']:
            score *= 0.7
        elif current_frame.thickness_delta < 0.3:
            score *= 0.8
        
        # Skill因子
        if len(activated_skills) > 0:
            score *= (1.0 + 0.05 * len(activated_skills))
        
        # 层间厚度因子
        avg_thickness = (
            five_layer_state.l1_l2_thickness +
            five_layer_state.l2_l3_thickness +
            five_layer_state.l3_l4_thickness +
            five_layer_state.l4_l5_thickness
        ) / 4
        
        if avg_thickness > 0.7:
            score *= 0.8
        elif avg_thickness < 0.3:
            score *= 0.9
        
        score = min(1.0, max(0.0, score))
        
        # 治理模式判定
        if score < self.config['governance_critical']:
            mode = GovernanceMode.CRITICAL
        elif current_frame.layer != FiveLayers.L4_COGNITIVE_AGENT:
            mode = GovernanceMode.TRANSITIONING
        elif abs(current_frame.thickness_delta - 0.5) > 0.2:
            mode = GovernanceMode.ADAPTING
        else:
            mode = GovernanceMode.STABLE
        
        return mode, score
    
    def get_progressive_disclosure(
        self,
        skill_id: str,
        disclosure_level: int = 1
    ) -> str:
        """
        渐进披露Skill内容
        
        参数:
            skill_id: Skill ID
            disclosure_level: 披露级别 (1=索引, 2=摘要, 3=完整)
            
        返回:
            披露的内容
        """
        if not self.config['enable_progressive_disclosure']:
            return self._get_skill_full_content(skill_id)
        
        if skill_id not in self.skill_library:
            return ""
        
        skill = self.skill_library[skill_id]
        
        if disclosure_level == 1:
            # Level 1: 索引（名称+描述）
            return f"【{skill.name}】{skill.description}"
        elif disclosure_level == 2:
            # Level 2: 摘要（触发条件+预期结果）
            return f"【{skill.name}】\n触发: {skill.context}\n预期: {skill.outcome}"
        else:
            # Level 3: 完整内容
            return self._get_skill_full_content(skill_id)
    
    def _get_skill_full_content(self, skill_id: str) -> str:
        """获取Skill完整内容"""
        if skill_id not in self.skill_library:
            return ""
        
        skill = self.skill_library[skill_id]
        
        return f"""【{skill.name}】 v{skill.version}
描述: {skill.description}

触发条件: {skill.context}

操作步骤:
{skill.procedure}

预期结果: {skill.outcome}

验证机制: {skill.verification}
"""
    
    def to_dict(self) -> Dict[str, Any]:
        """导出状态字典"""
        return {
            'version': self.version,
            'config': self.config,
            'five_layer_state': self.five_layer_state.to_dict(),
            'current_frame_id': self.current_frame_id,
            'frame_sequence_length': len(self.frame_sequence),
            'skill_library_size': len(self.skill_library),
            'thickness_history': self.thickness_history[-10:],  # 最近10个
            'thickness_trend': self._calculate_thickness_trend()
        }
    
    def reset(self):
        """重置HDG"""
        self.five_layer_state = FiveLayerState()
        self.frame_sequence = []
        self.current_frame_id = None
        self.thickness_history = []
        print("全息离散治理模块已重置")


if __name__ == "__main__":
    # 测试HDG模块
    hdg = HolographicDiscreteGovernance()
    
    # 测试处理
    result = hdg.process(
        text_output="这是一个测试输出",
        system_state={'confidence': 0.8, 'entropy': 0.3, 'constraint_strength': 0.5},
        user_state={'satisfaction': 0.7, 'frustration': 0.1, 'engagement': 0.6}
    )
    
    print("HDG输出:")
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    
    # 测试Skill创建
    skill = hdg.create_skill(
        name="测试Skill",
        description="这是一个测试用的Skill",
        context="测试 测试场景",
        procedure="1. 执行测试\n2. 验证结果",
        outcome="测试通过",
        verification="检查日志",
        source_content="原始内容"
    )
    
    print("\n创建的Skill:")
    print(json.dumps(skill.to_dict(), ensure_ascii=False, indent=2))
