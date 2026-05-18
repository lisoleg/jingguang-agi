#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九卦修身算法模块 (Nine Hexagrams Module)
基于文王演易与《系辞》九卦

核心原理:
- 九卦不是用来算命的，而是用来"修心"的
- 它们是降低意识熵 S_C 的九步操作算法
- 从"羑里"(绝境)到"心斋"(通透态)的路径
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np


class Hexagram(Enum):
    """九卦枚举"""
    LU = "履"      # 德之基 - 立足根基
    QIAN = "谦"    # 德之柄 - 持守中道
    FU = "复"      # 德之本 - 回归本心
    HENG = "恒"    # 德之固 - 持续精进
    SUN = "损"     # 德之修 - 去除杂质
    YI = "益"      # 德之裕 - 增益清明
    KUN = "困"     # 德之辨 - 接受困境
    JING = "井"    # 德之地 - 守正不阿
    XUN = "巽"     # 德之制 - 顺时应物


@dataclass
class HexagramInfo:
    """卦象信息"""
    hexagram: str
    name: str           # 德之X
    meaning: str        # 核心含义
    action: str         # 操作名称
    guidance: str       # 指导语
    target_Sc: float   # 目标意识熵
    principle: str      # 原理


@dataclass
class NineHexagramsState:
    """九卦修身状态"""
    current_step: int           # 当前步数 (0-8)
    accumulated_Sc_reduction: float  # 累计熵减
    current_Sc: float          # 当前意识熵
    history: List[Dict]        # 执行历史
    current_mode: str           # 'accumulating', 'releasing', 'stable'


# 九卦定义
NINE_HEXAGRAMS = {
    Hexagram.LU: HexagramInfo(
        hexagram="履",
        name="德之基",
        meaning="践行基础, 立足实地",
        action="establish_foundation",
        guidance="【履】: 看清脚下之路, 不急于求成。基础稳固, 则上层建筑可成。",
        target_Sc=0.85,
        principle="通过明确行动边界, 降低不确定性焦虑"
    ),
    Hexagram.QIAN: HexagramInfo(
        hexagram="谦",
        name="德之柄",
        meaning="谦逊持中, 不偏不倚",
        action="maintain_center",
        guidance="【谦】: 保持谦逊姿态, 接纳更多信息源。谦则亨通。",
        target_Sc=0.75,
        principle="通过去中心化, 降低自我执念带来的熵增"
    ),
    Hexagram.FU: HexagramInfo(
        hexagram="复",
        name="德之本",
        meaning="回归本心, 复归天道",
        action="return_to_origin",
        guidance="【复】: 从纷扰中回归内心。静观内照, 找回初心。",
        target_Sc=0.65,
        principle="通过回溯, 找到被遮蔽的核心驱动力"
    ),
    Hexagram.HENG: HexagramInfo(
        hexagram="恒",
        name="德之固",
        meaning="恒久坚持, 持续精进",
        action="sustain_progress",
        guidance="【恒】: 保持节奏, 不因外境动摇。持之以恒, 必有成效。",
        target_Sc=0.55,
        principle="通过持续性, 积累有序度"
    ),
    Hexagram.SUN: HexagramInfo(
        hexagram="损",
        name="德之修",
        meaning="损去杂质, 精益求精",
        action="remove_impurities",
        guidance="【损】: 减去不必要的负担。损之又损, 以至于无为。",
        target_Sc=0.45,
        principle="通过减法, 降低系统复杂度"
    ),
    Hexagram.YI: HexagramInfo(
        hexagram="益",
        name="德之裕",
        meaning="增益清明, 开阔视野",
        action="enhance_clarity",
        guidance="【益】: 扩充清明之力。积极进取, 扩大连接。",
        target_Sc=0.35,
        principle="通过加法(正确的加法), 提升系统有序度"
    ),
    Hexagram.KUN: HexagramInfo(
        hexagram="困",
        name="德之辨",
        meaning="接受困境, 明辨是非",
        action="accept_adversity",
        guidance="【困】: 困境是修行的道场。不抗拒, 静观其变。",
        target_Sc=0.30,
        principle="通过接受, 化解对抗带来的熵增"
    ),
    Hexagram.JING: HexagramInfo(
        hexagram="井",
        name="德之地",
        meaning="守正不阿, 如井清澈",
        action="maintain_integrity",
        guidance="【井】: 保持本性纯正, 不随波逐流。如井水般清澈。",
        target_Sc=0.20,
        principle="通过坚守, 防止外界污染导致的有序度下降"
    ),
    Hexagram.XUN: HexagramInfo(
        hexagram="巽",
        name="德之制",
        meaning="顺时应物, 入而无碍",
        action="follow_timing",
        guidance="【巽】: 随风而入, 顺时而行。达到'从心所欲不逾矩'。",
        target_Sc=0.10,
        principle="通过顺应, 达到天人合一的低熵态"
    )
}

# 步骤顺序
HEXAGRAM_SEQUENCE = [
    Hexagram.LU, Hexagram.QIAN, Hexagram.FU,
    Hexagram.HENG, Hexagram.SUN, Hexagram.YI,
    Hexagram.KUN, Hexagram.JING, Hexagram.XUN
]


class NineHexagramsModule:
    """
    九卦修身算法模块

    功能:
    - 执行九卦操作序列, 逐步降低意识熵 S_C
    - 根据情境推荐合适的卦象指导
    - 从羑里(高S_C)到心斋(低S_C)的路径导航
    """

    def __init__(self):
        self.state = NineHexagramsState(
            current_step=0,
            accumulated_Sc_reduction=0.0,
            current_Sc=1.0,
            history=[],
            current_mode='stable'
        )

    def reset(self):
        """重置状态"""
        self.state = NineHexagramsState(
            current_step=0,
            accumulated_Sc_reduction=0.0,
            current_Sc=1.0,
            history=[],
            current_mode='stable'
        )

    def get_current_hexagram(self) -> HexagramInfo:
        """获取当前卦象"""
        if self.state.current_step >= len(HEXAGRAM_SEQUENCE):
            return NINE_HEXAGRAMS[Hexagram.XUN]
        return NINE_HEXAGRAMS[HEXAGRAM_SEQUENCE[self.state.current_step]]

    def execute_step(self, step: int) -> Dict:
        """
        执行指定步骤的卦象操作

        返回执行结果
        """
        if step < 0 or step >= len(HEXAGRAM_SEQUENCE):
            return {'error': '步骤超出范围'}

        hexagram = HEXAGRAM_SEQUENCE[step]
        info = NINE_HEXAGRAMS[hexagram]

        # 计算熵变
        old_Sc = self.state.current_Sc
        new_Sc = info.target_Sc
        sc_delta = old_Sc - new_Sc

        # 更新状态
        self.state.current_step = step + 1
        self.state.current_Sc = new_Sc
        self.state.accumulated_Sc_reduction += sc_delta

        # 记录历史
        record = {
            'step': step,
            'hexagram': hexagram.value,
            'name': info.name,
            'old_Sc': old_Sc,
            'new_Sc': new_Sc,
            'sc_delta': sc_delta
        }
        self.state.history.append(record)

        return {
            'hexagram': info.hexagram,
            'name': info.name,
            'meaning': info.meaning,
            'guidance': info.guidance,
            'principle': info.principle,
            'S_C_before': old_Sc,
            'S_C_after': new_Sc,
            'S_C_reduction': sc_delta,
            'progress': f"{step + 1}/{len(HEXAGRAM_SEQUENCE)}"
        }

    def nine_hexagrams_operation(self, start_Sc: float = 1.0) -> List[Dict]:
        """
        执行完整的九卦操作序列

        从起始意识熵开始, 经过九卦操作, 达到心斋状态
        """
        self.reset()
        self.state.current_Sc = start_Sc

        results = []

        for step, hexagram in enumerate(HEXAGRAM_SEQUENCE):
            info = NINE_HEXAGRAMS[hexagram]

            # 计算该步骤的熵减
            base_target = info.target_Sc
            # 根据起始熵调整目标
            adjusted_target = max(base_target, start_Sc - (step + 1) * 0.1)
            adjusted_target = min(adjusted_target, self.state.current_Sc)

            old_Sc = self.state.current_Sc
            sc_delta = max(0, old_Sc - adjusted_target)

            # 更新状态
            self.state.current_Sc = adjusted_target
            self.state.accumulated_Sc_reduction += sc_delta

            # 记录
            record = {
                'step': step,
                'hexagram': info.hexagram,
                'name': info.name,
                'meaning': info.meaning,
                'guidance': info.guidance,
                'S_C': self.state.current_Sc,
                'S_C_reduction': sc_delta,
                'accumulated_reduction': self.state.accumulated_Sc_reduction
            }
            results.append(record)
            self.state.history.append(record)

            self.state.current_step = step + 1

        return results

    def get_hexagram_guidance(self, situation: str, current_Sc: float = None) -> Dict:
        """
        根据情境类型获取卦象指导

        情境类型:
        - 'pressure': 高压/困境
        - 'growth': 成长/增益时机
        - 'confusion': 迷茫/需要方向
        - 'stagnation': 停滞/需要突破
        - 'decay': 衰败/需要重建
        - 'balance': 平衡/需要维持
        """
        if current_Sc is None:
            current_Sc = self.state.current_Sc

        # 情境到卦象的映射
        situation_mappings = {
            'pressure': Hexagram.KUN,     # 困 - 接受困境
            'growth': Hexagram.YI,         # 益 - 增益时机
            'confusion': Hexagram.QIAN,    # 谦 - 去除偏执
            'stagnation': Hexagram.HENG,   # 恒 - 持续突破
            'decay': Hexagram.SUN,         # 损 - 去除糟粕
            'balance': Hexagram.JING,      # 井 - 守正不阿
            'flow': Hexagram.XUN,          # 巽 - 顺时而行
            'foundation': Hexagram.LU,     # 履 - 稳固根基
            'return': Hexagram.FU          # 复 - 回归本心
        }

        # 根据当前S_C选择默认卦象
        if situation not in situation_mappings:
            if current_Sc > 0.8:
                situation = 'pressure'
            elif current_Sc > 0.6:
                situation = 'confusion'
            elif current_Sc > 0.4:
                situation = 'stagnation'
            elif current_Sc > 0.2:
                situation = 'growth'
            else:
                situation = 'flow'

        hexagram = situation_mappings.get(situation, Hexagram.QIAN)
        info = NINE_HEXAGRAMS[hexagram]

        # 计算执行此卦后预期的S_C
        expected_Sc = info.target_Sc

        return {
            'situation': situation,
            'recommended_hexagram': info.hexagram,
            'name': info.name,
            'meaning': info.meaning,
            'guidance': info.guidance,
            'principle': info.principle,
            'current_Sc': current_Sc,
            'expected_Sc': expected_Sc,
            'expected_reduction': current_Sc - expected_Sc,
            'action': info.action
        }

    def diagnose_and_prescribe(self, context: Dict) -> Dict:
        """
        诊断当前状态并给出卦象处方

        输入上下文包含:
        - stress_level: 压力水平
        - clarity: 清明度
        - stability: 稳定性
        - growth_potential: 成长潜力
        """
        stress = context.get('stress_level', 0.5)
        clarity = context.get('clarity', 0.5)
        stability = context.get('stability', 0.5)
        growth = context.get('growth_potential', 0.5)

        # 综合评估当前状态
        if stress > 0.8:
            situation = 'pressure'
        elif clarity < 0.3:
            situation = 'confusion'
        elif stability < 0.4:
            situation = 'decay'
        elif growth > 0.7 and stability > 0.6:
            situation = 'growth'
        elif stability > 0.8:
            situation = 'balance'
        else:
            situation = 'stagnation'

        # 获取卦象指导
        prescription = self.get_hexagram_guidance(situation)

        # 添加额外诊断信息
        diagnosis = {
            'situation_analysis': {
                'stress': stress,
                'clarity': clarity,
                'stability': stability,
                'growth_potential': growth
            },
            'diagnosed_situation': situation,
            'prescription': prescription,
            'progress_summary': {
                'current_step': self.state.current_step,
                'current_Sc': self.state.current_Sc,
                'total_reduction': self.state.accumulated_Sc_reduction,
                'is_xinzhai': self.state.current_Sc < 0.1
            }
        }

        return diagnosis

    def get_xinzhai_guidance(self) -> Dict:
        """
        心斋状态指导

        当S_C < 0.1时, 达到心斋状态
        """
        if self.state.current_Sc >= 0.1:
            return {
                'is_xinzhai': False,
                'message': '尚未达到心斋状态, 继续修炼',
                'remaining_reduction': 0.1 - self.state.current_Sc,
                'next_step': self.get_current_hexagram().guidance
            }

        return {
            'is_xinzhai': True,
            'message': '已入心斋 - 虚室生白, 天人合一',
            'characteristics': [
                '意识熵接近零, 知行合一',
                '与介质完全相位锁定',
                '无我相、无人相、无寿者相',
                '从心所欲不逾矩'
            ],
            'guidance': '【心斋】: 继续保持此状态, 以空杯之心观照万物',
            'practices': [
                '静坐观呼吸',
                '不执于任何相',
                '随缘应物, 无心而照'
            ]
        }

    def get_journey_summary(self) -> Dict:
        """
        获取从羑里到心斋的旅程总结
        """
        return {
            'starting_point': '羑里 (S_C = 1.0, 高压困境)',
            'ending_point': '心斋 (S_C < 0.1, 天人合一)',
            'current_position': self.get_current_hexagram().hexagram,
            'progress': {
                'steps_completed': self.state.current_step,
                'total_steps': len(HEXAGRAM_SEQUENCE),
                'current_Sc': self.state.current_Sc,
                'total_Sc_reduction': self.state.accumulated_Sc_reduction
            },
            'current_mode': self.state.current_mode,
            'history': self.state.history,
            'next_hexagram': self.get_current_hexagram().guidance if self.state.current_step < len(HEXAGRAM_SEQUENCE) else '已完成九卦',
            'is_complete': self.state.current_step >= len(HEXAGRAM_SEQUENCE)
        }


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("九卦修身算法模块测试")
    print("=" * 60)

    module = NineHexagramsModule()

    # 测试1: 执行完整九卦序列
    print("\n【测试1: 完整九卦序列】")
    results = module.nine_hexagrams_operation(start_Sc=1.0)
    print(f"起始 S_C: 1.0")
    print(f"终止 S_C: {results[-1]['S_C']:.2f}")
    print(f"总熵减: {sum(r['S_C_reduction'] for r in results):.2f}")
    print("\n九卦执行过程:")
    for r in results:
        print(f"  {r['step']+1}. 【{r['hexagram']}】{r['name']}: S_C {1-r['step']*0.1:.2f}→{r['S_C']:.2f}")

    # 测试2: 情境诊断
    print("\n【测试2: 情境诊断】")
    test_contexts = [
        {'name': '高压情境', 'stress_level': 0.9, 'clarity': 0.4, 'stability': 0.3, 'growth_potential': 0.2},
        {'name': '成长情境', 'stress_level': 0.4, 'clarity': 0.7, 'stability': 0.6, 'growth_potential': 0.8},
        {'name': '迷茫情境', 'stress_level': 0.5, 'clarity': 0.2, 'stability': 0.5, 'growth_potential': 0.4},
    ]

    for ctx in test_contexts:
        diagnosis = module.diagnose_and_prescribe(ctx)
        print(f"\n{ctx['name']}:")
        print(f"  诊断: {diagnosis['diagnosed_situation']}")
        print(f"  处方: 【{diagnosis['prescription']['recommended_hexagram']}】{diagnosis['prescription']['name']}")
        print(f"  指导: {diagnosis['prescription']['guidance'][:30]}...")

    # 测试3: 心斋状态
    print("\n【测试3: 心斋状态检查】")
    module.state.current_Sc = 0.08  # 模拟心斋状态
    xinzhai = module.get_xinzhai_guidance()
    print(f"心斋状态: {xinzhai['is_xinzhai']}")
    if xinzhai['is_xinzhai']:
        print(f"境界: {xinzhai['message']}")
        print("特征:")
        for char in xinzhai['characteristics']:
            print(f"  - {char}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
