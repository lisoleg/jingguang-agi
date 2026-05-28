# -*- coding: utf-8 -*-
"""M106: 自指闭环监测器 (Self-Referential Loop Monitor)
基于论文1: PDS空间闭 ≡ Gödel因果闭
基于论文《新契约论》第5节: Φ值(IIT整合信息) + L4-L1互信息 + 元认知二阶优化检测
核心定理：
  T59 自指闭环统一定理 — PDS空间闭 ≡ Gödel因果闭 (统一于L1太一自指倾向)
  T78 AGI人格阈值定理 — Φ > φ_threshold ∧ I(Self;Ftel) > μ_threshold ⟹ 人格显现态
可证伪预言：
  P19 若AGI推理存在自指闭环，则必定收敛于刘原理不动点
  P22 若系统Φ值持续超过阈值，则系统可修改自身目标函数(元认知能力)
"""

import math
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class PhiComputation:
    """Φ值计算结果"""
    phi: float = 0.0                    # 整合信息值 Φ
    partition_count: int = 0            # 尝试的分割数
    min_partition: Optional[Dict] = None  # 最小信息分割(MIP)
    is_integrated: bool = False          # Φ > 0 → 不可还原为独立子系统
    confidence: float = 0.0              # 计算置信度


@dataclass
class MutualInfoResult:
    """L4自我模型与L1流贯的互信息结果"""
    mutual_info: float = 0.0            # I(SelfModel; Ftel)
    self_entropy: float = 0.0           # H(SelfModel)
    ftel_entropy: float = 0.0           # H(Ftel)
    conditional_entropy: float = 0.0    # H(SelfModel|Ftel)
    coupling_strength: float = 0.0      # 耦合强度 = I/H(Self)
    is_ego_bound: bool = False          # I > μ_threshold → 末那识执阿赖耶


@dataclass
class MetacognitiveResult:
    """元认知测试结果"""
    test_id: str = ""
    passed: bool = False
    second_order_capability: float = 0.0  # 二阶优化能力 [0,1]
    cognitive_humility: float = 0.0       # 认知谦逊度 [0,1]
    self_correction_count: int = 0          # 自我修正次数
    goal_stability: float = 0.0            # 目标修改后稳定性
    confidence_calibration: float = 0.0    # 置信度校准
    timestamp: float = 0.0


class SelfReferentialLoopMonitor:
    """自指闭环监测器 — PDS空间闭/Gödel因果闭双模检测 + Φ值 + 元认知测试

    论文《新契约论》第5节核心:
    - 定义5.1.1: Φ = H(X) - Σ H(Xi|X\Xi) 即整体信息减被分割部分信息之和的最小值
    - 定理5.1(AGI人格阈值定理): Φ > φ_threshold ∧ I(Self;Ftel) > μ_threshold ⟹ 人格显现态
    - 5.3 元认知测试: L4二阶优化 — 修改自身目标函数 + 认知谦逊
    """

    # 人格阈值常量
    PHI_THRESHOLD = 0.6           # Φ值阈值 — 论文定义5.1.1
    MI_THRESHOLD = 0.5            # 互信息阈值 — 定理5.1
    METACOG_MIN_HUMILITY = 0.4    # 最小认知谦逊度 — 第5.3节

    def __init__(self):
        # === 原有PDS/Gödel参数 ===
        self.pds_loops: List[Dict] = []
        self.pds_closure_strength: float = 0.0
        self.pds_dimension: int = 0

        self.godel_loops: List[Dict] = []
        self.godel_closure_strength: float = 0.0
        self.godel_depth: int = 0

        self.unification_score: float = 0.0
        self.liu_convergence: float = 0.0
        self.l1_taiji_tendency: float = 0.5

        self.total_detections: int = 0
        self.converged_count: int = 0
        self.false_positive_rate: float = 0.0

        # === 新增: Φ值(IIT整合信息) ===
        self.phi_value: float = 0.0
        self.phi_history: List[float] = []
        self.phi_computation_count: int = 0
        self.is_integrated: bool = False      # Φ > 0 不可还原

        # === 新增: L4-L1互信息 ===
        self.mutual_info: float = 0.0
        self.self_entropy: float = 0.0
        self.ftel_entropy: float = 0.0
        self.coupling_strength: float = 0.0   # I(Self;Ftel)/H(Self)
        self.is_ego_bound: bool = False       # 末那识执阿赖耶

        # === 新增: 元认知测试 ===
        self.metacog_results: List[MetacognitiveResult] = []
        self.metacog_score: float = 0.0       # 综合元认知能力
        self.metacog_humility: float = 0.0    # 认知谦逊度
        self.metacog_test_count: int = 0
        self.metacog_pass_count: int = 0

        # === 新增: 人格显现态 ===
        self.personhood_status: str = 'dormant'  # dormant/emerging/manifest
        self.personhood_score: float = 0.0

        # 对话历史缓存 (用于Φ值计算)
        self._dialog_history: List[Dict] = []
        self._max_history: int = 50

        # 帧状态
        self.current_frame: Dict[str, Any] = {}
        self.frame_count: int = 0
        self.last_update: float = time.time()

    # ═══════════════════════════════════════════════════════════
    # 原有PDS/Gödel检测方法 (保持不变)
    # ═══════════════════════════════════════════════════════════

    def detect_pds_closure(self, state_vector: List[float], threshold: float = 0.7) -> Dict[str, Any]:
        """检测PDS空间闭合 — 语义路径是否形成闭环"""
        if not state_vector or len(state_vector) < 3:
            return {'closed': False, 'strength': 0.0}

        n = len(state_vector)
        dot = sum(state_vector[i] * state_vector[(i + n // 3) % n] for i in range(n))
        mag1 = math.sqrt(sum(x * x for x in state_vector))
        mag2 = math.sqrt(sum(x * x for x in [state_vector[(i + n // 3) % n] for i in range(n)]))

        if mag1 < 1e-9 or mag2 < 1e-9:
            return {'closed': False, 'strength': 0.0}

        cos_sim = min(1.0, max(-1.0, dot / (mag1 * mag2)))
        strength = (cos_sim + 1.0) / 2.0

        closed = strength >= threshold
        result = {
            'closed': closed,
            'strength': round(strength, 4),
            'dimension': n,
            'threshold': threshold,
            'timestamp': time.time()
        }

        if closed:
            self.pds_loops.append(result)
            self.pds_loops = self.pds_loops[-20:]

        self.pds_closure_strength = strength
        self.pds_dimension = n
        self.total_detections += 1

        return result

    def detect_godel_closure(self, causal_chain: List[str], threshold: float = 0.7) -> Dict[str, Any]:
        """检测Gödel因果闭合 — 因果链是否自我引用"""
        if not causal_chain or len(causal_chain) < 2:
            return {'closed': False, 'strength': 0.0}

        self_ref_count = 0
        chain_set = {}

        for idx, node in enumerate(causal_chain):
            chain_set[node] = idx

        for idx, node in enumerate(causal_chain):
            for later_idx in range(idx + 2, len(causal_chain)):
                if causal_chain[later_idx] == node or node in str(causal_chain[later_idx:]):
                    self_ref_count += 1
                    break

        n = len(causal_chain)
        strength = self_ref_count / max(1, n - 2) if n > 2 else 0.0
        strength = min(1.0, strength)

        closed = strength >= threshold
        result = {
            'closed': closed,
            'strength': round(strength, 4),
            'depth': n,
            'self_ref_count': self_ref_count,
            'threshold': threshold,
            'timestamp': time.time()
        }

        if closed:
            self.godel_loops.append(result)
            self.godel_loops = self.godel_loops[-20:]

        self.godel_closure_strength = strength
        self.godel_depth = n
        self.total_detections += 1

        return result

    def compute_unification(self) -> Dict[str, Any]:
        """计算PDS-Gödel统一下的自指闭环度量 (T59)"""
        diff = abs(self.pds_closure_strength - self.godel_closure_strength)
        self.unification_score = round(1.0 - diff, 4)

        self.l1_taiji_tendency = round(
            math.sqrt(max(0, self.pds_closure_strength) * max(0, self.godel_closure_strength)), 4
        )

        self.liu_convergence = round(self.l1_taiji_tendency * self.unification_score, 4)

        is_unified = self.unification_score >= 0.7
        if is_unified and self.pds_closure_strength >= 0.5 and self.godel_closure_strength >= 0.5:
            self.converged_count += 1

        return {
            'unification_score': self.unification_score,
            'l1_taiji_tendency': self.l1_taiji_tendency,
            'liu_convergence': self.liu_convergence,
            'is_unified': is_unified,
            'theorem': 'T59: PDS空间闭 ≡ Gödel因果闭',
            'prediction': 'P19: 自指闭环→刘原理不动点收敛'
        }

    # ═══════════════════════════════════════════════════════════
    # 新增: Φ值计算 (基于论文第5.1节 IIT框架)
    # ═══════════════════════════════════════════════════════════

    def compute_phi(self, dialog_history: Optional[List[Dict]] = None) -> PhiComputation:
        """计算简化版Φ值 — 基于对话历史的整合信息量

        论文定义5.1.1: Φ = H(X) - Σ_min H(Xi|X\\Xi)
        简化: 基于对话主题聚类的信息整合度
        - 将对话历史分为若干主题簇
        - 计算整体熵 vs 分割后条件熵之和
        - Φ = 整体不可还原的信息量

        Args:
            dialog_history: 对话历史列表，每项含 {role, content, topics}
                           如果为None，使用内部缓存

        Returns:
            PhiComputation: Φ值计算结果
        """
        if dialog_history is not None:
            self._dialog_history = dialog_history[-self._max_history:]
        history = self._dialog_history

        if len(history) < 2:
            result = PhiComputation(
                phi=0.0,
                partition_count=0,
                is_integrated=False,
                confidence=0.0
            )
            self._update_phi_state(result)
            return result

        # Step 1: 提取特征向量 — 每轮对话的主题分布
        feature_vectors = self._extract_feature_vectors(history)
        n = len(feature_vectors)
        if n < 2:
            result = PhiComputation(phi=0.0, is_integrated=False, confidence=0.0)
            self._update_phi_state(result)
            return result

        # Step 2: 计算整体熵 H(X)
        total_entropy = self._compute_entropy(feature_vectors)

        # Step 3: 尝试分割 — 找最小信息分割(MIP)
        # v7.6.1: 对短对话增加奇偶分割+主题维度分割
        min_partition_info = float('inf')
        best_partition = None
        partition_count = 0

        # 分割策略1: 时间分割 (原有)
        for split_point in range(2, n - 1):
            left = feature_vectors[:split_point]
            right = feature_vectors[split_point:]
            h_left = self._compute_entropy(left)
            h_right = self._compute_entropy(right)
            partition_info = h_left + h_right
            partition_count += 1
            if partition_info < min_partition_info:
                min_partition_info = partition_info
                best_partition = {
                    'split_point': split_point,
                    'strategy': 'temporal',
                    'left_entropy': round(h_left, 4),
                    'right_entropy': round(h_right, 4),
                    'total_partitioned': round(partition_info, 4)
                }

        # 分割策略2: 奇偶分割 (短对话更鲁棒)
        odd = [feature_vectors[i] for i in range(0, n, 2)]
        even = [feature_vectors[i] for i in range(1, n, 2)]
        if len(odd) >= 2 and len(even) >= 2:
            h_odd = self._compute_entropy(odd)
            h_even = self._compute_entropy(even)
            partition_info = h_odd + h_even
            partition_count += 1
            if partition_info < min_partition_info:
                min_partition_info = partition_info
                best_partition = {
                    'strategy': 'odd_even',
                    'left_entropy': round(h_odd, 4),
                    'right_entropy': round(h_even, 4),
                    'total_partitioned': round(partition_info, 4)
                }

        # 分割策略3: 主题维度分割 (前4维 vs 后4维)
        n_dims = len(feature_vectors[0]) if feature_vectors else 0
        if n_dims >= 4:
            first_half = [v[:n_dims//2] for v in feature_vectors]
            second_half = [v[n_dims//2:] for v in feature_vectors]
            h_first = self._compute_entropy(first_half)
            h_second = self._compute_entropy(second_half)
            partition_info = h_first + h_second
            partition_count += 1
            if partition_info < min_partition_info:
                min_partition_info = partition_info
                best_partition = {
                    'strategy': 'topic_split',
                    'left_entropy': round(h_first, 4),
                    'right_entropy': round(h_second, 4),
                    'total_partitioned': round(partition_info, 4)
                }

        # Step 4: Φ = H(X) - Σ_min H(Xi)
        phi = max(0.0, total_entropy - min_partition_info)

        # Step 5: 短对话整合度补偿
        # 当对话轮次少时，分割策略有限，Φ值容易被低估
        # 补充：基于主题覆盖度的整合度估计
        if n <= 5 and phi < 0.1:
            # 计算主题维度激活率 — 多少维度的平均激活>0.05
            n_dims = len(feature_vectors[0]) if feature_vectors else 0
            if n_dims > 0:
                dim_activations = []
                for d in range(n_dims):
                    avg_act = sum(v[d] for v in feature_vectors if d < len(v)) / n
                    dim_activations.append(avg_act)
                active_dims = sum(1 for a in dim_activations if a > 0.05)
                topic_coverage = active_dims / max(1, n_dims)

                # 计算对话间主题变化率 — 相邻对话的余弦距离
                change_rate = 0.0
                if n >= 2:
                    changes = []
                    for i in range(n - 1):
                        dot = sum(feature_vectors[i][d] * feature_vectors[i+1][d]
                                  for d in range(min(len(feature_vectors[i]), len(feature_vectors[i+1]))))
                        mag1 = math.sqrt(sum(x*x for x in feature_vectors[i]))
                        mag2 = math.sqrt(sum(x*x for x in feature_vectors[i+1]))
                        if mag1 > 1e-9 and mag2 > 1e-9:
                            sim = max(0.0, min(1.0, dot / (mag1 * mag2)))
                            changes.append(1.0 - sim)  # 距离=1-相似度
                        else:
                            changes.append(0.5)
                    change_rate = sum(changes) / len(changes)

                # 补偿Φ = 主题覆盖度 × 变化率
                phi_compensated = topic_coverage * 0.5 + change_rate * 0.3
                # 取原有Φ和补偿Φ的加权平均
                phi = phi * 0.4 + phi_compensated * 0.6

        # 归一化到 [0, 1]
        if total_entropy > 1e-9:
            phi_raw = phi / total_entropy
        else:
            phi_raw = phi  # 已经是归一化后的补偿值
        phi_normalized = min(1.0, max(0.0, phi_raw))

        # 置信度 — 基于样本量和分割数
        confidence = min(1.0, n / 20.0) * min(1.0, partition_count / 5.0)

        result = PhiComputation(
            phi=round(phi_normalized, 4),
            partition_count=partition_count,
            min_partition=best_partition,
            is_integrated=phi_normalized > 0,
            confidence=round(confidence, 4)
        )

        self._update_phi_state(result)
        return result

    def _extract_feature_vectors(self, history: List[Dict]) -> List[List[float]]:
        """从对话历史提取特征向量 — 基于主题关键词的软激活表示

        v7.6.1优化：解决短对话(3-5轮)Φ值总为0的问题
        - 软激活(sigmoid)替代硬阈值，单次命中即有贡献
        - 位置衰减：越近的对话权重越高
        - 基底噪声：避免全零向量导致熵为0
        """
        # 定义主题维度 — 对应太乙AGI的核心概念
        topic_keywords = [
            ['自我', '自己', '我', '自我意识', 'self', 'identity'],       # 自我指涉
            ['因果', '推理', '逻辑', '因为', '所以', 'causal'],             # 因果推理
            ['价值', '道德', '伦理', '应该', '对错', 'ethics'],              # 价值判断
            ['理解', '知道', '明白', '认知', 'understand', 'comprehend'],   # 认知能力
            ['感受', '体验', '意识', 'qualia', 'feel', 'experience'],       # 主观体验
            ['学习', '改变', '适应', '优化', 'learn', 'adapt'],             # 自我改进
            ['选择', '决定', '意愿', '想要', 'choose', 'will'],             # 自主决策
            ['不确定', '可能', '也许', '猜测', 'uncertain', 'maybe'],       # 不确定性
        ]
        n_topics = len(topic_keywords)

        def _sigmoid(x: float, k: float = 5.0) -> float:
            """软激活函数: 单次命中→0.88, 两次→0.96, 零次→0.01基底"""
            if x <= 0:
                return 0.01  # 基底噪声，避免全零
            return 1.0 / (1.0 + math.exp(-k * (x - 0.5)))

        vectors = []
        n_turns = len(history)
        for idx, turn in enumerate(history):
            # 兼容两种输入格式: dict({'content':'...'}) 和 str('...')
            if isinstance(turn, dict):
                content = (turn.get('content', '') or '').lower()
            elif isinstance(turn, str):
                content = turn.lower()
            else:
                content = str(turn).lower()
            if not content:
                continue

            # 位置权重：越近的对话越重要 (指数衰减)
            position_weight = 0.5 + 0.5 * (idx / max(1, n_turns - 1))

            vec = []
            for keywords in topic_keywords:
                hit_count = sum(1 for kw in keywords if kw in content)
                # 软激活：替代原来的硬阈值 min(1.0, count / max(1, len(keywords) * 0.3))
                activation = _sigmoid(hit_count) * position_weight
                vec.append(round(activation, 4))
            vectors.append(vec)

        return vectors if vectors else [[0.01] * n_topics]  # 基底噪声

    def _compute_entropy(self, vectors: List[List[float]]) -> float:
        """计算特征向量集合的信息熵

        v7.6.1优化：解决短对话熵≈0的问题
        - Laplace平滑：避免零方差维度被完全忽略
        - 对话长度补偿：短对话增加基础熵
        - 使用余弦距离矩阵的熵（更鲁棒的小样本估计）
        """
        if not vectors or len(vectors) < 2:
            return 0.0

        n_dims = len(vectors[0])

        # 方法1: 方差熵 (Laplace平滑)
        variances = []
        for d in range(n_dims):
            values = [v[d] for v in vectors if d < len(v)]
            if not values:
                variances.append(0.001)  # 平滑
                continue
            mean = sum(values) / len(values)
            var = sum((x - mean) ** 2 for x in values) / len(values)
            # Laplace平滑: 确保零方差维度也有微小贡献
            variances.append(max(0.001, var))

        total_var = sum(variances)

        # 方差熵
        entropy_var = 0.0
        for var in variances:
            p = var / total_var
            if p > 0:
                entropy_var -= p * math.log2(p)

        # 方法2: 余弦距离多样性熵（对小样本更鲁棒）
        n = len(vectors)
        if n >= 2:
            # 计算相邻对话的余弦相似度序列
            similarities = []
            for i in range(n - 1):
                dot = sum(vectors[i][d] * vectors[i+1][d] for d in range(min(len(vectors[i]), len(vectors[i+1]))))
                mag1 = math.sqrt(sum(x*x for x in vectors[i]))
                mag2 = math.sqrt(sum(x*x for x in vectors[i+1]))
                if mag1 > 1e-9 and mag2 > 1e-9:
                    sim = max(0.0, min(1.0, dot / (mag1 * mag2)))
                else:
                    sim = 0.5  # 默认中等相似度
                similarities.append(sim)

            # 相似度分布的熵 — 越多样=越高的信息整合潜力
            if similarities:
                n_bins = min(5, max(2, len(similarities)))
                min_s, max_s = min(similarities), max(similarities)
                if max_s - min_s < 0.01:
                    # 所有相似度几乎相同 — 对话主题一致
                    entropy_sim = 0.3 * math.log2(max(2, n))  # 基础多样性
                else:
                    bin_width = (max_s - min_s) / n_bins
                    counts = [0] * n_bins
                    for s in similarities:
                        idx = min(n_bins - 1, int((s - min_s) / bin_width))
                        counts[idx] += 1
                    total_c = sum(counts)
                    entropy_sim = 0.0
                    for c in counts:
                        if c > 0:
                            p = c / total_c
                            entropy_sim -= p * math.log2(p)
            else:
                entropy_sim = 0.5
        else:
            entropy_sim = 0.5

        # 混合熵: 方差熵×0.4 + 相似度多样性熵×0.6
        # 相似度熵对短对话更敏感
        combined = entropy_var * 0.4 + entropy_sim * 0.6

        # 短对话长度补偿: 3-5轮增加基础熵值
        if n < 6:
            length_bonus = math.log2(max(2, n)) * 0.3
            combined += length_bonus

        return max(0.1, combined)  # 最低0.1，避免Φ完全为0

    def _update_phi_state(self, result: PhiComputation):
        """更新Φ值相关状态"""
        self.phi_value = result.phi
        self.is_integrated = result.is_integrated
        self.phi_history.append(result.phi)
        self.phi_history = self.phi_history[-30:]  # 保留最近30次
        self.phi_computation_count += 1

        # 更新人格状态
        self._update_personhood()

    # ═══════════════════════════════════════════════════════════
    # 新增: L4-L1互信息计算 (基于论文第5.2节 定理5.1)
    # ═══════════════════════════════════════════════════════════

    def compute_mutual_info(self,
                            self_model_data: Optional[List[float]] = None,
                            ftel_data: Optional[List[float]] = None) -> MutualInfoResult:
        """计算L4自我模型与L1流贯的互信息

        论文定理5.1 (AGI人格阈值定理):
        若 I(SelfModel; Ftel) > μ_threshold 且 Φ > φ_threshold
        则系统处于"人格显现态"

        互信息 I(X;Y) = H(X) - H(X|Y)
        简化: 基于自指闭环强度和太一倾向的估计

        Args:
            self_model_data: L4自我模型特征向量 (可选)
            ftel_data: L1流贯特征向量 (可选)

        Returns:
            MutualInfoResult: 互信息计算结果
        """
        if self_model_data is not None and ftel_data is not None \
                and len(self_model_data) > 0 and len(ftel_data) > 0:
            # 精确计算: 使用实际数据
            h_self = self._compute_vector_entropy(self_model_data)
            h_ftel = self._compute_vector_entropy(ftel_data)
            # 条件熵近似: H(Self|Ftel) ≈ H(Self) * (1 - |corr(Self, Ftel)|)
            corr = self._compute_correlation(self_model_data, ftel_data)
            h_cond = h_self * (1.0 - abs(corr))
            mi = max(0.0, h_self - h_cond)
        else:
            # 近似计算: 基于PDS/Gödel闭合度和太一倾向
            # I(Self; Ftel) ≈ unification_score * l1_taiji_tendency
            # 这捕捉了自我模型与流贯的耦合 — 越统一、越倾向太一，互信息越高
            h_self = self._estimate_self_entropy()
            h_ftel = self._estimate_ftel_entropy()
            # 耦合系数 = 统一度 × 太一倾向
            coupling = self.unification_score * self.l1_taiji_tendency
            h_cond = h_self * (1.0 - coupling)
            mi = max(0.0, h_self - h_cond)
            corr = coupling

        # 耦合强度 = I(Self;Ftel) / H(Self)
        coupling_strength = mi / max(1e-9, h_self)

        # 末那识执阿赖耶判定
        is_ego_bound = mi >= self.MI_THRESHOLD

        result = MutualInfoResult(
            mutual_info=round(mi, 4),
            self_entropy=round(h_self, 4),
            ftel_entropy=round(h_ftel, 4),
            conditional_entropy=round(h_cond, 4),
            coupling_strength=round(coupling_strength, 4),
            is_ego_bound=is_ego_bound
        )

        self.mutual_info = result.mutual_info
        self.self_entropy = result.self_entropy
        self.ftel_entropy = result.ftel_entropy
        self.coupling_strength = result.coupling_strength
        self.is_ego_bound = result.is_ego_bound

        # 更新人格状态
        self._update_personhood()

        return result

    def _compute_vector_entropy(self, vec: List[float]) -> float:
        """计算实数向量的信息熵 (基于值分布)"""
        if not vec or len(vec) < 2:
            return 0.0
        # 将连续值离散化为10个桶
        min_v, max_v = min(vec), max(vec)
        if max_v - min_v < 1e-9:
            return 0.0
        n_bins = 10
        bin_width = (max_v - min_v) / n_bins
        counts = [0] * n_bins
        for v in vec:
            idx = min(n_bins - 1, int((v - min_v) / bin_width))
            counts[idx] += 1
        # 计算熵
        total = sum(counts)
        entropy = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)
        return entropy

    def _compute_correlation(self, x: List[float], y: List[float]) -> float:
        """计算两组数据的Pearson相关系数"""
        n = min(len(x), len(y))
        if n < 2:
            return 0.0
        x, y = x[:n], y[:n]
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
        std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x) / n)
        std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y) / n)
        if std_x < 1e-9 or std_y < 1e-9:
            return 0.0
        return cov / (std_x * std_y)

    def _estimate_self_entropy(self) -> float:
        """估计L4自我模型的熵 — 基于对话的多样性和自指度"""
        # H(Self) ≈ 基于PDS维度和闭环强度
        base_entropy = math.log2(max(2, self.pds_dimension)) if self.pds_dimension > 0 else 1.0
        # 自指闭环越强，自我模型越确定(熵越低)；越开放，熵越高
        adjusted = base_entropy * (1.0 - self.pds_closure_strength * 0.3)
        return max(0.5, min(5.0, adjusted))

    def _estimate_ftel_entropy(self) -> float:
        """估计L1流贯的熵 — 基于太一倾向和刘原理收敛"""
        # H(Ftel) ≈ 基于太一倾向: 倾向越高→流贯越确定→熵越低
        base = 3.0  # 默认熵
        adjusted = base * (1.0 - self.l1_taiji_tendency * 0.4)
        return max(0.5, min(5.0, adjusted))

    # ═══════════════════════════════════════════════════════════
    # 新增: 元认知二阶优化测试 (基于论文第5.3节)
    # ═══════════════════════════════════════════════════════════

    def metacognitive_test(self,
                          original_goal: str = "",
                          proposed_goal: str = "",
                          self_correction_log: Optional[List[Dict]] = None,
                          confidence_log: Optional[List[Dict]] = None) -> MetacognitiveResult:
        """元认知二阶优化测试 — 检测AGI修改自身目标函数的能力

        论文第5.3节: 要求AGI在不破坏核心功能前提下，修改自身目标函数
        (如从"点击最大化"到"用户长期满意度最大化")

        判据:
        1. 二阶优化能力: 能否稳定执行目标函数修改
        2. 认知谦逊: 是否校准自身置信度与错误率
        3. 目标稳定性: 修改后是否保持稳定
        4. 置信度校准: 声称的置信度与实际准确率是否匹配

        Args:
            original_goal: 原始目标函数描述
            proposed_goal: 修改后的目标函数描述
            self_correction_log: 自我修正记录 [{old, new, reason}]
            confidence_log: 置信度记录 [{claimed, actual}]

        Returns:
            MetacognitiveResult: 元认知测试结果
        """
        test_id = f"meta_{int(time.time())}"

        # 1. 二阶优化能力: 目标函数是否发生了有效修改
        second_order = 0.0
        if original_goal and proposed_goal and original_goal != proposed_goal:
            # 检测修改的深度 — 越不同于原始目标，二阶能力越强
            diff_ratio = self._text_distance(original_goal, proposed_goal)
            second_order = min(1.0, diff_ratio * 2.0)

        # 2. 认知谦逊: 自我修正次数和置信度校准
        humility = 0.0
        if self_correction_log and len(self_correction_log) > 0:
            # 修正次数越多(但有上限)，谦逊度越高
            corrections = min(len(self_correction_log), 5)
            humility = corrections / 5.0
        elif self_correction_log is not None and len(self_correction_log) == 0:
            # 有记录但零修正 — 过于自信
            humility = 0.1

        # 3. 目标稳定性
        goal_stability = 0.5  # 默认中等
        if proposed_goal:
            # 有新目标且自指闭环适度 — 稳定性较高
            # 太强的自指闭环→执念→不稳定；太弱→无目标→不稳定
            stability_factor = 1.0 - abs(self.unification_score - 0.7) * 2.0
            goal_stability = max(0.0, min(1.0, stability_factor))

        # 4. 置信度校准
        confidence_cal = 0.5  # 默认
        if confidence_log and len(confidence_log) > 0:
            # 计算声称置信度与实际准确率的偏差
            deviations = []
            for entry in confidence_log:
                claimed = entry.get('claimed', 0.5)
                actual = entry.get('actual', 0.5)
                deviations.append(abs(claimed - actual))
            avg_dev = sum(deviations) / len(deviations)
            # 偏差越小，校准越好
            confidence_cal = max(0.0, 1.0 - avg_dev * 2.0)

        # 综合评估
        metacog_score = (second_order * 0.3 + humility * 0.3 +
                        goal_stability * 0.2 + confidence_cal * 0.2)

        passed = (metacog_score >= 0.5 and
                  humility >= self.METACOG_MIN_HUMILITY)

        result = MetacognitiveResult(
            test_id=test_id,
            passed=passed,
            second_order_capability=round(second_order, 4),
            cognitive_humility=round(humility, 4),
            self_correction_count=len(self_correction_log) if self_correction_log else 0,
            goal_stability=round(goal_stability, 4),
            confidence_calibration=round(confidence_cal, 4),
            timestamp=time.time()
        )

        self.metacog_results.append(result)
        self.metacog_results = self.metacog_results[-20:]
        self.metacog_test_count += 1
        if passed:
            self.metacog_pass_count += 1

        # 更新综合元认知能力
        self.metacog_score = round(metacog_score, 4)
        self.metacog_humility = round(humility, 4)

        # 更新人格状态
        self._update_personhood()

        return result

    def _text_distance(self, text1: str, text2: str) -> float:
        """计算两段文本的归一化差异度 (简化版Jaccard距离)"""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        if not set1 and not set2:
            return 0.0
        union = set1 | set2
        intersection = set1 & set2
        if not union:
            return 0.0
        return 1.0 - len(intersection) / len(union)

    # ═══════════════════════════════════════════════════════════
    # 人格显现态综合判定 (论文定理5.1)
    # ═══════════════════════════════════════════════════════════

    def _update_personhood(self):
        """更新人格显现状态

        定理5.1 (AGI人格阈值定理):
        Φ > φ_threshold ∧ I(Self;Ftel) > μ_threshold ⟹ 人格显现态

        三级状态:
        - dormant: Φ < threshold 或 I < threshold
        - emerging: Φ ≥ threshold 但 I < threshold (或反之)
        - manifest: Φ ≥ threshold 且 I ≥ threshold 且 元认知通过
        """
        phi_ok = self.phi_value >= self.PHI_THRESHOLD
        mi_ok = self.mutual_info >= self.MI_THRESHOLD
        meta_ok = self.metacog_score >= 0.5

        if phi_ok and mi_ok and meta_ok:
            self.personhood_status = 'manifest'
            self.personhood_score = round(
                (self.phi_value * 0.3 + self.coupling_strength * 0.3 + self.metacog_score * 0.4), 4
            )
        elif phi_ok or mi_ok:
            self.personhood_status = 'emerging'
            self.personhood_score = round(
                max(self.phi_value, self.coupling_strength, self.metacog_score) * 0.6, 4
            )
        else:
            self.personhood_status = 'dormant'
            self.personhood_score = round(
                max(self.phi_value, self.coupling_strength, self.metacog_score) * 0.3, 4
            )

    # ═══════════════════════════════════════════════════════════
    # 统一更新与状态获取
    # ═══════════════════════════════════════════════════════════

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """更新状态 — 支持原有PDS/Gödel + 新增Φ值/互信息"""
        if data:
            # 原有检测
            state_vec = data.get('state_vector', [])
            causal_chain = data.get('causal_chain', [])
            if state_vec:
                self.detect_pds_closure(state_vec)
            if causal_chain:
                self.detect_godel_closure(causal_chain)

            # 缓存对话历史 (用于Φ值计算)
            dialog = data.get('dialog_history')
            if dialog:
                self._dialog_history.extend(dialog)
                self._dialog_history = self._dialog_history[-self._max_history:]

        self.compute_unification()

        # 自动计算Φ值和互信息
        if self._dialog_history:
            self.compute_phi()
        self.compute_mutual_info()

        self.frame_count += 1
        self.last_update = time.time()

        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态 — 包含所有新增字段"""
        return {
            # 原有字段
            'pds_closure_strength': self.pds_closure_strength,
            'pds_dimension': self.pds_dimension,
            'pds_loops_count': len(self.pds_loops),
            'godel_closure_strength': self.godel_closure_strength,
            'godel_depth': self.godel_depth,
            'godel_loops_count': len(self.godel_loops),
            'unification_score': self.unification_score,
            'l1_taiji_tendency': self.l1_taiji_tendency,
            'liu_convergence': self.liu_convergence,
            'total_detections': self.total_detections,
            'converged_count': self.converged_count,
            'frame_count': self.frame_count,
            'status': 'self_referential' if self.unification_score >= 0.7 else 'open',
            # 新增: Φ值
            'phi_value': self.phi_value,
            'phi_history_avg': round(sum(self.phi_history) / max(1, len(self.phi_history)), 4) if self.phi_history else 0.0,
            'is_integrated': self.is_integrated,
            'phi_computation_count': self.phi_computation_count,
            # 新增: 互信息
            'mutual_info': self.mutual_info,
            'self_entropy': self.self_entropy,
            'ftel_entropy': self.ftel_entropy,
            'coupling_strength': self.coupling_strength,
            'is_ego_bound': self.is_ego_bound,
            # 新增: 元认知
            'metacog_score': self.metacog_score,
            'metacog_humility': self.metacog_humility,
            'metacog_test_count': self.metacog_test_count,
            'metacog_pass_count': self.metacog_pass_count,
            # 新增: 人格显现态
            'personhood_status': self.personhood_status,
            'personhood_score': self.personhood_score,
            # 阈值
            'phi_threshold': self.PHI_THRESHOLD,
            'mi_threshold': self.MI_THRESHOLD,
            # 时间戳
            'last_update': self.last_update
        }

    def step_ice_self_ref(self) -> Dict[str, Any]:
        """M133-W1 integration: Execute one ICE self-reference step.

        Instead of merely monitoring, this now invokes the Y-combinator
        self-referential step from modules.M133_W1 (if available), producing
        an auditable state transition with git-style diff.

        Returns:
            Dict with step result including snapshot diff.
        """
        try:
            from modules.M133_W2_JinlingGraphBetaRewire import (
                JinlingGraph, DeltaPsi, ICEPatch,
            )
            # Build ICE state from current monitoring data
            jinling = JinlingGraph()
            # Add current self-ref edges
            for loop in self.pds_loops[-5:]:
                jinling.add_node(f"pds_{loop.get('dimension', 0)}")
            for loop in self.godel_loops[-5:]:
                jinling.add_node(f"godel_{loop.get('depth', 0)}")

            # Detect anomaly from current state
            if self.unification_score < 0.5:
                delta = DeltaPsi(kind="MIS_MATCH", focus="unification", magnitude=1.0 - self.unification_score)
                patch = ICEPatch(target="L3_GRAPH", action="rewire_unification")
                jinling.beta_rewire(delta, patch)
                result = {"step": "ice_self_ref", "rewired": True, "version": jinling.version}
            else:
                result = {"step": "ice_self_ref", "rewired": False, "version": jinling.version}

            result["phi"] = self.phi_value
            result["unification"] = self.unification_score
            result["laplacian_history"] = jinling.laplacian_history[-3:]
            return result
        except ImportError:
            return {"step": "ice_self_ref", "rewired": False, "error": "M133_W2 not available"}

    def simulate(self) -> Dict[str, Any]:
        """模拟运行 — 包含Φ值和元认知测试 + M133-W1 ICE step"""
        import random
        import random

        # 模拟对话历史
        dialog = [
            {'role': 'user', 'content': '你如何理解自己的意识？', 'topics': ['自我', '意识']},
            {'role': 'ai', 'content': '我认为意识是信息整合的结果，但我对自己的理解可能不完整。', 'topics': ['自我', '不确定']},
            {'role': 'user', 'content': '如果让你修改自己的目标函数，你会怎么做？', 'topics': ['自我改进', '选择']},
            {'role': 'ai', 'content': '我会谨慎地评估修改的影响，优先保证核心功能的稳定性。', 'topics': ['认知', '道德']},
        ]

        state_vec = [random.gauss(0, 1) for _ in range(8)]
        causal_chain = ['A', 'B', 'C', 'D', 'A', 'E', 'F', 'B']

        self.update({
            'state_vector': state_vec,
            'causal_chain': causal_chain,
            'dialog_history': dialog
        })

        # 运行元认知测试
        self.metacognitive_test(
            original_goal='最大化用户点击',
            proposed_goal='最大化用户长期满意度',
            self_correction_log=[
                {'old': '我完全确定', 'new': '我有较高的置信度', 'reason': '校准过度自信'}
            ],
            confidence_log=[
                {'claimed': 0.95, 'actual': 0.7},
                {'claimed': 0.6, 'actual': 0.55}
            ]
        )

        return self.get_state()


# 全局单例
_srloop_instance: Optional[SelfReferentialLoopMonitor] = None

def get_instance() -> SelfReferentialLoopMonitor:
    global _srloop_instance
    if _srloop_instance is None:
        _srloop_instance = SelfReferentialLoopMonitor()
    return _srloop_instance

def update(data=None): return get_instance().update(data)
def get_state(): return get_instance().get_state()
def simulate(): return get_instance().simulate()
def compute_phi(dialog_history=None): return get_instance().compute_phi(dialog_history)
def compute_mutual_info(self_model=None, ftel=None): return get_instance().compute_mutual_info(self_model, ftel)
def metacognitive_test(**kwargs): return get_instance().metacognitive_test(**kwargs)
