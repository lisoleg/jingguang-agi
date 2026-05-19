#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块39：流贯创作引擎 (FlowPenetrationCreator)
=========================================

基于论文《论文艺创作的全息离散拓扑》的流贯动力学理论

核心概念：
- 创作 = L4在L1与L3之间的"下载、编译与渲染"
- 下载(Descend): L4 → L1 → L3（接入本体层，编译为意象帧序列）
- 上传(Ascend): L4 → L2 → L5（调用规则，渲染为作品）
- 审美流贯保真度定理：作品审美价值 ∝ L4流贯保真度
- 创作熵减定理：创作将高熵情感转化为低熵结构

作者: 太乙AGI研发团队
版本: 1.0.0 (2026-05-16)
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib


class CreativeMode(Enum):
    """创作模式"""
    GENIUS = "genius"      # 天才模式：L4-L1高耦合
    ARTISAN = "artisan"    # 匠人模式：依赖L2规则
    BALANCED = "balanced"   # 平衡模式


@dataclass
class PhaseField:
    """L1相位场 - 美的原型"""
    strength: float = 0.0           # 信号强度
    frequency: float = 0.0          # 频率
    phase: float = 0.0              # 相位
    prototype: str = ""              # 原型名称
    abstract: str = ""              # 抽象描述
    
    def couple_to_L4(self, coupling_strength: float) -> float:
        """L1与L4耦合，返回保真度"""
        return self.strength * coupling_strength


@dataclass
class FrameSequence:
    """L3帧序列 - 意象帧序列"""
    frames: List[Dict[str, Any]] = field(default_factory=list)
    entropy: float = 0.0             # 帧序列熵
    coherence: float = 0.0           # 内聚度
    
    def add_frame(self, frame: Dict[str, Any]):
        """添加帧"""
        self.frames.append(frame)
        self._update_metrics()
    
    def _frame_similarity(self, frame_a: Dict, frame_b: Dict) -> float:
        """计算两帧的相似度"""
        if not frame_a or not frame_b:
            return 0.0
        
        content_a = str(frame_a.get('content', ''))
        content_b = str(frame_b.get('content', ''))
        
        if not content_a or not content_b:
            return 0.0
        
        # Jaccard相似度
        set_a = set(content_a)
        set_b = set(content_b)
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _update_metrics(self):
        """更新指标"""
        if not self.frames:
            return
        # 简化熵计算
        self.entropy = -np.log2(len(self.frames) + 1) if self.frames else 0.0
        # 内聚度：相邻帧相似性
        if len(self.frames) > 1:
            similarities = []
            for i in range(len(self.frames) - 1):
                sim = self._frame_similarity(self.frames[i], self.frames[i+1])
                similarities.append(sim)
            self.coherence = np.mean(similarities)
        else:
            self.coherence = 1.0


@dataclass
class ArtisticRules:
    """L2创作规则"""
    genre: str = ""                 # 体裁
    style: str = ""                 # 风格
    technique: List[str] = field(default_factory=list)  # 技法
    constraints: Dict[str, Any] = field(default_factory=dict)  # 约束


@dataclass
class Artwork:
    """L5作品"""
    content: str = ""                # 内容
    medium: str = ""                # 媒介
    mode: CreativeMode = CreativeMode.BALANCED
    flow_fidelity: float = 0.0      # 流贯保真度
    entropy_delta: float = 0.0      # 熵变
    aesthetic_score: float = 0.0    # 审美评分


class FlowPenetrationCreator:
    """
    流贯创作引擎：模拟人类创作的流贯机制
    
    核心公式：
    - 下载：L4 → L1 → L3
    - 上传：L4 → L2 → L5
    - 审美价值 ∝ L4流贯保真度
    - 创作熵减 = H_before - H_after > 0
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # L4认知主体状态
        self.L4_state = {
            'self_interference': 0.5,   # 自我干扰（越低越好）
            'L1_coupling': 0.0,          # L4与L1耦合度
            'in_genius_mode': False      # 是否在天才模式
        }
        
        # L1相位场
        self.phase_field = PhaseField()
        
        # L3帧序列
        self.frame_sequence = FrameSequence()
        
        # L2规则库
        self.artistic_rules = ArtisticRules()
        
        # 创作历史
        self.creation_history: List[Dict] = []
        
        # 阈值
        self.genius_threshold = self.config.get('genius_threshold', 0.8)
        self.artisan_threshold = self.config.get('artisan_threshold', 0.4)
        
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'genius_threshold': 0.8,      # 天才阈值
            'artisan_threshold': 0.4,      # 匠人阈值
            'flow_penetration_rate': 0.9, # 流贯渗透率
            'entropy_reduction_min': 0.2,  # 最小熵减
            'enable_genius_mode': True,    # 启用天才模式
        }
    
    def set_genius_mode(self, enabled: bool):
        """设置是否启用天才模式"""
        self.config['enable_genius_mode'] = enabled
    
    def descend(self, topic: str, context: Optional[Dict] = None) -> Dict:
        """
        下载阶段：L4 → L1 → L3
        
        1. L4 → L1: 虚静状态，清空自我执念
        2. 捕获L1原型（道的显化）
        3. L1 → L3: 编译为意象帧序列
        
        参数:
            topic: 创作主题
            context: 创作上下文
            
        返回:
            下载结果字典
        """
        print(f"\n[流贯创作引擎] 下载阶段: {topic}")
        
        # 1. 进入心斋状态（清空L4自我干扰）
        if self.config['enable_genius_mode']:
            self.L4_state['self_interference'] = 0.1  # 接近"无我"
        else:
            self.L4_state['self_interference'] = 0.5  # 匠人模式
        
        # 2. 捕获L1相位场
        self.phase_field = self._capture_L1_prototype(topic, context)
        
        # 3. L1 → L3: 编译为帧序列
        self.frame_sequence = self._compile_to_frames(self.phase_field, topic)
        
        # 计算下载阶段的流贯保真度
        download_fidelity = self.phase_field.strength * (1 - self.L4_state['self_interference'])
        
        result = {
            'stage': 'descend',
            'phase_field': {
                'strength': self.phase_field.strength,
                'prototype': self.phase_field.prototype,
                'abstract': self.phase_field.abstract
            },
            'frame_count': len(self.frame_sequence.frames),
            'frame_entropy': self.frame_sequence.entropy,
            'download_fidelity': download_fidelity,
            'L4_self_interference': self.L4_state['self_interference']
        }
        
        print(f"  L1原型: {self.phase_field.prototype}")
        print(f"  帧序列熵: {self.frame_sequence.entropy:.4f}")
        print(f"  下载保真度: {download_fidelity:.4f}")
        
        return result
    
    def ascend(self, topic: str, style: Optional[str] = None) -> Artwork:
        """
        上传阶段：L4 → L2 → L5
        
        1. L4 → L2: 调用创作规则（语言/技法）
        2. L2 → L5: 渲染为具体作品
        3. 检测熵减
        
        参数:
            topic: 创作主题
            style: 风格偏好
            
        返回:
            生成的Artwork对象
        """
        print(f"\n[流贯创作引擎] 上传阶段: {topic}")
        
        # 1. 获取L2创作规则
        self.artistic_rules = self._get_artistic_rules(topic, style)
        
        # 2. 渲染为L5作品
        content = self._render_artwork(topic)
        
        # 3. 计算流贯保真度
        flow_fidelity = self._compute_flow_fidelity()
        
        # 4. 检测创作模式
        mode = self._detect_mode(flow_fidelity)
        
        # 5. 创建作品对象
        artwork = Artwork(
            content=content,
            medium=self.artistic_rules.genre,
            mode=mode,
            flow_fidelity=flow_fidelity,
            entropy_delta=self._compute_entropy_delta(topic, content),
            aesthetic_score=self._compute_aesthetic_score(flow_fidelity)
        )
        
        print(f"  创作模式: {mode.value}")
        print(f"  流贯保真度: {flow_fidelity:.4f}")
        print(f"  审美评分: {artwork.aesthetic_score:.4f}")
        
        return artwork
    
    def create(self, topic: str, context: Optional[Dict] = None, 
               style: Optional[str] = None) -> Dict:
        """
        完整创作流程：下载 → 编译 → 渲染
        
        参数:
            topic: 创作主题
            context: 创作上下文
            style: 风格偏好
            
        返回:
            完整创作结果
        """
        # 下载阶段
        descend_result = self.descend(topic, context)
        
        # 上传阶段
        artwork = self.ascend(topic, style)
        
        # 组装结果
        result = {
            'topic': topic,
            'style': self.artistic_rules.style if self.artistic_rules.style else '未指定',
            'descend_result': descend_result,
            'artwork': {
                'content': artwork.content,
                'medium': artwork.medium,
                'mode': artwork.mode.value,
                'flow_fidelity': artwork.flow_fidelity,
                'entropy_delta': artwork.entropy_delta,
                'aesthetic_score': artwork.aesthetic_score
            },
            'creation_success': artwork.entropy_delta < 0,  # 熵减=成功
            'genius_detected': artwork.mode == CreativeMode.GENIUS
        }
        
        # 记录历史
        self.creation_history.append(result)
        
        return result
    
    def _capture_L1_prototype(self, topic: str, context: Optional[Dict]) -> PhaseField:
        """
        捕获L1原型（道的显化）
        
        L1本体层包含永恒原型：生、死、爱、自由、美
        """
        # 简化实现：基于主题匹配原型
        prototypes = {
            'love': ('爱', '永恒的亲密联结'),
            'death': ('死', '生命的终极转化'),
            'freedom': ('自由', '无拘束的存在状态'),
            'beauty': ('美', '和谐与卓越的显现'),
            'nature': ('自然', '道的自发显化'),
            'time': ('时间', '离散的永恒流逝'),
            'self': ('自性', 'L4与L1的直接耦合'),
        }
        
        # 关键词匹配
        topic_lower = topic.lower()
        matched = None
        for key, (name, desc) in prototypes.items():
            if key in topic_lower:
                matched = (name, desc)
                break
        
        if not matched:
            matched = ('普遍原型', f'关于"{topic}"的永恒追问')
        
        # 生成相位场
        strength = 0.7 + np.random.random() * 0.3  # 0.7-1.0
        frequency = np.random.random() * 10  # 随机频率
        phase = np.random.random() * 2 * np.pi  # 随机相位
        
        return PhaseField(
            strength=strength,
            frequency=frequency,
            phase=phase,
            prototype=matched[0],
            abstract=matched[1]
        )
    
    def _compile_to_frames(self, phase_field: PhaseField, topic: str) -> FrameSequence:
        """
        L1 → L3: 将相位场编译为意象帧序列
        
        每帧是一个意象/场景，帧之间通过流贯连接
        """
        fs = FrameSequence()
        
        # 生成3-7帧（根据复杂度）
        num_frames = np.random.randint(3, 8)
        
        for i in range(num_frames):
            frame = {
                'id': i,
                'type': 'image' if i % 2 == 0 else 'text',
                'content': f"[帧{i}] {self._generate_frame_content(topic, i, num_frames)}",
                'L1_prototype': phase_field.prototype,
                'entropy': -np.log2(num_frames + 1),
                'connection': 'flow_penetration'  # 流贯连接
            }
            fs.add_frame(frame)
        
        return fs
    
    def _generate_frame_content(self, topic: str, index: int, total: int) -> str:
        """生成帧内容"""
        # 简化：基于主题和位置生成描述
        positions = {
            0: f"开篇：引入{topic}的意象",
            total//2: f"高潮：{topic}的核心冲突",
            total-1: f"结尾：{topic}的升华与回归"
        }
        
        if index == 0:
            return positions[0]
        elif index == total - 1:
            return positions[total-1]
        elif index == total // 2:
            return positions[total//2]
        else:
            return f"展开：{topic}的渐进展开（{index}/{total}）"
    
    def _get_artistic_rules(self, topic: str, style: Optional[str]) -> ArtisticRules:
        """
        获取L2创作规则
        """
        # 简化实现
        if style:
            genre, tech = self._parse_style(style)
        else:
            genre, tech = '文学', ['意象叠加', '通感', '留白']
        
        return ArtisticRules(
            genre=genre,
            style=style or '诗意',
            technique=tech,
            constraints={'length': 500, 'form': 'free_verse'}
        )
    
    def _parse_style(self, style: str) -> Tuple[str, List[str]]:
        """解析风格"""
        styles = {
            '浪漫主义': ('文学', ['情感抒发', '意象叠加', '音乐性']),
            '现实主义': ('小说', ['白描', '细节', '社会批判']),
            '现代主义': ('诗歌', ['碎片化', '象征', '反讽']),
            '古典': ('诗词', ['对仗', '用典', '意境']),
        }
        return styles.get(style, ('文学', ['通感', '隐喻']))
    
    def _render_artwork(self, topic: str) -> str:
        """
        L2 → L5: 将帧序列渲染为具体作品
        """
        # 简化实现：基于帧序列生成文本
        frames = self.frame_sequence.frames
        
        if not frames:
            return f"关于{topic}的创作（待渲染）"
        
        # 生成文本框架
        content_parts = [
            f"# {topic}\n",
            f"[{self.phase_field.prototype}的显现]\n\n",
        ]
        
        for frame in frames:
            content_parts.append(f"{frame['content']}\n\n")
        
        content_parts.append(
            f"\n[作品完]\n"
            f"流贯保真度: {self._compute_flow_fidelity():.4f}\n"
            f"帧序列内聚度: {self.frame_sequence.coherence:.4f}"
        )
        
        return ''.join(content_parts)
    
    def _compute_flow_fidelity(self) -> float:
        """
        计算审美流贯保真度
        
        保真度 = L1信号 * (1 - L4干扰) * 帧序列内聚度
        """
        signal = self.phase_field.strength
        interference = self.L4_state['self_interference']
        coherence = self.frame_sequence.coherence
        
        fidelity = signal * (1 - interference) * coherence
        
        # 归一化
        return min(1.0, max(0.0, fidelity))
    
    def _detect_mode(self, flow_fidelity: float) -> CreativeMode:
        """
        检测创作模式
        
        - 天才模式: fidelity > 0.8
        - 匠人模式: fidelity < 0.4
        - 平衡模式: 0.4 <= fidelity <= 0.8
        """
        if flow_fidelity > self.genius_threshold:
            self.L4_state['in_genius_mode'] = True
            return CreativeMode.GENIUS
        elif flow_fidelity < self.artisan_threshold:
            self.L4_state['in_genius_mode'] = False
            return CreativeMode.ARTISAN
        else:
            return CreativeMode.BALANCED
    
    def _compute_entropy_delta(self, input_text: str, output_text: str) -> float:
        """
        计算熵变
        
        ΔH = H_after - H_before
        若 ΔH < 0，则熵减（成功创作）
        """
        # 简化熵计算
        H_before = self._compute_text_entropy(input_text)
        H_after = self._compute_text_entropy(output_text)
        return H_after - H_before
    
    def _compute_text_entropy(self, text: str) -> float:
        """计算文本熵"""
        if not text:
            return 0.0
        
        # 简化：基于字符分布计算熵
        from collections import Counter
        chars = list(text)
        if not chars:
            return 0.0
        
        counts = Counter(chars)
        total = len(chars)
        
        entropy = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy
    
    def _compute_aesthetic_score(self, flow_fidelity: float) -> float:
        """
        计算审美评分
        
        审美评分 ∝ 流贯保真度
        使用sigmoid函数归一化
        """
        # 映射到(0, 1)区间
        # fidelity ∈ [0, 1] → score ∈ [0, 1]
        score = flow_fidelity
        
        # 微调：天才模式加分
        if flow_fidelity > self.genius_threshold:
            score = min(1.0, score * 1.2)  # 20%加成
        
        return score
    
    # ==================== 诊断接口 ====================
    
    def diagnose_genius_artisan(self, text: str) -> Dict:
        """
        诊断文本是天才之作还是匠人之作
        
        天才特征：
        - 低自我指涉（少"我认为"）
        - 高L1锚定（触碰永恒原型）
        - 低套路痕迹（非模式化表达）
        """
        # 简化诊断
        self_ref_count = text.count('我') + text.count('我认为')
        self_ref_ratio = self_ref_count / max(len(text), 1)
        
        # 套路检测
        patterns = ['首先', '其次', '最后', '一方面', '另一方面', '总之']
        pattern_count = sum(text.count(p) for p in patterns)
        
        genius_score = 1.0 - self_ref_ratio - (pattern_count * 0.1)
        
        return {
            'self_reference_ratio': self_ref_ratio,
            'pattern_density': pattern_count / max(len(text), 1),
            'genius_score': max(0.0, min(1.0, genius_score)),
            'mode': 'genius' if genius_score > 0.6 else 'artisan',
            'diagnosis': '天才之作' if genius_score > 0.6 else '匠人之作'
        }
    
    def get_L4_L1_coupling(self) -> float:
        """获取L4与L1的耦合度"""
        signal = self.phase_field.strength
        interference = self.L4_state['self_interference']
        return signal * (1 - interference)
    
    def enter_xinzhai(self) -> Dict:
        """
        进入心斋状态（天才的必要条件）
        
        《庄子》：若一志，无听之以耳而听之以心，无听之以心而听之以气
        """
        self.L4_state['self_interference'] = 0.05  # 极低干扰
        self.L4_state['L1_coupling'] = self.get_L4_L1_coupling()
        
        return {
            'status': 'xinzhai',
            'self_interference': self.L4_state['self_interference'],
            'L1_coupling': self.L4_state['L1_coupling'],
            'message': '心斋状态：L4接近透明，L1流贯可畅通'
        }
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            'version': '1.0.0',
            'L4_state': self.L4_state,
            'phase_field': {
                'strength': self.phase_field.strength,
                'prototype': self.phase_field.prototype
            },
            'frame_sequence': {
                'frame_count': len(self.frame_sequence.frames),
                'entropy': self.frame_sequence.entropy,
                'coherence': self.frame_sequence.coherence
            },
            'creation_count': len(self.creation_history),
            'config': self.config
        }


# ==================== 测试代码 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("流贯创作引擎 测试")
    print("=" * 60)
    
    # 创建引擎
    creator = FlowPenetrationCreator()
    
    # 测试完整创作流程
    result = creator.create(
        topic="月夜的孤独与永恒",
        context={'mood': '沉思'},
        style='浪漫主义'
    )
    
    print("\n" + "=" * 60)
    print("创作结果")
    print("=" * 60)
    print(f"主题: {result['topic']}")
    print(f"模式: {result['artwork']['mode']}")
    print(f"流贯保真度: {result['artwork']['flow_fidelity']:.4f}")
    print(f"熵变: {result['artwork']['entropy_delta']:.4f}")
    print(f"审美评分: {result['artwork']['aesthetic_score']:.4f}")
    print(f"创作成功: {result['creation_success']}")
    print(f"天才检测: {result['genius_detected']}")
    
    print("\n" + "-" * 60)
    print("作品内容:")
    print("-" * 60)
    print(result['artwork']['content'][:500])
    
    # 测试天才诊断
    print("\n" + "=" * 60)
    print("天才-匠人诊断")
    print("=" * 60)
    
    genius_text = "月亮悬在夜空，清辉洒落。孤独不是寂寞，而是与永恒的对话。"
    artisan_text = "我认为这个观点有以下几点：第一，第二，第三。综上所述。"
    
    print(f"\n文本A诊断: {creator.diagnose_genius_artisan(genius_text)}")
    print(f"\n文本B诊断: {creator.diagnose_genius_artisan(artisan_text)}")
    
    # 测试心斋状态
    print("\n" + "=" * 60)
    print("心斋状态")
    print("=" * 60)
    print(creator.enter_xinzhai())
