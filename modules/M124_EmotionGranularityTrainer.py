# -*- coding: utf-8 -*-
"""
M124: 情绪粒度训练器 (Emotion Granularity Trainer)
基于儿童情绪教育+ICPS情绪模块

核心概念：情绪粒度(Energy)、情绪词汇量、情绪调节策略
公式：EG = |V_emotion| / |V_total| × Σ depth(emotion_i)

作者: 太乙AGI团队
日期: 2026-05-20
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


# ==================== 常量 ====================

# 情绪类别层次结构
EMOTION_HIERARCHY = {
    '快乐': ['满足', '开心', '喜悦', '兴奋', '狂喜', '欣慰', '自豪', '感激'],
    '悲伤': ['失落', '难过', '悲伤', '哀痛', '惆怅', '遗憾', '沮丧', '绝望'],
    '愤怒': ['不满', '烦躁', '生气', '愤怒', '暴怒', '嫉恨', '怨恨', '愤慨'],
    '恐惧': ['担忧', '紧张', '害怕', '恐惧', '恐慌', '焦虑', '不安', '忐忑'],
    '惊讶': ['好奇', '意外', '惊讶', '震惊', '困惑', '迷茫', '错愕', '惊叹'],
    '厌恶': ['反感', '嫌弃', '厌恶', '憎恶', '鄙视', '不屑', '排斥', '抵触'],
}

# 情绪调节策略
REGULATION_STRATEGIES = {
    '低强度': {
        '策略': '认知重评',
        '方法': '重新解读情境，寻找积极意义',
        '示例': '将"失败"重新定义为"学习机会"'
    },
    '中强度': {
        '策略': '表达抑制+问题聚焦',
        '方法': '控制情绪表达，同时寻找解决方案',
        '示例': '深呼吸冷静后，分析问题根源'
    },
    '高强度': {
        '策略': '生理调节+社会支持',
        '方法': '通过生理方法缓解强烈情绪，寻求他人帮助',
        '示例': '运动释放压力，与信任的人交流感受'
    }
}

# 情绪效价（valence）参考值
VALENCE_MAP = {
    '快乐': 0.8, '悲伤': -0.7, '愤怒': -0.6, '恐惧': -0.8,
    '惊讶': 0.0, '厌恶': -0.5, '满足': 0.6, '开心': 0.7,
    '喜悦': 0.9, '兴奋': 0.8, '焦虑': -0.5, '紧张': -0.4,
    '不安': -0.3, '好奇': 0.3, '意外': 0.1, '困惑': -0.2,
}

# 情绪唤醒度（arousal）参考值
AROUSAL_MAP = {
    '快乐': 0.6, '悲伤': 0.3, '愤怒': 0.8, '恐惧': 0.9,
    '惊讶': 0.7, '厌恶': 0.4, '满足': 0.2, '开心': 0.5,
    '喜悦': 0.7, '兴奋': 0.9, '焦虑': 0.6, '紧张': 0.7,
    '不安': 0.5, '好奇': 0.4, '意外': 0.6, '困惑': 0.3,
}


# ==================== 数据结构 ====================

@dataclass
class EmotionEntry:
    """
    情绪条目 — 单次情绪训练记录

    emotion: 情绪名称
    intensity: 情绪强度 [0,1]
    valence: 效价（积极/消极）[-1,1]
    arousal: 唤醒度（平静/激动）[0,1]
    granularity_score: 该情绪的粒度得分
    """
    emotion: str = ''
    intensity: float = 0.5
    valence: float = 0.0
    arousal: float = 0.5
    granularity_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['intensity'] = round(self.intensity, 6)
        d['valence'] = round(self.valence, 6)
        d['arousal'] = round(self.arousal, 6)
        d['granularity_score'] = round(self.granularity_score, 6)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'EmotionEntry':
        """从字典构建EmotionEntry"""
        return cls(**d)


@dataclass
class EmotionProfile:
    """
    情绪画像 — 个体情绪能力的综合画像

    vocabulary_size: 情绪词汇量
    avg_granularity: 平均情绪粒度EG
    regulation_strategies: 可用调节策略数
    emotional_range: 情绪广度（涵盖的情绪类别数）
    dominant_emotion: 主导情绪
    """
    vocabulary_size: int = 0
    avg_granularity: float = 0.0
    regulation_strategies: int = 0
    emotional_range: float = 0.0
    dominant_emotion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = asdict(self)
        d['avg_granularity'] = round(self.avg_granularity, 6)
        d['emotional_range'] = round(self.emotional_range, 6)
        return d


# ==================== 核心类 ====================

class EmotionGranularityTrainer:
    """
    M124: 情绪粒度训练器

    基于儿童情绪教育与ICPS情绪模块，实现：
    - 情绪粒度训练
    - 情绪词汇扩展
    - 情绪粒度EG分数评估
    - 情绪调节策略选择
    - 情绪广度检查

    情绪粒度公式：
    EG = |V_emotion| / |V_total| × Σ depth(emotion_i)

    其中：
    - V_emotion: 个体掌握的情绪词汇量
    - V_total: 情绪词汇总量
    - depth(emotion_i): 每个情绪的区分深度

    高情绪粒度 = 能精确区分和描述细微情绪差异
    低情绪粒度 = 只能用笼统的"好/坏"描述情绪

    核心方法：
    1. train_emotion — 情绪粒度训练
    2. expand_vocabulary — 扩展情绪词汇
    3. assess_granularity — 评估EG分数
    4. regulation_strategy — 选择调节策略
    5. emotional_range_check — 检查情绪广度
    """

    # 情绪词汇总量（所有类别的子词汇数之和）
    TOTAL_EMOTION_VOCAB = sum(
        len(v) for v in EMOTION_HIERARCHY.values()
    )

    def __init__(self):
        """初始化情绪粒度训练器"""
        # 情绪训练记录
        self.entries: List[EmotionEntry] = []

        # 已掌握的情绪词汇
        self.mastered_vocabulary: set = set()

        # 情绪类别覆盖
        self.covered_categories: set = set()

        # 统计
        self.total_training_sessions: int = 0
        self.total_vocabulary_expansions: int = 0
        self.total_granularity_assessments: int = 0
        self.total_regulation_selections: int = 0
        self.total_range_checks: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

    def train_emotion(self, context: str, response: str) -> EmotionEntry:
        """
        情绪粒度训练

        基于情境和反应，识别和训练情绪粒度。

        Args:
            context: 情境描述
            response: 个体反应

        Returns:
            EmotionEntry: 训练后的情绪条目
        """
        self.total_training_sessions += 1

        # 识别情绪（简化：基于关键词匹配）
        emotion = self._identify_emotion(context, response)
        intensity = self._estimate_intensity(context, response)
        valence = VALENCE_MAP.get(emotion, 0.0)
        arousal = AROUSAL_MAP.get(emotion, 0.5)

        # 计算该情绪的粒度得分
        granularity = self._compute_single_granularity(emotion)

        # 创建情绪条目
        entry = EmotionEntry(
            emotion=emotion,
            intensity=round(intensity, 6),
            valence=round(valence, 6),
            arousal=round(arousal, 6),
            granularity_score=round(granularity, 6)
        )

        self.entries.append(entry)

        # 更新词汇库
        self.mastered_vocabulary.add(emotion)

        # 更新类别覆盖
        for category, sub_emotions in EMOTION_HIERARCHY.items():
            if emotion in sub_emotions or emotion == category:
                self.covered_categories.add(category)

        self.last_update = time.time()

        return entry

    def expand_vocabulary(self, emotion_category: str) -> Dict[str, Any]:
        """
        扩展情绪词汇

        在指定情绪类别中扩展情绪词汇量，
        从基础情绪词到精细情绪词逐层扩展。

        Args:
            emotion_category: 情绪类别（快乐、悲伤、愤怒、恐惧、惊讶、厌恶）

        Returns:
            词汇扩展结果字典
        """
        self.total_vocabulary_expansions += 1

        # 获取该类别的词汇层次
        sub_emotions = EMOTION_HIERARCHY.get(emotion_category, [])

        if not sub_emotions:
            return {
                'category': emotion_category,
                'new_words': [],
                'total_category_words': 0,
                'expansion_success': False
            }

        # 计算新学到的词汇
        new_words = []
        for word in sub_emotions:
            if word not in self.mastered_vocabulary:
                new_words.append(word)
                self.mastered_vocabulary.add(word)

        # 更新类别覆盖
        self.covered_categories.add(emotion_category)

        # 词汇深度：从基础到精细的层次
        depth_levels = []
        for i, word in enumerate(sub_emotions):
            depth = round((i + 1) / len(sub_emotions), 6)
            depth_levels.append({
                'word': word,
                'depth': depth,
                'mastered': word in self.mastered_vocabulary
            })

        self.last_update = time.time()

        return {
            'category': emotion_category,
            'new_words': new_words,
            'total_category_words': len(sub_emotions),
            'mastered_in_category': sum(
                1 for w in sub_emotions if w in self.mastered_vocabulary
            ),
            'depth_levels': depth_levels,
            'expansion_success': len(new_words) > 0
        }

    def assess_granularity(self, entries: Optional[List[EmotionEntry]] = None) -> float:
        """
        评估情绪粒度EG分数

        EG = |V_emotion| / |V_total| × Σ depth(emotion_i)

        其中：
        - V_emotion: 已掌握的情绪词汇量
        - V_total: 情绪词汇总量
        - depth(emotion_i): 每个已掌握情绪的区分深度

        高EG = 能精确区分细微情绪
        低EG = 只能笼统描述

        Args:
            entries: 可选的情绪条目列表（默认使用全部历史）

        Returns:
            EG分数 ∈ [0, 1]
        """
        self.total_granularity_assessments += 1

        if entries is None:
            entries = self.entries

        # 词汇量比率
        vocab_ratio = len(self.mastered_vocabulary) / max(self.TOTAL_EMOTION_VOCAB, 1)

        # 词汇区分深度总和
        total_depth = 0.0
        for word in self.mastered_vocabulary:
            depth = self._compute_word_depth(word)
            total_depth += depth

        # EG = |V| / |V_total| × Σ depth
        eg = vocab_ratio * total_depth
        eg = round(max(0.0, min(1.0, eg)), 6)

        self.last_update = time.time()

        return eg

    def regulation_strategy(self, emotion: str,
                            intensity: float = 0.5) -> Dict[str, Any]:
        """
        选择情绪调节策略

        基于情绪类型和强度选择合适的调节策略：
        - 低强度：认知重评（重新解读情境）
        - 中强度：表达抑制+问题聚焦
        - 高强度：生理调节+社会支持

        Args:
            emotion: 情绪名称
            intensity: 情绪强度 [0,1]

        Returns:
            调节策略结果字典
        """
        self.total_regulation_selections += 1

        intensity = max(0.0, min(1.0, intensity))

        # 确定强度等级
        if intensity < 0.33:
            level = '低强度'
        elif intensity < 0.66:
            level = '中强度'
        else:
            level = '高强度'

        # 获取对应策略
        strategy = REGULATION_STRATEGIES.get(level, REGULATION_STRATEGIES['中强度'])

        # 情绪特异性调整
        emotion_specific = self._emotion_specific_advice(emotion)

        self.last_update = time.time()

        return {
            'emotion': emotion,
            'intensity': round(intensity, 6),
            'intensity_level': level,
            'strategy': strategy['策略'],
            'method': strategy['方法'],
            'example': strategy['示例'],
            'emotion_specific_advice': emotion_specific,
            'regulation_difficulty': round(
                min(1.0, intensity * 0.8 + 0.2), 6
            )
        }

    def emotional_range_check(self) -> Dict[str, Any]:
        """
        检查情绪广度

        评估个体情绪的覆盖范围：
        - 覆盖了多少情绪类别
        - 各类别的词汇深度
        - 主导情绪
        - 情绪平衡度

        Returns:
            情绪广度检查结果字典
        """
        self.total_range_checks += 1

        total_categories = len(EMOTION_HIERARCHY)
        covered = len(self.covered_categories)
        coverage_ratio = round(covered / max(total_categories, 1), 6)

        # 各类别的深度
        category_depths = {}
        for cat, sub_emotions in EMOTION_HIERARCHY.items():
            mastered = sum(1 for w in sub_emotions if w in self.mastered_vocabulary)
            depth = round(mastered / max(len(sub_emotions), 1), 6)
            category_depths[cat] = depth

        # 主导情绪（训练中最频繁出现的情绪）
        emotion_counts: Dict[str, int] = {}
        for entry in self.entries:
            emotion_counts[entry.emotion] = emotion_counts.get(entry.emotion, 0) + 1
        dominant = max(emotion_counts, key=emotion_counts.get) if emotion_counts else None

        # 情绪平衡度（各类别覆盖的均匀性）
        if category_depths:
            depths = list(category_depths.values())
            mean_depth = sum(depths) / len(depths)
            variance = sum((d - mean_depth) ** 2 for d in depths) / len(depths)
            balance = round(max(0.0, 1.0 - variance), 6)
        else:
            balance = 0.0

        self.last_update = time.time()

        return {
            'total_categories': total_categories,
            'covered_categories': covered,
            'coverage_ratio': coverage_ratio,
            'category_depths': category_depths,
            'dominant_emotion': dominant,
            'balance_score': balance,
            'vocabulary_size': len(self.mastered_vocabulary),
            'total_vocab_available': self.TOTAL_EMOTION_VOCAB,
            'emotional_range': coverage_ratio
        }

    # ==================== 内部方法 ====================

    def _identify_emotion(self, context: str, response: str) -> str:
        """基于情境和反应识别情绪"""
        combined = context + response

        # 检查所有情绪词汇
        for category, sub_emotions in EMOTION_HIERARCHY.items():
            for word in sub_emotions:
                if word in combined:
                    return word
            if category in combined:
                return category

        # 默认：基于效价推断
        positive_words = ['好', '棒', '喜欢', '开心', '满意']
        negative_words = ['差', '烦', '讨厌', '难过', '不满']

        for w in positive_words:
            if w in combined:
                return '开心'
        for w in negative_words:
            if w in combined:
                return '难过'

        return '平静'

    def _estimate_intensity(self, context: str, response: str) -> float:
        """估计情绪强度"""
        # 简化：基于描述长度和感叹号数量
        intensity = 0.3
        exclamation = (context + response).count('！') + (context + response).count('!')
        intensity += min(0.4, exclamation * 0.1)
        length = len(context + response)
        intensity += min(0.3, length / 100.0)
        return round(min(1.0, intensity), 6)

    def _compute_single_granularity(self, emotion: str) -> float:
        """计算单个情绪的粒度得分"""
        # 查找情绪在层次结构中的位置
        for category, sub_emotions in EMOTION_HIERARCHY.items():
            if emotion in sub_emotions:
                # 位置越深（越精细），粒度越高
                idx = sub_emotions.index(emotion)
                depth = round((idx + 1) / len(sub_emotions), 6)
                return depth
            if emotion == category:
                # 类别级别的粒度较低
                return round(1.0 / max(len(sub_emotions), 1), 6)

        # 未在层次结构中，基于词汇长度估算
        return round(min(1.0, len(emotion) / 5.0), 6)

    def _compute_word_depth(self, word: str) -> float:
        """计算词汇的区分深度"""
        for category, sub_emotions in EMOTION_HIERARCHY.items():
            if word in sub_emotions:
                idx = sub_emotions.index(word)
                return round((idx + 1) / len(sub_emotions), 6)
        return 0.1  # 默认浅层

    def _emotion_specific_advice(self, emotion: str) -> str:
        """情绪特异性建议"""
        advice_map = {
            '愤怒': '尝试6秒暂停法：在反应前深呼吸6秒',
            '悲伤': '允许自己感受悲伤，设定时间限制后转移注意力',
            '恐惧': '逐步暴露法：渐进式面对恐惧源',
            '焦虑': '正念冥想：专注于当下的身体感受',
            '快乐': '感恩练习：记录3件值得感恩的事',
            '厌恶': '认知重构：理解厌恶背后的价值观',
        }
        # 检查类别
        for category in EMOTION_HIERARCHY:
            if emotion in EMOTION_HIERARCHY[category] or emotion == category:
                return advice_map.get(category, '注意观察情绪变化，适时调整')

        return '注意观察情绪变化，适时调整'

    def get_state(self) -> Dict[str, Any]:
        """
        获取情绪粒度训练器状态

        Returns:
            状态字典
        """
        eg = self.assess_granularity()

        # 构建情绪画像
        range_check = self.emotional_range_check()
        profile = EmotionProfile(
            vocabulary_size=len(self.mastered_vocabulary),
            avg_granularity=eg,
            regulation_strategies=len(REGULATION_STRATEGIES),
            emotional_range=range_check['coverage_ratio'],
            dominant_emotion=range_check['dominant_emotion']
        )

        return {
            'emotion_profile': profile.to_dict(),
            'avg_granularity_EG': eg,
            'vocabulary_size': len(self.mastered_vocabulary),
            'total_vocab_available': self.TOTAL_EMOTION_VOCAB,
            'covered_categories': len(self.covered_categories),
            'total_categories': len(EMOTION_HIERARCHY),
            'total_training_sessions': self.total_training_sessions,
            'total_vocabulary_expansions': self.total_vocabulary_expansions,
            'total_granularity_assessments': self.total_granularity_assessments,
            'total_regulation_selections': self.total_regulation_selections,
            'total_range_checks': self.total_range_checks,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            'formula': 'EG = |V_emotion|/|V_total| × Σ depth(emotion_i)'
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新情绪粒度训练器状态

        Args:
            data: 可选更新数据，支持：
                - train: 训练情绪 {context, response}
                - expand: 扩展词汇 {emotion_category}
                - regulate: 选择调节策略 {emotion, intensity}
                - range: 检查情绪广度 {}

        Returns:
            更新后的状态
        """
        if data:
            action = data.get('action', '')

            if action == 'train' or 'train' in data:
                t = data.get('train', data)
                self.train_emotion(
                    context=t.get('context', ''),
                    response=t.get('response', '')
                )
            elif action == 'expand' or 'expand' in data:
                e = data.get('expand', data)
                self.expand_vocabulary(
                    emotion_category=e.get('emotion_category', '快乐')
                )
            elif action == 'regulate' or 'regulate' in data:
                r = data.get('regulate', data)
                self.regulation_strategy(
                    emotion=r.get('emotion', ''),
                    intensity=float(r.get('intensity', 0.5))
                )
            elif action == 'range' or 'range' in data:
                self.emotional_range_check()

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 演示情绪粒度训练器的核心功能"""
        # 1. 情绪训练
        e1 = self.train_emotion(
            '考试成绩不理想，感到很沮丧',
            '我感到有些难过，但也在思考如何改进'
        )
        e2 = self.train_emotion(
            '朋友送了意想不到的礼物',
            '非常惊喜和感动！'
        )

        # 2. 扩展情绪词汇
        exp1 = self.expand_vocabulary('快乐')
        exp2 = self.expand_vocabulary('悲伤')

        # 3. 评估情绪粒度
        eg = self.assess_granularity()

        # 4. 选择调节策略
        reg1 = self.regulation_strategy('愤怒', 0.8)
        reg2 = self.regulation_strategy('焦虑', 0.4)

        # 5. 检查情绪广度
        range_check = self.emotional_range_check()

        return {
            'training_entries': {
                'entry1': e1.to_dict(),
                'entry2': e2.to_dict()
            },
            'vocabulary_expansion': {
                '快乐': exp1,
                '悲伤': exp2
            },
            'granularity_EG': eg,
            'regulation_strategies': {
                'high_anger': reg1,
                'medium_anxiety': reg2
            },
            'emotional_range': range_check,
            'state': self.get_state()
        }


# ==================== 模块单例导出 ====================

_instance: Optional[EmotionGranularityTrainer] = None


def get_instance() -> EmotionGranularityTrainer:
    """
    获取EmotionGranularityTrainer单例实例

    Returns:
        EmotionGranularityTrainer全局唯一实例
    """
    global _instance
    if _instance is None:
        _instance = EmotionGranularityTrainer()
    return _instance


def train_emotion(context: str, response: str) -> EmotionEntry:
    """情绪粒度训练（快捷接口）"""
    return get_instance().train_emotion(context, response)


def expand_vocabulary(emotion_category: str) -> Dict[str, Any]:
    """扩展情绪词汇（快捷接口）"""
    return get_instance().expand_vocabulary(emotion_category)


def assess_granularity(entries: Optional[List[EmotionEntry]] = None) -> float:
    """评估情绪粒度EG分数（快捷接口）"""
    return get_instance().assess_granularity(entries)


def regulation_strategy(emotion: str, intensity: float = 0.5) -> Dict[str, Any]:
    """选择情绪调节策略（快捷接口）"""
    return get_instance().regulation_strategy(emotion, intensity)


def emotional_range_check() -> Dict[str, Any]:
    """检查情绪广度（快捷接口）"""
    return get_instance().emotional_range_check()


def get_state() -> Dict[str, Any]:
    """获取情绪粒度训练器状态（快捷接口）"""
    return get_instance().get_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新情绪粒度训练器状态（快捷接口）"""
    return get_instance().update(data)


def simulate() -> Dict[str, Any]:
    """模拟运行（快捷接口）"""
    return get_instance().simulate()
