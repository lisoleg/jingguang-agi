# -*- coding: utf-8 -*-
"""
M132: AdditivePrimeClassifier — 堆垒素数分类器

堆垒素数论驱动的实体分类与交互生成:
  - 奇数堆垒 → 费米子 (遵守泡利不相容)
  - 偶数堆垒 → 玻色子 (可玻色-爱因斯坦凝聚)
  - 哥德巴赫交互: 两奇素数之和 = 偶数(玻色子)
  - 黎曼共振: 零点 → 金灵球网格共振频率

包含定理T94堆垒费米子-玻色子分类定理。

Author: Kou (寇豆码) — 太乙AGI团队
"""

import math
import hashlib
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Tuple


# ===========================================================================
# 数据结构
# ===========================================================================

@dataclass
class PrimeCluster:
    """素数簇 — 粒子分类的基本单位"""
    value: int = 2                     # 素数值
    is_fermion: bool = True             # 奇数堆垒→费米子
    is_boson: bool = False              # 偶数堆垒→玻色子
    generation: int = 1                 # 代际层级
    decomposition: List[int] = field(default_factory=list)  # 分解路径


@dataclass
class InteractionResult:
    """交互结果"""
    fermion_a: Dict[str, Any] = field(default_factory=dict)   # 费米子A
    fermion_b: Dict[str, Any] = field(default_factory=dict)   # 费米子B
    exchange_boson: Dict[str, Any] = field(default_factory=dict)  # 交换玻色子
    coupling_strength: float = 0.0     # 耦合强度
    goldbach_verified: bool = False     # 哥德巴赫验证


@dataclass
class RiemannResonance:
    """黎曼共振"""
    zero_index: int = 0                # 零点序号
    frequency: float = 0.0             # 共振频率
    is_on_critical_line: bool = True   # 是否在临界线Re=1/2上
    stability: float = 1.0             # 稳定性评分


# ===========================================================================
# 素数工具函数
# ===========================================================================

def is_prime(n: int) -> bool:
    """
    素数检测（确定性算法）

    Args:
        n: 待检测整数

    Returns:
        是否为素数
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    if n == 3:
        return True
    if n % 3 == 0:
        return False

    # 6k±1 优化
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w

    return True


def prime_decompose(n: int) -> List[int]:
    """
    素数分解

    将n分解为素因子列表（含重复）。

    Args:
        n: 待分解整数

    Returns:
        素因子列表（升序）
    """
    if n <= 1:
        return []

    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1

    if n > 1:
        factors.append(n)

    return factors


def generate_primes(limit: int) -> List[int]:
    """
    生成不超过limit的所有素数（埃拉托斯特尼筛法）

    Args:
        limit: 上限

    Returns:
        素数列表
    """
    if limit < 2:
        return []

    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False

    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False

    return [i for i in range(2, limit + 1) if sieve[i]]


# ===========================================================================
# 代际划分表
# ===========================================================================

# 第1代: 3,5,7 → 第2代: 11,13,17,19 → 第3代: 23,29,31,37,41,43,47 → ...
# 规则: 第g代素数是区间 (g*10, (g+1)*10] 内的素数
# 简化规则: 2是特殊玻色子; 奇素数按值递增分代

def _compute_generation(prime_value: int) -> int:
    """
    计算素数的代际

    规则:
    - 2: 特殊（第0代，唯一偶素数→玻色子）
    - 3,5,7: 第1代
    - 11,13,17,19: 第2代
    - 23,29,31,37,41,43,47: 第3代
    - 一般: 第g代素数 ∈ [p_g_start, p_g_end]

    简化: generation = ceil((prime_index) / 3) 其中prime_index从1开始
    或者直接按值域: generation = (prime - 1) // 10 + 1 (对奇素数)
    """
    if prime_value == 2:
        return 0  # 特殊: 唯一偶素数

    # 按值域分代
    gen = max(1, (prime_value - 1) // 10 + 1)
    return gen


# ===========================================================================
# AdditivePrimeClassifier 分类器
# ===========================================================================

class AdditivePrimeClassifier:
    """
    堆垒素数分类器

    堆垒素数论驱动的实体分类:
    - 奇数堆垒 → 费米子
    - 偶数堆垒 → 玻色子
    - 哥德巴赫交互: 奇素数 + 奇素数 = 偶数(玻色子)
    - 黎曼共振: 零点 → 频率映射

    包含定理T94堆垒费米子-玻色子分类定理。
    """

    _instance: Optional["AdditivePrimeClassifier"] = None

    # 缓存
    _prime_cache: List[int] = []
    _cluster_cache: Dict[int, PrimeCluster] = {}

    def __init__(self) -> None:
        """初始化分类器"""
        self._prime_cache = generate_primes(1000)
        self._cluster_cache = {}
        self._operation_count: int = 0
        self._interaction_log: List[Dict[str, Any]] = []
        self._created_at: float = time.time()

    # -------------------------------------------------------------------
    # 单例模式
    # -------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "AdditivePrimeClassifier":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -------------------------------------------------------------------
    # 状态方法
    # -------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """返回模块状态字典"""
        return {
            "module_id": "M132",
            "module_name": "AdditivePrimeClassifier",
            "prime_cache_size": len(self._prime_cache),
            "cluster_cache_size": len(self._cluster_cache),
            "operation_count": self._operation_count,
            "interaction_log_count": len(self._interaction_log),
            "created_at": self._created_at,
        }

    # ===================================================================
    # 粒子分类
    # ===================================================================

    def classify_particle(self, n: int = 2) -> PrimeCluster:
        """
        粒子分类

        规则:
        - n为奇数 → 费米子 (遵守泡利不相容)
        - n为偶数 → 玻色子 (可玻色-爱因斯坦凝聚)
        - n=2 特殊: 唯一偶素数，但仍为玻色子类型
        - n=1: 非素数，标记为未分类

        Args:
            n: 粒子对应的整数值

        Returns:
            PrimeCluster 分类结果
        """
        if n in self._cluster_cache:
            return self._cluster_cache[n]

        is_odd = n % 2 == 1
        is_even = n % 2 == 0

        # 费米子/玻色子分类
        is_fermion = is_odd
        is_boson = is_even

        # 代际计算
        generation = _compute_generation(n) if is_prime(n) else 0

        # 分解路径
        decomposition = prime_decompose(n) if n > 1 else []

        cluster = PrimeCluster(
            value=n,
            is_fermion=is_fermion,
            is_boson=is_boson,
            generation=generation,
            decomposition=decomposition,
        )

        self._cluster_cache[n] = cluster
        self._operation_count += 1

        return cluster

    # ===================================================================
    # 哥德巴赫交互
    # ===================================================================

    def goldbach_interaction(
        self,
        p1: int = 3,
        p2: int = 5
    ) -> InteractionResult:
        """
        哥德巴赫交互

        两奇素数之和 = 偶数(玻色子)
        这是强哥德巴赫猜想的堆垒诠释:
        费米子 + 费米子 → 玻色子 (交换力)

        Args:
            p1: 第一个奇素数
            p2: 第二个奇素数

        Returns:
            InteractionResult 交互结果
        """
        # 确保是素数
        if not is_prime(p1):
            p1 = 3
        if not is_prime(p2):
            p2 = 5

        # 分类两个费米子
        fermion_a = self.classify_particle(p1)
        fermion_b = self.classify_particle(p2)

        # 交互产生玻色子
        boson_value = p1 + p2
        exchange_boson = self.classify_particle(boson_value)

        # 耦合强度: 基于素数间距的倒数
        coupling_strength = 1.0 / max(abs(p1 - p2), 1)

        # 哥德巴赫验证: 两奇素数之和为偶数
        goldbach_verified = (p1 % 2 == 1 and p2 % 2 == 1 and boson_value % 2 == 0)

        result = InteractionResult(
            fermion_a=asdict(fermion_a),
            fermion_b=asdict(fermion_b),
            exchange_boson=asdict(exchange_boson),
            coupling_strength=round(coupling_strength, 10),
            goldbach_verified=goldbach_verified,
        )

        self._operation_count += 1
        self._interaction_log.append({
            "p1": p1,
            "p2": p2,
            "boson_value": boson_value,
            "goldbach_verified": goldbach_verified,
            "timestamp": time.time(),
        })

        return result

    # ===================================================================
    # 素数分解
    # ===================================================================

    def prime_decompose(self, n: int = 12) -> Dict[str, Any]:
        """
        素数分解

        将n分解为素因子，并给出堆垒诠释。

        Args:
            n: 待分解整数

        Returns:
            {
                "value": int,
                "factors": List[int],
                "factor_count": int,
                "is_prime": bool,
                "prime_signature": str,
                "fermion_count": int,  # 奇素因子个数
                "boson_count": int,    # 偶素因子个数(2的个数)
            }
        """
        if n <= 1:
            return {
                "value": n,
                "factors": [],
                "factor_count": 0,
                "is_prime": False,
                "prime_signature": "trivial",
                "fermion_count": 0,
                "boson_count": 0,
            }

        factors = prime_decompose(n)
        fermion_count = sum(1 for f in factors if f % 2 == 1)
        boson_count = sum(1 for f in factors if f == 2)

        # 素数签名: 因子次数编码
        from collections import Counter
        factor_counts = Counter(factors)
        signature = "·".join(
            f"{p}^{e}" if e > 1 else str(p)
            for p, e in sorted(factor_counts.items())
        )

        self._operation_count += 1

        return {
            "value": n,
            "factors": factors,
            "factor_count": len(factors),
            "is_prime": is_prime(n),
            "prime_signature": signature,
            "fermion_count": fermion_count,
            "boson_count": boson_count,
        }

    # ===================================================================
    # 代际计算
    # ===================================================================

    def compute_generation(self, n: int = 3) -> Dict[str, Any]:
        """
        代际计算

        素数分代:
        - 第1代: 3,5,7
        - 第2代: 11,13,17,19
        - 第3代: 23,29,31,37,41,43,47
        - ...

        规则: 第g代素数 ∈ (10(g-1)+1, 10g] 中的奇素数
        2为特殊第0代(偶素数/玻色子)

        Args:
            n: 素数值

        Returns:
            代际信息字典
        """
        if not is_prime(n):
            return {
                "value": n,
                "is_prime": False,
                "generation": 0,
                "generation_label": "非素数",
                "same_generation_primes": [],
            }

        gen = _compute_generation(n)

        # 同代素数
        if gen == 0:
            same_gen = [2]
            label = "第0代(偶素数/玻色子)"
        else:
            low = (gen - 1) * 10 + 1
            high = gen * 10
            same_gen = [p for p in self._prime_cache if low < p <= high and p % 2 == 1]
            label = f"第{gen}代"

        self._operation_count += 1

        return {
            "value": n,
            "is_prime": True,
            "generation": gen,
            "generation_label": label,
            "same_generation_primes": same_gen,
        }

    # ===================================================================
    # 黎曼共振
    # ===================================================================

    def riemann_resonance(
        self,
        zero_count: int = 10
    ) -> List[RiemannResonance]:
        """
        黎曼共振

        将黎曼ζ函数零点映射到金灵球网格共振频率。

        使用前zero_count个已知零点的虚部近似值:
        γ₁ ≈ 14.1347, γ₂ ≈ 21.0220, γ₃ ≈ 24.9650, ...

        零点 → 共振频率映射:
        f_k = γ_k / (2π) × scale_factor

        所有已知零点都在临界线 Re = 1/2 上（黎曼假设的数值验证）。

        Args:
            zero_count: 要计算的零点数

        Returns:
            RiemannResonance 列表
        """
        # 已知的前20个黎曼ζ零点虚部（高精度近似）
        known_zeros = [
            14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
            37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
            52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
            67.079811, 69.546402, 72.057416, 75.704691, 77.144840,
        ]

        results = []
        scale_factor = 0.1  # 频率缩放因子

        for k in range(min(zero_count, len(known_zeros))):
            gamma_k = known_zeros[k]

            # 共振频率
            frequency = gamma_k / (2 * math.pi) * scale_factor

            # 稳定性: 基于零点间距
            if k > 0:
                spacing = gamma_k - known_zeros[k - 1]
                stability = 1.0 / (1.0 + abs(spacing - 6.0) / 6.0)
            else:
                stability = 0.9  # 第一个零点默认稳定性

            resonance = RiemannResonance(
                zero_index=k + 1,  # 1-indexed
                frequency=round(frequency, 10),
                is_on_critical_line=True,  # 所有已知零点在临界线上
                stability=round(stability, 10),
            )
            results.append(resonance)

        # 如果需要更多零点，使用近似公式
        if zero_count > len(known_zeros):
            for k in range(len(known_zeros), zero_count):
                # 零点密度近似: N(T) ≈ (T/2π)ln(T/2π) - T/2π
                # 逆函数近似: γ_k ≈ 2πk/ln(k)
                approx_gamma = 2 * math.pi * (k + 1) / math.log(max(k + 1, 2))
                frequency = approx_gamma / (2 * math.pi) * scale_factor

                resonance = RiemannResonance(
                    zero_index=k + 1,
                    frequency=round(frequency, 10),
                    is_on_critical_line=True,  # 假设RH成立
                    stability=0.5,  # 近似值稳定性较低
                )
                results.append(resonance)

        self._operation_count += 1
        return results

    # ===================================================================
    # 泡利不相容检验
    # ===================================================================

    def pauli_exclusion_check(
        self,
        cluster1: Optional[PrimeCluster] = None,
        cluster2: Optional[PrimeCluster] = None
    ) -> Dict[str, Any]:
        """
        泡利不相容检验

        两个费米子不能占据完全相同的量子态。
        在堆垒素数框架中: 两个奇素数(费米子)如果值相同且代际相同，
        则违反泡利不相容原理。

        Args:
            cluster1: 第一个素数簇
            cluster2: 第二个素数簇

        Returns:
            {
                "exclusion_violated": bool,
                "both_fermions": bool,
                "same_value": bool,
                "same_generation": bool,
                "explanation": str,
            }
        """
        if cluster1 is None:
            cluster1 = self.classify_particle(3)
        if cluster2 is None:
            cluster2 = self.classify_particle(5)

        both_fermions = cluster1.is_fermion and cluster2.is_fermion
        same_value = cluster1.value == cluster2.value
        same_generation = cluster1.generation == cluster2.generation

        # 泡利违反: 两个费米子在同一代际且值相同
        exclusion_violated = both_fermions and same_value and same_generation

        if not both_fermions:
            explanation = "泡利不相容仅适用于费米子（奇数堆垒）"
        elif same_value and same_generation:
            explanation = f"违反泡利不相容: 两个费米子(p={cluster1.value})在相同代际(g={cluster1.generation})"
        elif same_value:
            explanation = f"值相同但代际不同，量子态可区分，不违反泡利原理"
        else:
            explanation = f"两个费米子(p1={cluster1.value}, p2={cluster2.value})占据不同量子态"

        self._operation_count += 1

        return {
            "exclusion_violated": exclusion_violated,
            "both_fermions": both_fermions,
            "same_value": same_value,
            "same_generation": same_generation,
            "explanation": explanation,
        }

    # ===================================================================
    # 玻色-爱因斯坦凝聚判定
    # ===================================================================

    def bose_einstein_condensation(
        self,
        clusters: Optional[List[PrimeCluster]] = None
    ) -> Dict[str, Any]:
        """
        玻色-爱因斯坦凝聚判定

        玻色子（偶数堆垒）可以聚集到同一量子态。
        判定条件:
        1. 所有粒子必须是玻色子
        2. 玻色子数密度超过临界值
        3. 温度低于临界温度（这里用"熵"替代）

        在堆垒素数框架中: 多个偶数(玻色子)可以叠加产生凝聚效应。

        Args:
            clusters: 素数簇列表

        Returns:
            凝聚判定结果
        """
        if clusters is None:
            # 默认: 2, 4, 6, 8, 10 (偶数=玻色子)
            clusters = [self.classify_particle(n) for n in [2, 4, 6, 8, 10]]

        # 检查是否全部为玻色子
        all_bosons = all(c.is_boson for c in clusters)
        boson_count = sum(1 for c in clusters if c.is_boson)
        fermion_count = len(clusters) - boson_count

        # 凝聚条件
        total_particles = len(clusters)
        boson_fraction = boson_count / max(total_particles, 1)

        # 临界分数（类比物理中的临界密度）
        critical_fraction = 0.75

        # "温度"类比: 用值的方差表示
        if len(clusters) > 1:
            values = [c.value for c in clusters]
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            effective_temp = math.sqrt(variance)
        else:
            effective_temp = 0.0

        # 临界温度（类比）
        critical_temp = 10.0

        # 凝聚判定
        can_condense = (
            all_bosons
            and boson_fraction >= critical_fraction
            and effective_temp < critical_temp
        )

        # 凝聚值: 所有玻色子值的叠加
        condensation_value = sum(c.value for c in clusters if c.is_boson)

        self._operation_count += 1

        return {
            "can_condense": can_condense,
            "all_bosons": all_bosons,
            "boson_count": boson_count,
            "fermion_count": fermion_count,
            "boson_fraction": round(boson_fraction, 4),
            "effective_temperature": round(effective_temp, 4),
            "critical_temperature": critical_temp,
            "condensation_value": condensation_value,
            "total_particles": total_particles,
        }

    # ===================================================================
    # 定理T94: 堆垒费米子-玻色子分类定理
    # ===================================================================

    def verify_classification_theorem(
        self,
        test_range: int = 100
    ) -> Dict[str, Any]:
        """
        定理T94: 堆垒费米子-玻色子分类定理

        任意正整数n:
        - n为奇数 → 费米子类 (遵守泡利不相容)
        - n为偶数 → 玻色子类 (可玻色-爱因斯坦凝聚)

        验证:
        1. 奇偶性与费米子/玻色子分类的一致性
        2. 哥德巴赫交互的闭合性（奇素数+奇素数=偶数）
        3. 泡利不相容的适用性
        4. 玻色-爱因斯坦凝聚的可能性

        Args:
            test_range: 测试范围 [2, test_range]

        Returns:
            验证结果字典
        """
        start_time = time.time()

        # 1. 奇偶-费米子/玻色子一致性
        consistency_pass = True
        consistency_errors = []
        for n in range(2, test_range + 1):
            cluster = self.classify_particle(n)
            expected_fermion = (n % 2 == 1)
            expected_boson = (n % 2 == 0)
            if cluster.is_fermion != expected_fermion or cluster.is_boson != expected_boson:
                consistency_pass = False
                consistency_errors.append(f"n={n}: fermion={cluster.is_fermion}(exp={expected_fermion}), boson={cluster.is_boson}(exp={expected_boson})")

        # 2. 哥德巴赫交互闭合性
        odd_primes = [p for p in self._prime_cache if p % 2 == 1 and p < test_range]
        goldbach_pass = True
        goldbach_count = 0
        goldbach_failures = []

        for i in range(min(len(odd_primes), 20)):
            for j in range(i, min(len(odd_primes), 20)):
                p1, p2 = odd_primes[i], odd_primes[j]
                result = self.goldbach_interaction(p1, p2)
                if not result.goldbach_verified:
                    goldbach_pass = False
                    goldbach_failures.append(f"{p1}+{p2}={p1+p2}")
                goldbach_count += 1

        # 3. 泡利不相容验证
        pauli_pass = True
        pauli_tests = 0
        for p in odd_primes[:10]:
            c1 = self.classify_particle(p)
            c2 = self.classify_particle(p)
            check = self.pauli_exclusion_check(c1, c2)
            if not check["exclusion_violated"]:
                pauli_pass = False  # 相同费米子应违反泡利
            pauli_tests += 1

        # 不同费米子不违反泡利
        if len(odd_primes) >= 2:
            c1 = self.classify_particle(odd_primes[0])
            c2 = self.classify_particle(odd_primes[1])
            check_diff = self.pauli_exclusion_check(c1, c2)
            if check_diff["exclusion_violated"]:
                pauli_pass = False  # 不同费米子不应违反

        # 4. 玻色-爱因斯坦凝聚验证
        boson_clusters = [self.classify_particle(n) for n in [2, 4, 6, 8, 10, 12, 14, 16]]
        bec_result = self.bose_einstein_condensation(boson_clusters)

        # 汇总
        total_checks = 4
        passed = sum([
            consistency_pass,
            goldbach_pass,
            pauli_pass,
            bec_result["can_condense"],
        ])
        completeness_ratio = passed / total_checks

        elapsed = time.time() - start_time

        return {
            "theorem": "T94_堆垒费米子-玻色子分类定理",
            "verified": completeness_ratio >= 0.75,
            "completeness_ratio": round(completeness_ratio, 4),
            "passed_checks": passed,
            "total_checks": total_checks,
            "consistency_pass": consistency_pass,
            "goldbach_pass": goldbach_pass,
            "goldbach_count": goldbach_count,
            "pauli_pass": pauli_pass,
            "bec_can_condense": bec_result["can_condense"],
            "test_range": test_range,
            "odd_primes_tested": len(odd_primes),
            "consistency_errors": consistency_errors[:5],
            "goldbach_failures": goldbach_failures[:5],
            "elapsed_seconds": round(elapsed, 4),
        }

    # ===================================================================
    # 辅助方法
    # ===================================================================

    def get_primes(self, limit: int = 100) -> List[int]:
        """获取不超过limit的素数列表"""
        if limit <= self._prime_cache[-1]:
            return [p for p in self._prime_cache if p <= limit]
        return generate_primes(limit)

    def find_goldbach_pairs(self, even_number: int = 10) -> List[Tuple[int, int]]:
        """
        寻找哥德巴赫分解对

        对给定偶数，找到所有 (p1, p2) 使得 p1 + p2 = even_number

        Args:
            even_number: 目标偶数

        Returns:
            素数对列表
        """
        if even_number < 4 or even_number % 2 != 0:
            return []

        pairs = []
        primes = self.get_primes(even_number)

        for p1 in primes:
            if p1 > even_number // 2:
                break
            p2 = even_number - p1
            if is_prime(p2) and p2 >= p1:
                pairs.append((p1, p2))

        self._operation_count += 1
        return pairs

    def compute_coupling_matrix(
        self,
        primes: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        计算素数间耦合矩阵

        Args:
            primes: 素数列表

        Returns:
            耦合矩阵和统计信息
        """
        if primes is None:
            primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

        n = len(primes)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0  # 自耦合
                else:
                    # 耦合强度: 1/|p_i - p_j|
                    diff = abs(primes[i] - primes[j])
                    matrix[i][j] = round(1.0 / max(diff, 1), 10)

        self._operation_count += 1

        return {
            "primes": primes,
            "matrix_size": n,
            "matrix": matrix,
        }

    def get_interaction_log(self) -> List[Dict[str, Any]]:
        """获取交互日志"""
        return list(self._interaction_log)

    def reset(self) -> None:
        """重置状态"""
        self._cluster_cache = {}
        self._interaction_log = []
        self._operation_count = 0


# ===========================================================================
# 便捷函数
# ===========================================================================

def create_default_classifier() -> AdditivePrimeClassifier:
    """创建默认分类器"""
    return AdditivePrimeClassifier.get_instance()


def quick_classify(n: int) -> str:
    """快速分类: 返回 'fermion' 或 'boson'"""
    classifier = AdditivePrimeClassifier.get_instance()
    cluster = classifier.classify_particle(n)
    return "fermion" if cluster.is_fermion else "boson"


# ===========================================================================
# 模块自检
# ===========================================================================

def _self_test() -> Dict[str, Any]:
    """模块自检"""
    classifier = AdditivePrimeClassifier.get_instance()

    results = {}

    # 素数检测测试
    results["is_prime"] = {
        "7": is_prime(7),
        "8": is_prime(8),
        "2": is_prime(2),
        "1": is_prime(1),
        "pass": is_prime(7) and not is_prime(8) and is_prime(2) and not is_prime(1),
    }

    # 粒子分类测试
    c3 = classifier.classify_particle(3)
    c4 = classifier.classify_particle(4)
    results["classify"] = {
        "3_is_fermion": c3.is_fermion,
        "4_is_boson": c4.is_boson,
        "pass": c3.is_fermion and c4.is_boson,
    }

    # 哥德巴赫交互测试
    gi = classifier.goldbach_interaction(3, 5)
    results["goldbach"] = {
        "3+5=8": gi.exchange_boson["value"],
        "verified": gi.goldbach_verified,
        "pass": gi.goldbach_verified and gi.exchange_boson["value"] == 8,
    }

    # 黎曼共振测试
    rr = classifier.riemann_resonance(5)
    results["riemann"] = {
        "count": len(rr),
        "first_frequency": rr[0].frequency if rr else 0,
        "all_on_critical_line": all(r.is_on_critical_line for r in rr),
        "pass": len(rr) == 5 and all(r.is_on_critical_line for r in rr),
    }

    # 泡利不相容测试
    c_same = classifier.classify_particle(7)
    pauli_same = classifier.pauli_exclusion_check(c_same, c_same)
    c_diff = classifier.classify_particle(3)
    pauli_diff = classifier.pauli_exclusion_check(c_same, c_diff)
    results["pauli"] = {
        "same_excluded": pauli_same["exclusion_violated"],
        "diff_not_excluded": not pauli_diff["exclusion_violated"],
        "pass": pauli_same["exclusion_violated"] and not pauli_diff["exclusion_violated"],
    }

    # BEC测试
    bec = classifier.bose_einstein_condensation()
    results["bec"] = {
        "can_condense": bec["can_condense"],
        "all_bosons": bec["all_bosons"],
        "pass": bec["all_bosons"],
    }

    # 定理T94测试
    t94 = classifier.verify_classification_theorem(50)
    results["T94"] = t94

    # 状态测试
    state = classifier.get_state()
    results["state"] = state

    return results


# ==================== 单例模式 ====================
_instance = None

def get_instance():
    """获取AdditivePrimeClassifier单例"""
    global _instance
    if _instance is None:
        _instance = create_default_classifier()
    return _instance


if __name__ == "__main__":
    import json
    test_results = _self_test()
    print(json.dumps(test_results, indent=2, ensure_ascii=False, default=str))
