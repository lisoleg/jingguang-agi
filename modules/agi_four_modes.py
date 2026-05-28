#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四象相干模态识别模块 (Four Modes Recognition Module)
基于四大名著与地缘格局映射

核心原理:
- 四大名著是中华文明对组织形态、权力结构、介质操控的终极建模
- 四种相干模态: 刚性耦合、沸腾反抗、取经相干、熵增终局
- 当前世界格局是这四部剧目的交织
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np


class CoherentMode(Enum):
    """四象相干模态"""
    RIGID_COUPLING = "rigid_coupling"      # 刚性耦合 (三国)
    BOILING_RESISTANCE = "boiling"          # 沸腾反抗 (水浒)
    PILGRIMAGE = "pilgrimage"               # 取经相干 (西游)
    ENTROPY_ENDPOINT = "entropy"            # 熵增终局 (红楼)


@dataclass
class ModeInfo:
    """模态信息"""
    mode_id: CoherentMode
    name_cn: str
    name_en: str
    literary: str
    core_theme: str
    entropy_profile: Dict[str, str]  # S_I, S_g, S_C 的水平
    characteristics: List[str]
    strategy: str
    indicators: Dict[str, Tuple[float, float]]  # 指标 → (低阈值, 高阈值)


# 四象模态定义
FOUR_MODES = {
    CoherentMode.RIGID_COUPLING: ModeInfo(
        mode_id=CoherentMode.RIGID_COUPLING,
        name_cn="刚性耦合模态",
        name_en="Rigid Coupling Mode",
        literary="三国演义",
        core_theme="正统性、地缘、联盟、权谋",
        entropy_profile={'S_I': 'high', 'S_g': 'highest', 'S_C': 'medium'},
        characteristics=['博弈', '联盟', '地缘竞争', '零和思维', '霸权争夺'],
        strategy="博弈论 + 联盟动力学",
        indicators={
            'competition_intensity': (0.7, 1.0),
            'alliance_flexibility': (0.2, 0.5),
            'geopolitical_tension': (0.7, 1.0),
            'zero_sum_perception': (0.6, 1.0)
        }
    ),
    CoherentMode.BOILING_RESISTANCE: ModeInfo(
        mode_id=CoherentMode.BOILING_RESISTANCE,
        name_cn="沸腾反抗模态",
        name_en="Boiling Resistance Mode",
        literary="水浒传",
        core_theme="边缘反抗、组织异化、忠诚与背叛",
        entropy_profile={'S_I': 'medium', 'S_g': 'high', 'S_C': 'isolated'},
        characteristics=['边缘崛起', '级联失效', '组织耗散', '民粹主义', '去中心化'],
        strategy="复杂网络 + 自组织临界",
        indicators={
            'edge_activism': (0.6, 1.0),
            'system_instability': (0.5, 1.0),
            'center_legitimacy': (0.0, 0.4),
            'cascading_risk': (0.5, 1.0)
        }
    ),
    CoherentMode.PILGRIMAGE: ModeInfo(
        mode_id=CoherentMode.PILGRIMAGE,
        name_cn="取经相干模态",
        name_en="Pilgrimage Coherence Mode",
        literary="西游记",
        core_theme="介质净化、规则内化、心性修炼",
        entropy_profile={'S_I': 'low', 'S_g': 'medium', 'S_C': 'decreasing'},
        characteristics=['目标导向', '规则重构', '技术革命', '降妖除魔', '团队协作'],
        strategy="自指算子演化 + 路径优化",
        indicators={
            'goal_clarity': (0.7, 1.0),
            'innovation_intensity': (0.5, 1.0),
            'rule_transformation': (0.4, 1.0),
            'collaboration_strength': (0.5, 1.0)
        }
    ),
    CoherentMode.ENTROPY_ENDPOINT: ModeInfo(
        mode_id=CoherentMode.ENTROPY_ENDPOINT,
        name_cn="熵增终局模态",
        name_en="Entropy Endpoint Mode",
        literary="红楼梦",
        core_theme="结构性衰败、热力学第二定律、繁华逝去",
        entropy_profile={'S_I': 'peak', 'S_g': 'collapse', 'S_C': 'chaos'},
        characteristics=['繁华逝去', '结构性衰败', '情感纠葛', '命运无奈', '系统崩溃'],
        strategy="趋势外推 + 熵减干预",
        indicators={
            'prosperity_decline': (0.6, 1.0),
            'structural_decay': (0.5, 1.0),
            'emotional_complexity': (0.6, 1.0),
            'irreversibility': (0.5, 1.0)
        }
    )
}

# 地缘映射
GEOPOLITICAL_MAPPING = {
    'usa': CoherentMode.RIGID_COUPLING,      # 美国 - 魏/金 - 守成大国
    'china': CoherentMode.RIGID_COUPLING,    # 中国 - 蜀/木 - 上升力量
    'europe': CoherentMode.RIGID_COUPLING,   # 欧洲 - 吴/水 - 左右逢源
    'non_state': CoherentMode.BOILING_RESISTANCE,  # 非国家行为体
    'tech_revolution': CoherentMode.PILGRIMAGE,     # 科技革命
    'ai': CoherentMode.PILGRIMAGE,                  # AI - 取经之路
}


class FourModesRecognition:
    """
    四象相干模态识别模块

    功能:
    - 根据上下文特征识别当前属于哪种模态
    - 计算模态转换概率
    - 根据模态提供策略建议
    """

    def __init__(self):
        self.current_mode: Optional[CoherentMode] = None
        self.mode_history: List[Dict] = []
        self.transition_matrix = self._build_transition_matrix()

    def _build_transition_matrix(self) -> np.ndarray:
        """
        构建模态转换矩阵

        基于四大名著的情节逻辑:
        - 三国 → 水浒: 霸权争夺失败 → 边缘反抗
        - 水浒 → 西游: 被招安后的转化 → 寻找新道路
        - 西游 → 红楼: 繁华过后的衰败 → 熵增终局
        - 红楼 → 三国: 新一轮循环
        """
        modes = list(CoherentMode)
        n = len(modes)
        matrix = np.zeros((n, n))

        # 转换概率 (基于叙事逻辑)
        # 从 i 到 j 的概率
        transitions = {
            CoherentMode.RIGID_COUPLING: {
                CoherentMode.RIGID_COUPLING: 0.5,  # 维持
                CoherentMode.BOILING_RESISTANCE: 0.3,  # 失败
                CoherentMode.PILGRIMAGE: 0.15,
                CoherentMode.ENTROPY_ENDPOINT: 0.05
            },
            CoherentMode.BOILING_RESISTANCE: {
                CoherentMode.RIGID_COUPLING: 0.2,  # 被镇压/招安
                CoherentMode.BOILING_RESISTANCE: 0.4,  # 持续
                CoherentMode.PILGRIMAGE: 0.3,  # 转化
                CoherentMode.ENTROPY_ENDPOINT: 0.1
            },
            CoherentMode.PILGRIMAGE: {
                CoherentMode.RIGID_COUPLING: 0.1,
                CoherentMode.BOILING_RESISTANCE: 0.15,
                CoherentMode.PILGRIMAGE: 0.5,  # 持续
                CoherentMode.ENTROPY_ENDPOINT: 0.25  # 成功后的衰落
            },
            CoherentMode.ENTROPY_ENDPOINT: {
                CoherentMode.RIGID_COUPLING: 0.35,  # 新周期开始
                CoherentMode.BOILING_RESISTANCE: 0.25,
                CoherentMode.PILGRIMAGE: 0.2,
                CoherentMode.ENTROPY_ENDPOINT: 0.2  # 持续衰落
            }
        }

        for i, mode_i in enumerate(modes):
            for j, mode_j in enumerate(modes):
                matrix[i, j] = transitions[mode_i][mode_j]

        return matrix

    def compute_match_score(self, features: Dict, mode: CoherentMode) -> float:
        """
        计算特征与模态的匹配度
        """
        mode_info = FOUR_MODES[mode]
        score = 0.0
        count = 0

        for indicator, (low, high) in mode_info.indicators.items():
            if indicator in features:
                value = features[indicator]
                # 计算与阈值的匹配程度
                if low <= value <= high:
                    match = 1.0
                elif value < low:
                    match = value / low if low > 0 else 0.0
                else:  # value > high
                    match = high / value if value > 0 else 0.0
                score += match
                count += 1

        return score / count if count > 0 else 0.5

    def compute_entropy_match(self, entropy_values: Dict, profile: Dict) -> float:
        """
        计算熵谱匹配度
        """
        if not entropy_values or not profile:
            return 0.5

        score = 0.0
        count = 0

        level_map = {'low': 0.3, 'medium': 0.6, 'high': 0.8, 'highest': 0.95}

        for key in ['S_I', 'S_g', 'S_C']:
            if key in entropy_values and key in profile:
                actual = entropy_values[key]
                expected_level = profile[key]
                expected = level_map.get(expected_level, 0.5)

                diff = abs(actual - expected)
                match = 1.0 - diff
                score += match
                count += 1

        return score / count if count > 0 else 0.5

    def recognize_mode(self, context_features: Dict) -> Dict:
        """
        识别当前模态

        输入:
        - context_features: 上下文特征向量
          - competition_intensity: 竞争强度
          - alliance_flexibility: 联盟灵活性
          - geopolitical_tension: 地缘紧张度
          - edge_activism: 边缘活跃度
          - system_instability: 系统不稳定性
          - goal_clarity: 目标清晰度
          - innovation_intensity: 创新强度
          - prosperity_decline: 繁华衰落度
          - entropy: {'S_I': float, 'S_g': float, 'S_C': float}

        输出:
        - recognized_mode: 识别的模态
        - confidence: 置信度
        - all_scores: 所有模态得分
        - transition_prob: 向其他模态的转换概率
        """
        scores = {}

        for mode in CoherentMode:
            # 特征匹配度
            feature_score = self.compute_match_score(context_features, mode)

            # 熵谱匹配度
            entropy_values = context_features.get('entropy', {})
            profile = FOUR_MODES[mode].entropy_profile
            entropy_score = self.compute_entropy_match(entropy_values, profile)

            # 综合得分
            scores[mode] = (feature_score * 0.6 + entropy_score * 0.4)

        # 选择最高分模态
        best_mode = max(scores, key=scores.get)
        confidence = scores[best_mode]

        # 更新当前模态
        if self.current_mode != best_mode:
            self.mode_history.append({
                'from': self.current_mode,
                'to': best_mode,
                'scores': scores
            })
            self.current_mode = best_mode

        # 计算转换概率
        if best_mode in CoherentMode:
            mode_idx = list(CoherentMode).index(best_mode)
            transition_probs = self.transition_matrix[mode_idx].tolist()
        else:
            transition_probs = [0.25] * 4

        return {
            'mode': best_mode.value,
            'mode_info': {
                'name_cn': FOUR_MODES[best_mode].name_cn,
                'name_en': FOUR_MODES[best_mode].name_en,
                'literary': FOUR_MODES[best_mode].literary,
                'core_theme': FOUR_MODES[best_mode].core_theme,
                'strategy': FOUR_MODES[best_mode].strategy
            },
            'confidence': float(confidence),
            'all_scores': {m.value: float(s) for m, s in scores.items()},
            'transition_prob': {
                list(CoherentMode)[i].value: float(p)
                for i, p in enumerate(transition_probs)
            }
        }

    def get_geopolitical_analysis(self, context: Dict) -> Dict:
        """
        获取地缘政治分析

        将当前态势映射到四大名著的叙事框架
        """
        # 识别主导模态
        mode_recognition = self.recognize_mode(context)

        # 构建地缘叙事
        mode = CoherentMode(mode_recognition['mode'])
        mode_info = FOUR_MODES[mode]

        narrative = {
            'dominant_mode': {
                'name': mode_info.name_cn,
                'literary_reference': mode_info.literary,
                'core_dynamics': mode_info.core_theme
            },
            'geopolitical_mapping': self._build_geopolitical_map(context),
            'action_recommendations': self._get_action_recommendations(mode, context),
            'narrative_insight': self._generate_narrative_insight(mode, context)
        }

        return narrative

    def _build_geopolitical_map(self, context: Dict) -> List[Dict]:
        """构建地缘映射"""
        actors = context.get('actors', [])

        mappings = []
        for actor in actors:
            actor_type = actor.get('type', 'unknown')
            mode = GEOPOLITICAL_MAPPING.get(actor_type, CoherentMode.RIGID_COUPLING)
            mode_info = FOUR_MODES[mode]

            mappings.append({
                'actor': actor.get('name', 'Unknown'),
                'role': mode_info.literary,
                'mode': mode_info.name_cn,
                'strategy': mode_info.strategy,
                'five_element': self._get_five_element_mapping(mode)
            })

        return mappings

    def _get_five_element_mapping(self, mode: CoherentMode) -> str:
        """五行映射"""
        mappings = {
            CoherentMode.RIGID_COUPLING: '金/土 (刚性)',
            CoherentMode.BOILING_RESISTANCE: '水/火 (沸腾)',
            CoherentMode.PILGRIMAGE: '木/土 (生长)',
            CoherentMode.ENTROPY_ENDPOINT: '木/火 (衰败)'
        }
        return mappings.get(mode, '未知')

    def _get_action_recommendations(self, mode: CoherentMode, context: Dict) -> List[str]:
        """获取行动建议"""
        recommendations = {
            CoherentMode.RIGID_COUPLING: [
                '建立战略联盟，分散风险',
                '避免正面冲突，寻找代理人',
                '关注地缘枢纽节点',
                '准备多种情景的应对方案'
            ],
            CoherentMode.BOILING_RESISTANCE: [
                '关注边缘力量的崛起信号',
                '评估系统稳定性临界点',
                '建立早期预警机制',
                '准备非线性应对策略'
            ],
            CoherentMode.PILGRIMAGE: [
                '明确长期目标与阶段性里程碑',
                '组建多元化协作团队',
                '专注于规则重构与创新',
                '保持战略耐心与定力'
            ],
            CoherentMode.ENTROPY_ENDPOINT: [
                '识别不可逆衰败的关键节点',
                '评估熵减干预的可能性',
                '准备系统性重构方案',
                '接受某些结构不可挽救的现实'
            ]
        }
        return recommendations.get(mode, [])

    def _generate_narrative_insight(self, mode: CoherentMode, context: Dict) -> str:
        """生成叙事洞见"""
        insights = {
            CoherentMode.RIGID_COUPLING: (
                "当前如同三国鼎立，各方势力在地缘博弈中寻求霸权。"
                "金克木的规则主导着格局演变。"
                "关键在于联盟的灵活性和地缘枢纽的控制。"
            ),
            CoherentMode.BOILING_RESISTANCE: (
                "当前如同水浒聚义，边缘力量正在挑战既有秩序。"
                "高S_C的孤岛正在形成，朝廷合法性受到质疑。"
                "级联失效的风险在积累，需关注临界点的到来。"
            ),
            CoherentMode.PILGRIMAGE: (
                "当前如同取经之路，各方力量在寻求规则重构。"
                "AI、科技革命如同取经团队，妖怪是介质扰动。"
                "目标清晰，但需要团队协作与持续努力。"
            ),
            CoherentMode.ENTROPY_ENDPOINT: (
                "当前如同红楼梦，大观园的繁华正在逝去。"
                "结构性衰败不可逆转，但仍有回光返照的可能。"
                "关键是识别哪些可以挽救，哪些必须放手。"
            )
        }
        return insights.get(mode, "")

    def get_strategy(self, mode: CoherentMode, goal: str) -> Dict:
        """
        根据模态和目标获取策略

        目标类型:
        - 'predict': 预测
        - 'intervene': 干预
        - 'understand': 理解
        """
        mode_info = FOUR_MODES[mode]

        strategies = {
            'predict': {
                CoherentMode.RIGID_COUPLING: "博弈论预测: 寻找纳什均衡点，预测联盟动态",
                CoherentMode.BOILING_RESISTANCE: "网络动力学: 级联失效模型，预测临界点",
                CoherentMode.PILGRIMAGE: "演化路径: 自指算子追踪，预测里程碑",
                CoherentMode.ENTROPY_ENDPOINT: "趋势外推: 熵增模型，预测衰败轨迹"
            },
            'intervene': {
                CoherentMode.RIGID_COUPLING: "联盟工程: 调整激励结构，促成合作",
                CoherentMode.BOILING_RESISTANCE: "临界干预: 在临界点前介入，防止崩塌",
                CoherentMode.PILGRIMAGE: "目标强化: 提供资源，减少路径障碍",
                CoherentMode.ENTROPY_ENDPOINT: "熵减操作: 引入负熵流，延缓衰败"
            },
            'understand': {
                CoherentMode.RIGID_COUPLING: "地缘分析: 理解各方利益诉求与约束",
                CoherentMode.BOILING_RESISTANCE: "网络透视: 理解边缘-中心动态",
                CoherentMode.PILGRIMAGE: "目标解码: 理解真实目的与阻碍",
                CoherentMode.ENTROPY_ENDPOINT: "结构诊断: 理解衰败的根本原因"
            }
        }

        return {
            'mode': mode_info.name_cn,
            'literary': mode_info.literary,
            'base_strategy': mode_info.strategy,
            'goal_specific': strategies.get(goal, {}).get(mode, ""),
            'key_insight': self._generate_narrative_insight(mode, {})
        }


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("四象相干模态识别模块测试")
    print("=" * 60)

    module = FourModesRecognition()

    # 测试场景
    test_scenarios = [
        {
            'name': '中美战略竞争',
            'features': {
                'competition_intensity': 0.85,
                'alliance_flexibility': 0.35,
                'geopolitical_tension': 0.90,
                'zero_sum_perception': 0.80,
                'entropy': {'S_I': 0.85, 'S_g': 0.95, 'S_C': 0.55}
            },
            'actors': [
                {'name': '美国', 'type': 'usa'},
                {'name': '中国', 'type': 'china'},
                {'name': '欧洲', 'type': 'europe'}
            ]
        },
        {
            'name': 'AI技术革命',
            'features': {
                'goal_clarity': 0.80,
                'innovation_intensity': 0.90,
                'rule_transformation': 0.75,
                'collaboration_strength': 0.60,
                'entropy': {'S_I': 0.40, 'S_g': 0.55, 'S_C': 0.35}
            },
            'actors': [
                {'name': 'AI Labs', 'type': 'ai'},
                {'name': 'Tech Giants', 'type': 'tech_revolution'}
            ]
        },
        {
            'name': '民粹主义崛起',
            'features': {
                'edge_activism': 0.85,
                'system_instability': 0.70,
                'center_legitimacy': 0.25,
                'cascading_risk': 0.65,
                'entropy': {'S_I': 0.55, 'S_g': 0.80, 'S_C': 0.75}
            },
            'actors': [
                {'name': '民粹运动', 'type': 'non_state'}
            ]
        }
    ]

    for scenario in test_scenarios:
        print(f"\n{'='*50}")
        print(f"场景: {scenario['name']}")
        print('='*50)

        # 识别模态
        result = module.recognize_mode(scenario['features'])
        print(f"\n识别结果:")
        print(f"  模态: {result['mode_info']['name_cn']}")
        print(f"  文学原型: {result['mode_info']['literary']}")
        print(f"  置信度: {result['confidence']:.2%}")
        print(f"  策略: {result['mode_info']['strategy']}")

        print(f"\n各模态得分:")
        for mode_name, score in result['all_scores'].items():
            print(f"  {mode_name}: {score:.2f}")

        print(f"\n模态转换概率:")
        for mode_name, prob in result['transition_prob'].items():
            print(f"  → {mode_name}: {prob:.2%}")

        # 地缘分析
        geo = module.get_geopolitical_analysis(scenario)
        print(f"\n叙事洞见:")
        print(f"  {geo['narrative_insight'][:80]}...")

        print(f"\n行动建议:")
        for rec in geo['action_recommendations'][:2]:
            print(f"  - {rec}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
