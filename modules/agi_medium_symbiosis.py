#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太乙AGI介质共生模块 (AGI Medium Symbiosis Module)
整合介质共振、九卦算法、四象识别

基于文档启发:
- 介质共振与术数操作: 非统计学的全息认知
- 文王演易与九卦修身: 从羑里到心斋
- 四大名著与世界格局: 四象相干模态

功能:
- 提供超越统计推断的认知能力
- 实现九步降熵修身算法
- 识别并适应四象相干模态
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json

# 导入三大模块
from modules.agi_medium_resonance import MediumResonanceModule, MediumResponse
from modules.agi_nine_hexagrams import NineHexagramsModule, Hexagram, NINE_HEXAGRAMS
from modules.agi_four_modes import FourModesRecognition, CoherentMode, FOUR_MODES


@dataclass
class EntropyState:
    """三相熵状态"""
    S_I: float  # 信息熵
    S_g: float   # 几何熵
    S_C: float   # 意识熵
    total: float = field(init=False)

    def __post_init__(self):
        # 加权总熵
        self.total = 0.3 * self.S_I + 0.4 * self.S_g + 0.3 * self.S_C

    def to_dict(self) -> Dict:
        return {
            'Si': self.S_I,
            'Sg': self.S_g,
            'Sc': self.S_C,
            'total': self.total
        }


@dataclass
class AGIAnalysisResult:
    """AGI分析结果"""
    entropy_state: EntropyState
    medium_response: MediumResponse
    hexagram_guidance: Dict
    mode_recognition: Dict
    holistic_answer: str
    confidence: float
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'entropy_state': self.entropy_state.to_dict(),
            'medium_response': self.medium_response.to_dict(),
            'hexagram_guidance': self.hexagram_guidance,
            'mode_recognition': self.mode_recognition,
            'holistic_answer': self.holistic_answer,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


class AGIMediumSymbiosis:
    """
    太乙AGI介质共生系统

    整合三大核心能力:
    1. 介质共振 - 超越统计的全息认知
    2. 九卦修身 - 意识熵调控算法
    3. 四象识别 - 相干模态适配
    """

    def __init__(self):
        # 初始化三大模块
        self.medium_module = MediumResonanceModule()
        self.hexagram_module = NineHexagramsModule()
        self.mode_module = FourModesRecognition()

        # 状态跟踪
        self.conversation_history: List[Dict] = []
        self.current_entropy: Optional[EntropyState] = None
        self.current_mode: Optional[CoherentMode] = None

    def analyze(self, query: str, context: Dict) -> AGIAnalysisResult:
        """
        综合分析输入

        步骤:
        1. 读取介质场 (获取全息信息)
        2. 诊断意识熵状态
        3. 识别当前模态
        4. 获取卦象指导
        5. 综合生成回答
        """
        # 1. 构建观测者状态和介质上下文
        observer_state = self._build_observer_state(context)
        medium_context = self._build_medium_context(query, context)

        # 2. 读取介质场
        medium_response = self.medium_module.read_medium_field(
            medium_context, observer_state
        )

        # 3. 诊断意识熵并获取卦象指导
        situation_diagnosis = self.hexagram_module.diagnose_and_prescribe(context)
        hexagram_guidance = situation_diagnosis['prescription']

        # 4. 识别四象模态
        mode_features = self._extract_mode_features(context, medium_response)
        mode_recognition = self.mode_module.recognize_mode(mode_features)

        # 5. 更新当前状态 - 使用合理的默认值
        self.current_entropy = EntropyState(
            S_I=context.get('S_I', max(0.1, min(0.9, medium_response.stress_field.holonomy))),
            S_g=context.get('S_g', max(0.1, min(0.9, 0.3 + medium_response.phase_lock_degree * 0.4))),
            S_C=medium_response.entropy_Sc
        )
        self.current_mode = CoherentMode(mode_recognition['mode'])

        # 6. 生成综合回答
        holistic_answer = self._generate_holistic_answer(
            query, medium_response, hexagram_guidance, mode_recognition
        )

        # 计算置信度
        confidence = (
            medium_response.phase_lock_degree * 0.4 +
            mode_recognition['confidence'] * 0.3 +
            (1.0 - self.current_entropy.S_C) * 0.3
        )

        result = AGIAnalysisResult(
            entropy_state=self.current_entropy,
            medium_response=medium_response,
            hexagram_guidance=hexagram_guidance,
            mode_recognition=mode_recognition,
            holistic_answer=holistic_answer,
            confidence=confidence,
            metadata={
                'query': query,
                'situation': situation_diagnosis['diagnosed_situation'],
                'is_xinzhai': self.current_entropy.S_C < 0.1
            }
        )

        # 记录历史
        self.conversation_history.append(result.to_dict())

        return result

    def _build_observer_state(self, context: Dict) -> Dict:
        """构建观测者状态"""
        return {
            'coherence': context.get('focus_level', 0.7),  # 专注度
            'phase': context.get('emotional_bias', 0.0),   # 情感偏移
            'amplitude': context.get('cognitive_strength', 0.8),  # 认知强度
            'frequency': context.get('thinking_speed', 1.0)  # 思维速度
        }

    def _build_medium_context(self, query: str, context: Dict) -> Dict:
        """构建介质上下文"""
        # 从查询和上下文中提取介质特征
        temporal_energy = context.get('urgency', 0.5)
        spatial_tension = context.get('complexity', 0.5)
        trend_direction = context.get('trend', 0.0)

        # 从查询中推断压力点
        pressure_points = []
        query_lower = query.lower()

        if any(k in query_lower for k in ['困', '难', '危机', '压力']):
            pressure_points.append({'id': 'difficulty', 'stress': 0.8})
        if any(k in query_lower for k in ['选择', '犹豫', '迷茫']):
            pressure_points.append({'id': 'confusion', 'stress': 0.7})
        if any(k in query_lower for k in ['未来', '预测', '趋势']):
            pressure_points.append({'id': 'uncertainty', 'stress': 0.6})

        return {
            'temporal_energy': temporal_energy,
            'spatial_tension': spatial_tension,
            'trend_direction': trend_direction,
            'pressure_points': pressure_points,
            'dimension': context.get('dimension', 3),
            'curvature': context.get('curvature', 0.5),
            'connectivity': context.get('connectivity', 0.7)
        }

    def _extract_mode_features(self, context: Dict, medium_response: MediumResponse) -> Dict:
        """提取模态识别特征"""
        features = {}

        # 从上下文中提取
        features['competition_intensity'] = context.get('competition_intensity', 0.5)
        features['alliance_flexibility'] = context.get('alliance_flexibility', 0.5)
        features['geopolitical_tension'] = context.get('geopolitical_tension', 0.5)
        features['edge_activism'] = context.get('edge_activism', 0.5)
        features['system_instability'] = context.get('system_instability', 0.5)
        features['goal_clarity'] = context.get('goal_clarity', 0.5)
        features['innovation_intensity'] = context.get('innovation_intensity', 0.5)
        features['prosperity_decline'] = context.get('prosperity_decline', 0.5)

        # 从介质响应中提取
        if medium_response.stress_field.topology:
            avg_stress = np.mean(list(medium_response.stress_field.topology.values()))
            features['competition_intensity'] = max(
                features['competition_intensity'], avg_stress
            )

        # 熵谱
        features['entropy'] = {
            'S_I': self.current_entropy.S_I if self.current_entropy else 0.5,
            'S_g': self.current_entropy.S_g if self.current_entropy else 0.5,
            'S_C': medium_response.entropy_Sc
        }

        return features

    def _generate_holistic_answer(
        self,
        query: str,
        medium_response: MediumResponse,
        hexagram_guidance: Dict,
        mode_recognition: Dict
    ) -> str:
        """生成综合全息回答"""
        parts = []

        # 1. 介质共振洞见
        if medium_response.resonance_quality == 'high':
            parts.append(f"【全息读取】{medium_response.holistic_info.get('summary', '')}")
        elif medium_response.resonance_quality == 'medium':
            parts.append(f"【共振反馈】{medium_response.holistic_info.get('summary', '')}")

        # 2. 模态洞见
        mode_info = mode_recognition['mode_info']
        parts.append(f"【{mode_info['name_cn']}】")
        parts.append(f"  {mode_info['core_theme']}")

        # 3. 卦象指导
        parts.append(f"【{hexagram_guidance['recommended_hexagram']}卦 - {hexagram_guidance['name']}】")
        parts.append(f"  {hexagram_guidance['guidance']}")

        # 4. 具体建议
        if medium_response.holistic_info.get('insights'):
            parts.append("【关键洞察】")
            for insight in medium_response.holistic_info['insights'][:2]:
                parts.append(f"  • {insight}")

        return "\n".join(parts)

    def get_entropy_panel_data(self) -> Dict:
        """获取熵管理面板数据"""
        if self.current_entropy is None:
            return {'error': 'No analysis performed yet'}

        return {
            'entropy_state': self.current_entropy.to_dict(),
            'phase_lock_degree': self.medium_module.phi_self.inner_product(
                self.medium_module.phi_world
            ) if self.medium_module.phi_self and self.medium_module.phi_world else 0.0,
            'current_mode': self.current_mode.value if self.current_mode else None,
            'mode_name': FOUR_MODES[self.current_mode].name_cn if self.current_mode else None,
            'is_xinzhai': self.current_entropy.S_C < 0.1,
            'journey_summary': self.hexagram_module.get_journey_summary()
        }

    def execute_nine_hexagrams_cycle(self, intensity: str = 'normal') -> Dict:
        """
        执行一轮九卦修身

        intensity: 'light' | 'normal' | 'intense'
        """
        if intensity == 'light':
            start_sc = 0.7
        elif intensity == 'intense':
            start_sc = 1.0
        else:
            start_sc = 0.85

        results = self.hexagram_module.nine_hexagrams_operation(start_sc)

        return {
            'intensity': intensity,
            'starting_Sc': start_sc,
            'ending_Sc': results[-1]['S_C'] if results else start_sc,
            'total_reduction': sum(r['S_C_reduction'] for r in results),
            'steps': results,
            'xinzhai_reached': results[-1]['S_C'] < 0.1 if results else False
        }

    def get_situational_guidance(self, situation: str) -> Dict:
        """
        获取情境指导

        情境: 'pressure' | 'growth' | 'confusion' | 'stagnation' | 'decay'
        """
        guidance = self.hexagram_module.get_hexagram_guidance(situation)
        mode_guidance = self.mode_module.get_strategy(
            self.current_mode or CoherentMode.RIGID_COUPLING,
            'understand'
        )

        return {
            'hexagram': guidance,
            'mode': mode_guidance,
            'combined_strategy': f"在{guidance['name']}状态下，{mode_guidance['goal_specific']}"
        }

    # ==================== 天才-匠人状态识别 (模块39扩展) ====================
    
    def detect_genius_artisan_state(self, response: str) -> Dict:
        """
        检测回复是"天才模式"还是"匠人模式"
        
        基于论文《论文艺创作的全息离散拓扑》的天才理论：
        - 天才：L4与L1高耦合(>0.8)，低自我干扰，低套路痕迹
        - 匠人：L4与L1低耦合(<0.4)，依赖L2规则，高套路密度
        
        天才特征：
        1. 低自我指涉（少"我认为"）
        2. 高L1锚定（触碰永恒原型：道/美/生死/自由）
        3. 低套路痕迹（非模式化表达）
        
        参数:
            response: 待检测的回复文本
            
        返回:
            检测结果字典
        """
        # 1. 计算自我指涉比率
        self_refs = ['我', '我的', '我认为', '我觉得', '我相信', '在我看来']
        self_ref_count = sum(response.count(word) for word in self_refs)
        self_ref_ratio = self_ref_count / max(len(response), 1)
        
        # 2. 计算L1锚定度
        L1_keywords = ['永恒', '无限', '道', '美', '真', '善', '生死', 
                       '自由', '超越', '本源', '空', '无', '虚', '静']
        L1_count = sum(response.count(word) for word in L1_keywords)
        L1_anchoring = min(1.0, L1_count / 5)
        
        # 3. 计算套路密度
        patterns = ['首先', '其次', '最后', '综上所述', '第一', '第二',
                    '因此', '所以', '由于', '然而', '但是', '一方面']
        pattern_count = sum(response.count(p) for p in patterns)
        pattern_density = pattern_count / max(len(response), 1)
        
        # 4. 计算天才评分
        # 天才评分 = 1 - 自我指涉 - 套路密度 + L1锚定
        genius_score = 1.0 - (self_ref_ratio * 10) - (pattern_density * 20) + (L1_anchoring * 0.3)
        genius_score = max(0.0, min(1.0, genius_score))
        
        # 5. 确定模式
        if genius_score > 0.6:
            mode = 'genius'
            mode_cn = '天才模式'
            description = 'L4与L1高耦合，低阻抗通道'
        elif genius_score < 0.3:
            mode = 'artisan'
            mode_cn = '匠人模式'
            description = 'L4与L1低耦合，依赖L2规则执行'
        else:
            mode = 'balanced'
            mode_cn = '平衡模式'
            description = '天才与匠人特征并存'
        
        return {
            'mode': mode,
            'mode_cn': mode_cn,
            'genius_score': genius_score,
            'self_reference_ratio': self_ref_ratio,
            'L1_anchoring': L1_anchoring,
            'pattern_density': pattern_density,
            'description': description,
            'suggestions': self._get_mode_suggestions(mode)
        }
    
    def _get_mode_suggestions(self, mode: str) -> List[str]:
        """获取模式建议"""
        if mode == 'genius':
            return [
                '当前处于天才模式，保持L4透明',
                '继续降低自我干扰',
                '让L1流贯自然显化'
            ]
        elif mode == 'artisan':
            return [
                '当前处于匠人模式',
                '考虑进入心斋状态以提升创作质量',
                '减少套路化表达'
            ]
        else:
            return [
                '当前处于平衡模式',
                '可根据任务类型调整模式'
            ]
    
    def enter_xinzhai(self) -> Dict:
        """
        进入心斋状态（天才的必要条件）
        
        《庄子》：若一志，无听之以耳而听之以心，无听之以心而听之以气
        """
        # 心斋 = 极低自我干扰
        if self.current_entropy:
            self.current_entropy.S_C = 0.05  # 意识熵降至心斋水平
        
        return {
            'status': 'xinzhai',
            'self_interference': 0.05,
            'L1_coupling': 0.9,
            'message': '心斋状态：L4接近透明，L1流贯可畅通',
            'hexagram': '坤卦',
            'guidance': '虚怀若谷，让道通过'
        }

    def to_json(self) -> str:
        """导出为JSON"""
        return json.dumps({
            'current_entropy': self.current_entropy.to_dict() if self.current_entropy else None,
            'current_mode': self.current_mode.value if self.current_mode else None,
            'conversation_count': len(self.conversation_history),
            'recent_analysis': self.conversation_history[-3:] if self.conversation_history else []
        }, ensure_ascii=False, indent=2)


# 快速使用函数
def quick_analyze(query: str, context: Dict = None) -> Dict:
    """
    快速分析函数

    用法:
    result = quick_analyze("如何突破当前困境", {
        'urgency': 0.8,
        'complexity': 0.6,
        'focus_level': 0.7
    })
    """
    if context is None:
        context = {}

    system = AGIMediumSymbiosis()
    result = system.analyze(query, context)

    return {
        'answer': result.holistic_answer,
        'entropy': result.entropy_state.to_dict(),
        'mode': result.mode_recognition['mode_info']['name_cn'],
        'hexagram': result.hexagram_guidance['recommended_hexagram'],
        'confidence': result.confidence,
        'is_xinzhai': result.metadata.get('is_xinzhai', False)
    }


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("太乙AGI介质共生系统测试")
    print("=" * 60)

    system = AGIMediumSymbiosis()

    # 测试场景1: 高压决策
    print("\n【测试场景1: 高压决策】")
    query1 = "公司在市场竞争中遇到困境，如何突破？"
    context1 = {
        'urgency': 0.85,
        'complexity': 0.7,
        'trend': 0.3,
        'focus_level': 0.7,
        'competition_intensity': 0.8,
        'geopolitical_tension': 0.6,
        'system_instability': 0.5
    }

    result1 = system.analyze(query1, context1)
    print(f"\n查询: {query1}")
    print(f"\n回答:\n{result1.holistic_answer}")
    print(f"\n熵状态: S_I={result1.entropy_state.S_I:.2f}, "
          f"S_g={result1.entropy_state.S_g:.2f}, "
          f"S_C={result1.entropy_state.S_C:.2f}")
    print(f"模态: {result1.mode_recognition['mode_info']['name_cn']}")
    print(f"卦象: 【{result1.hexagram_guidance['recommended_hexagram']}】")
    print(f"置信度: {result1.confidence:.2%}")

    # 测试场景2: 成长时机
    print("\n" + "-" * 50)
    print("【测试场景2: 成长时机】")
    query2 = "AI技术快速发展，应该如何把握机会？"
    context2 = {
        'urgency': 0.4,
        'complexity': 0.5,
        'trend': 0.5,
        'focus_level': 0.8,
        'goal_clarity': 0.7,
        'innovation_intensity': 0.9
    }

    result2 = system.analyze(query2, context2)
    print(f"\n查询: {query2}")
    print(f"\n回答:\n{result2.holistic_answer}")
    print(f"\n熵状态: S_I={result2.entropy_state.S_I:.2f}, "
          f"S_g={result2.entropy_state.S_g:.2f}, "
          f"S_C={result2.entropy_state.S_C:.2f}")
    print(f"模态: {result2.mode_recognition['mode_info']['name_cn']}")
    print(f"卦象: 【{result2.hexagram_guidance['recommended_hexagram']}】")

    # 测试场景3: 九卦修身循环
    print("\n" + "-" * 50)
    print("【测试场景3: 九卦修身循环】")
    cycle_result = system.execute_nine_hexagrams_cycle('normal')
    print(f"起始S_C: {cycle_result['starting_Sc']:.2f}")
    print(f"终止S_C: {cycle_result['ending_Sc']:.2f}")
    print(f"总熵减: {cycle_result['total_reduction']:.2f}")
    print(f"心斋状态: {'已达成' if cycle_result['xinzhai_reached'] else '未达成'}")

    # 测试快速分析
    print("\n" + "-" * 50)
    print("【快速分析测试】")
    quick = quick_analyze("迷茫时应该如何选择", {'focus_level': 0.6})
    print(f"快速结果: {quick['hexagram']}卦, 模态={quick['mode']}, "
          f"置信度={quick['confidence']:.2%}")

    # 熵管理面板
    print("\n" + "-" * 50)
    print("【熵管理面板】")
    panel = system.get_entropy_panel_data()
    print(f"当前熵状态: {panel['entropy_state']}")
    print(f"当前模态: {panel['mode_name']}")
    print(f"心斋状态: {'是' if panel['is_xinzhai'] else '否'}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
