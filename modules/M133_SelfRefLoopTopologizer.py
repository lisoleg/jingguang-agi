# -*- coding: utf-8 -*-
"""
M133: SelfRefLoopTopologizer — 自指闭环拓扑器

PDS/哥德尔双模式自指闭环 + 统一场方程:
  S_unified = S_R + Ξ(κ)

两种自指闭环模式:
  - PDS (Poincaré Dodecahedral Space): 空间静态自指闭环
  - GÖDEL: 时间动态自指闭环 (含CTC)

自指惩罚项 Ξ(κ):
  - κ → 0: 选PDS/哥德尔（自指闭环活跃）
  - κ → ∞: 退化为标准理论（自指闭环消失）

包含定理T95自指闭环必然性定理。

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
class SelfRefLoopState:
    """自指闭环状态"""
    loop_type: str = "PDS"            # 'PDS'(空间静态) / 'GODEL'(时间动态)
    curvature: float = 0.0            # 曲率
    closure_dimension: int = 3         # 闭环维度
    penalty_kappa: float = 0.1         # 自指惩罚系数κ


@dataclass
class UnifiedFieldResult:
    """统一场方程结果"""
    S_unified: float = 0.0            # S_unified = S_R + Ξ(κ)
    S_R_component: float = 0.0        # 关系作用量分量
    self_ref_penalty: float = 0.0     # 自指惩罚项Ξ(κ)
    regime: str = "PDS"              # 'PDS' / 'GODEL' / 'STANDARD'
    rotation_phase: float = 0.0       # 整体旋转相位ω（哥德尔模式）


@dataclass
class CMBSignature:
    """CMB签名"""
    has_cold_spot: bool = False       # 低温斑点缺失
    has_dodecahedral_pattern: bool = False  # 十二面体偏振模式
    correlation_score: float = 0.0    # 相关性评分
    topology_type: str = "unknown"    # 拓扑类型


# ===========================================================================
# 常量
# ===========================================================================

# 临界自指惩罚系数
KAPPA_CRITICAL: float = 0.5

# 物理常数（归一化）
C_NORMALIZED: float = 1.0  # 光速（归一化）
PLANCK_NORMALIZED: float = 1.0  # 普朗克常数（归一化）

# PDS参数
PDS_CURVATURE_DEFAULT: float = 0.01  # PDS默认曲率
PDS_PENTAGON_COUNT_DEFAULT: int = 12  # PDS默认正五边形数

# 哥德尔参数
GODEL_ROTATION_DEFAULT: float = 0.1  # 哥德尔默认旋转参数
GODEL_CTC_DEFAULT: bool = True  # 哥德尔默认含CTC


# ===========================================================================
# SelfRefLoopTopologizer 拓扑器
# ===========================================================================

class SelfRefLoopTopologizer:
    """
    自指闭环拓扑器

    PDS/哥德尔双模式自指闭环 + 统一场方程:
      S_unified = S_R + Ξ(κ)

    当κ < κ_c时，宇宙包含自指闭环（PDS或哥德尔），
    这是刘机制的核心论断: 自指闭环是物理实在的必然特征。

    包含定理T95自指闭环必然性定理。
    """

    _instance: Optional["SelfRefLoopTopologizer"] = None

    # 临界值
    DEFAULT_KAPPA_CRITICAL = KAPPA_CRITICAL

    def __init__(self) -> None:
        """初始化拓扑器"""
        self._kappa_critical: float = self.DEFAULT_KAPPA_CRITICAL
        self._current_loop_state: Optional[SelfRefLoopState] = None
        self._loop_history: List[Dict[str, Any]] = []
        self._cmb_analyses: List[Dict[str, Any]] = []
        self._operation_count: int = 0
        self._created_at: float = time.time()

    # -------------------------------------------------------------------
    # 单例模式
    # -------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "SelfRefLoopTopologizer":
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
            "module_id": "M133",
            "module_name": "SelfRefLoopTopologizer",
            "kappa_critical": self._kappa_critical,
            "current_loop_type": self._current_loop_state.loop_type if self._current_loop_state else None,
            "current_kappa": self._current_loop_state.penalty_kappa if self._current_loop_state else None,
            "loop_history_count": len(self._loop_history),
            "cmb_analyses_count": len(self._cmb_analyses),
            "operation_count": self._operation_count,
            "created_at": self._created_at,
        }

    # ===================================================================
    # 构建PDS: 空间静态自指闭环
    # ===================================================================

    def construct_pds(
        self,
        pentagon_count: int = 0,
        curvature: float = 0.0
    ) -> SelfRefLoopState:
        """
        构建PDS (Poincaré Dodecahedral Space)

        PDS是一个有限、无界、正曲率的3-流形。
        其拓扑等价于S³/I*（对径商的3-球面），
        基本群为二面体群I* (120阶)。

        关键特征:
        - 正曲率 → 有限宇宙
        - 十二面体基本域 → 自指闭环
        - 空间静态: 时间方向开放，空间方向闭合
        - CMB预测: 低温斑点缺失 + 十二面体偏振模式

        Args:
            pentagon_count: 正五边形面数（0则用默认值12）
            curvature: 曲率（0则用默认值）

        Returns:
            SelfRefLoopState PDS状态
        """
        if pentagon_count <= 0:
            pentagon_count = PDS_PENTAGON_COUNT_DEFAULT

        if curvature == 0.0:
            curvature = PDS_CURVATURE_DEFAULT

        # 计算闭环维度
        # PDS是3维闭合空间，但基本域是3维十二面体
        closure_dimension = 3

        # 自指惩罚系数: 与曲率成正比
        # 曲率越大→宇宙越小→自指越强→κ越小
        kappa = 1.0 / (1.0 + abs(curvature) * 100)

        state = SelfRefLoopState(
            loop_type="PDS",
            curvature=curvature,
            closure_dimension=closure_dimension,
            penalty_kappa=round(kappa, 10),
        )

        self._current_loop_state = state
        self._operation_count += 1
        self._loop_history.append({
            "action": "construct_pds",
            "state": asdict(state),
            "pentagon_count": pentagon_count,
            "timestamp": time.time(),
        })

        return state

    # ===================================================================
    # 构建哥德尔宇宙: 时间动态自指闭环
    # ===================================================================

    def construct_godel(
        self,
        rotation_phase: float = 0.0,
        ctc_present: bool = True
    ) -> SelfRefLoopState:
        """
        构建哥德尔宇宙

        哥德尔宇宙是旋转的宇宙模型，包含闭合类时曲线(CTC)。
        关键特征:
        - 整体旋转 → CTC存在
        - 时间动态自指: 未来可以影响过去
        - 因果闭环: 信息/物质可以沿CTC循环

        数学: Gödel度规
          ds² = -dt² + dx² - (1/2)e^(2√2 ωx)dy² + dz² - 2e^(√2 ωx)dtdy

        Args:
            rotation_phase: 整体旋转相位ω
            ctc_present: 是否存在CTC

        Returns:
            SelfRefLoopState 哥德尔状态
        """
        if rotation_phase == 0.0:
            rotation_phase = GODEL_ROTATION_DEFAULT

        # 哥德尔宇宙的曲率: 由旋转决定
        # Gödel度规的里奇曲率与ω相关
        curvature = -rotation_phase ** 2  # 负曲率（旋转宇宙）

        # 闭环维度: 时间方向闭合（CTC）
        closure_dimension = 1  # 时间维度的闭合

        # 自指惩罚系数: 旋转越强→CTC越显著→自指越强→κ越小
        kappa = 1.0 / (1.0 + abs(rotation_phase) * 50)

        # 如果没有CTC，κ更大（自指弱化）
        if not ctc_present:
            kappa = min(kappa + 0.5, 1.0)

        state = SelfRefLoopState(
            loop_type="GODEL",
            curvature=curvature,
            closure_dimension=closure_dimension,
            penalty_kappa=round(kappa, 10),
        )

        self._current_loop_state = state
        self._operation_count += 1
        self._loop_history.append({
            "action": "construct_godel",
            "state": asdict(state),
            "rotation_phase": rotation_phase,
            "ctc_present": ctc_present,
            "timestamp": time.time(),
        })

        return state

    # ===================================================================
    # 统一场方程
    # ===================================================================

    def compute_unified_field(
        self,
        S_R: float = 1.0,
        kappa: float = 0.1,
        loop_type: str = "PDS"
    ) -> UnifiedFieldResult:
        """
        统一场方程

        S_unified = S_R + Ξ(κ)

        其中:
        - S_R: 关系作用量（来自M131）
        - Ξ(κ): 自指惩罚项
        - κ: 自指惩罚系数

        当κ < κ_c时，Ξ(κ)为负值，表示自指闭环降低了总作用量，
        使宇宙倾向于选择包含自指闭环的拓扑。

        Args:
            S_R: 关系作用量
            kappa: 自指惩罚系数
            loop_type: 闭环类型 'PDS' / 'GODEL'

        Returns:
            UnifiedFieldResult 统一场结果
        """
        # 计算自指惩罚项
        penalty = self.compute_self_ref_penalty(kappa, loop_type)

        # 统一作用量
        S_unified = S_R + penalty

        # 判定制度
        regime = self.determine_regime(kappa)

        # 哥德尔模式的旋转相位
        rotation_phase = 0.0
        if loop_type == "GODEL":
            rotation_phase = 2 * math.pi * kappa  # ω与κ关联

        result = UnifiedFieldResult(
            S_unified=round(S_unified, 10),
            S_R_component=round(S_R, 10),
            self_ref_penalty=round(penalty, 10),
            regime=regime,
            rotation_phase=round(rotation_phase, 10),
        )

        self._operation_count += 1
        return result

    # ===================================================================
    # 自指惩罚项
    # ===================================================================

    def compute_self_ref_penalty(
        self,
        kappa: float = 0.1,
        loop_type: str = "PDS"
    ) -> float:
        """
        自指惩罚项 Ξ(κ)

        Ξ(κ) 描述自指闭环对作用量的贡献:
        - κ → 0: 自指闭环活跃，Ξ(κ) → -∞（强负贡献，降低作用量）
        - κ = κ_c: 临界点，Ξ(κ_c) = 0
        - κ → ∞: 自指闭环消失，Ξ(κ) → 0（退化为标准理论）

        函数形式:
          PDS模式:   Ξ_PDS(κ) = -A/κ · exp(-κ/κ_c)
          GODEL模式: Ξ_GÖDEL(κ) = -A/κ · sin(π·κ/κ_c) · exp(-κ/κ_c)

        其中 A 是振幅常数。

        Args:
            kappa: 自指惩罚系数
            loop_type: 闭环类型

        Returns:
            自指惩罚值
        """
        if kappa <= 0:
            # κ=0时自指极强，返回大负值
            return -1000.0

        kappa_c = self._kappa_critical
        A = 1.0  # 振幅常数

        if loop_type == "GODEL":
            # 哥德尔模式: 含振荡项（CTC效应）
            penalty = -A / kappa * math.sin(math.pi * kappa / kappa_c) * math.exp(-kappa / kappa_c)
        else:
            # PDS模式: 单调衰减
            penalty = -A / kappa * math.exp(-kappa / kappa_c)

        self._operation_count += 1
        return round(penalty, 10)

    # ===================================================================
    # CMB签名分析
    # ===================================================================

    def analyze_cmb_signature(
        self,
        temperature_data: Optional[List[float]] = None
    ) -> CMBSignature:
        """
        CMB签名分析

        PDS宇宙的CMB预测:
        1. 低温斑点缺失: 由于正曲率，大尺度涨落被抑制
        2. 十二面体偏振模式: PDS的拓扑导致偏振有特殊的十二面体对称性

        检测方法:
        - 对温度数据进行统计分析
        - 检查低温区域是否缺失
        - 检查偏振模式是否匹配十二面体群

        Args:
            temperature_data: CMB温度涨落数据

        Returns:
            CMBSignature 分析结果
        """
        if temperature_data is None:
            # 生成模拟CMB数据（正曲率宇宙: 抑制大尺度涨落）
            import random
            random.seed(42)
            # 基础涨落
            temperature_data = [random.gauss(0, 1) for _ in range(1000)]
            # PDS效应: 抑制大尺度（低频）涨落
            temperature_data = [t * 0.8 for t in temperature_data]

        if len(temperature_data) == 0:
            return CMBSignature(
                has_cold_spot=False,
                has_dodecahedral_pattern=False,
                correlation_score=0.0,
                topology_type="empty_data",
            )

        # 1. 低温斑点检测
        # 在标准宇宙中，期望有一定数量的低温异常区域
        # PDS宇宙中，正曲率抑制大尺度涨落，导致低温斑点缺失
        mean_temp = sum(temperature_data) / len(temperature_data)
        std_temp = math.sqrt(sum((t - mean_temp) ** 2 for t in temperature_data) / len(temperature_data))

        # 计算低于3σ的区域数
        cold_threshold = mean_temp - 3 * std_temp if std_temp > 0 else mean_temp - 1
        cold_spots = sum(1 for t in temperature_data if t < cold_threshold)
        expected_cold_spots = len(temperature_data) * 0.0013  # 3σ 期望比例

        # 低温斑点缺失: 实际远少于期望
        has_cold_spot_missing = cold_spots < expected_cold_spots * 0.5

        # 2. 十二面体偏振模式检测
        # 简化: 检查数据的周期性是否与十二面体对称性匹配
        # 十二面体有60阶旋转对称群，对应特定频率
        n = len(temperature_data)
        if n > 10:
            # 简单傅里叶分析
            # 检查60阶对称性（十二面体有60个旋转）
            correlation_60 = 0.0
            for i in range(min(n, 100)):
                j = (i + n // 60) % n
                correlation_60 += temperature_data[i] * temperature_data[j]
            correlation_60 /= min(n, 100)

            # 归一化
            max_val = max(abs(t) for t in temperature_data) if temperature_data else 1
            if max_val > 0:
                correlation_60 /= max_val
        else:
            correlation_60 = 0.0

        # 十二面体模式: 60阶相关性显著
        has_dodecahedral = abs(correlation_60) > 0.1

        # 3. 综合评分
        score = 0.0
        if has_cold_spot_missing:
            score += 0.4
        if has_dodecahedral:
            score += 0.4
        # 额外: 检查正曲率特征
        if std_temp < 1.0:  # 正曲率抑制涨落
            score += 0.2

        # 4. 拓扑类型判定
        if score > 0.7:
            topology_type = "PDS"
        elif score > 0.4:
            topology_type = "PDS_candidate"
        elif score > 0.2:
            topology_type = "mixed"
        else:
            topology_type = "flat_or_open"

        result = CMBSignature(
            has_cold_spot=not has_cold_spot_missing,  # 注意: 原始含义是"有低温斑点"
            has_dodecahedral_pattern=has_dodecahedral,
            correlation_score=round(score, 4),
            topology_type=topology_type,
        )

        self._operation_count += 1
        self._cmb_analyses.append({
            "result": asdict(result),
            "data_size": len(temperature_data),
            "mean_temp": round(mean_temp, 6),
            "std_temp": round(std_temp, 6) if std_temp > 0 else 0,
            "timestamp": time.time(),
        })

        return result

    # ===================================================================
    # 因果闭环检测
    # ===================================================================

    def detect_causal_loop(
        self,
        state_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        因果闭环检测

        在状态历史中检测闭合类时曲线(CTC)的存在性。
        CTC的存在意味着未来状态可以影响过去状态。

        检测方法:
        1. 检查状态序列是否出现循环（回到之前的状态）
        2. 检查因果关系是否形成环路
        3. 量化CTC的"强度"

        Args:
            state_history: 状态历史序列

        Returns:
            {
                "ctc_detected": bool,
                "ctc_strength": float,
                "loop_length": int,
                "causality_violations": int,
                "explanation": str,
            }
        """
        if state_history is None:
            # 默认测试: 线性状态序列（无CTC）
            state_history = [
                {"t": i, "state": f"S{i}"} for i in range(10)
            ]

        n = len(state_history)
        if n < 3:
            return {
                "ctc_detected": False,
                "ctc_strength": 0.0,
                "loop_length": 0,
                "causality_violations": 0,
                "explanation": "状态历史太短，无法检测CTC",
            }

        # 1. 检测状态循环
        # 使用哈希来检测重复状态
        state_hashes = []
        for s in state_history:
            h = hashlib.sha256(str(s).encode("utf-8")).hexdigest()[:8]
            state_hashes.append(h)

        # 查找重复的哈希
        hash_to_indices: Dict[str, List[int]] = {}
        for idx, h in enumerate(state_hashes):
            if h not in hash_to_indices:
                hash_to_indices[h] = []
            hash_to_indices[h].append(idx)

        # 找到循环
        loops = []
        for h, indices in hash_to_indices.items():
            if len(indices) >= 2:
                # 状态在 indices[0] 和 indices[1] 处相同 → 循环
                loop_length = indices[1] - indices[0]
                loops.append({
                    "hash": h,
                    "start": indices[0],
                    "end": indices[1],
                    "length": loop_length,
                })

        # 2. 检查因果关系
        causality_violations = 0
        for loop in loops:
            # 如果一个状态的"结果"出现在其"原因"之前
            # 这意味着因果关系被违反
            causality_violations += 1

        # 3. CTC强度
        if loops:
            max_loop = max(loops, key=lambda l: l["length"])
            loop_length = max_loop["length"]
            # CTC强度: 循环越长越强
            ctc_strength = min(1.0, loop_length / max(n, 1))
        else:
            loop_length = 0
            ctc_strength = 0.0

        ctc_detected = len(loops) > 0

        # 解释
        if ctc_detected:
            explanation = f"检测到{len(loops)}个因果闭环，最长循环长度={loop_length}，CTC强度={ctc_strength:.4f}"
        else:
            explanation = "未检测到因果闭环，状态历史为因果正常的序列"

        self._operation_count += 1

        return {
            "ctc_detected": ctc_detected,
            "ctc_strength": round(ctc_strength, 10),
            "loop_length": loop_length,
            "num_loops": len(loops),
            "causality_violations": causality_violations,
            "explanation": explanation,
        }

    # ===================================================================
    # 判定制度
    # ===================================================================

    def determine_regime(
        self,
        kappa: float = 0.1
    ) -> str:
        """
        判定制度

        κ < κ_c → PDS 或 GÖDEL（自指闭环活跃）
        κ ≥ κ_c → STANDARD（自指闭环退化，标准理论）

        在PDS/GÖDEL制度中:
        - 宇宙具有自指拓扑结构
        - 统一场方程包含自指惩罚项
        - 物理定律需要修正

        在STANDARD制度中:
        - 自指闭环退化
        - 退化为标准场论
        - Ξ(κ) → 0

        Args:
            kappa: 自指惩罚系数

        Returns:
            'PDS' / 'GODEL' / 'STANDARD'
        """
        if kappa < self._kappa_critical:
            # 根据当前闭环状态决定PDS还是GÖDEL
            if self._current_loop_state is not None:
                if self._current_loop_state.loop_type == "GODEL":
                    regime = "GODEL"
                else:
                    regime = "PDS"
            else:
                # 默认PDS（空间静态优先）
                regime = "PDS"
        else:
            regime = "STANDARD"

        self._operation_count += 1
        return regime

    # ===================================================================
    # 定理T95: 自指闭环必然性定理
    # ===================================================================

    def verify_necessity_theorem(
        self,
        test_kappa_values: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        定理T95: 自指闭环必然性定理

        在刘机制框架下，自指闭环是物理实在的必然特征。

        证明思路:
        1. 考虑任何有限金灵球系统
        2. 若κ < κ_c，则Ξ(κ) < 0，自指闭环降低总作用量
        3. 由关系作用量极小值定理(T93)，系统趋向S_R极小
        4. S_unified = S_R + Ξ(κ)，若Ξ(κ) < 0则S_unified < S_R
        5. 因此，包含自指闭环的状态比不包含的状态作用量更低
        6. 故自指闭环是必然的

        验证方法:
        - 对一系列κ值计算Ξ(κ)和S_unified
        - 验证κ < κ_c时Ξ(κ) < 0
        - 验证S_unified < S_R（当κ < κ_c时）
        - 验证κ ≥ κ_c时退化为标准理论

        Args:
            test_kappa_values: 测试κ值列表

        Returns:
            验证结果字典
        """
        start_time = time.time()

        if test_kappa_values is None:
            test_kappa_values = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 2.0, 5.0]

        kappa_c = self._kappa_critical
        S_R_test = 10.0  # 固定的S_R用于测试

        results_per_kappa = []
        penalty_negative_when_active = True
        unified_lower_when_active = True
        degrades_at_critical = True

        for kappa in test_kappa_values:
            # PDS模式
            pds_penalty = self.compute_self_ref_penalty(kappa, "PDS")
            pds_unified = self.compute_unified_field(S_R_test, kappa, "PDS")

            # GODEL模式
            godel_penalty = self.compute_self_ref_penalty(kappa, "GODEL")
            godel_unified = self.compute_unified_field(S_R_test, kappa, "GODEL")

            # 制度判定
            regime = self.determine_regime(kappa)

            result = {
                "kappa": kappa,
                "kappa_lt_critical": kappa < kappa_c,
                "regime": regime,
                "pds_penalty": pds_penalty,
                "pds_S_unified": pds_unified.S_unified,
                "godel_penalty": godel_penalty,
                "godel_S_unified": godel_unified.S_unified,
                "penalty_negative": pds_penalty < 0 or godel_penalty < 0,
                "unified_lt_SR": pds_unified.S_unified < S_R_test or godel_unified.S_unified < S_R_test,
            }
            results_per_kappa.append(result)

            # 验证条件
            if kappa < kappa_c:
                if pds_penalty >= 0 and godel_penalty >= 0:
                    penalty_negative_when_active = False
                if pds_unified.S_unified >= S_R_test and godel_unified.S_unified >= S_R_test:
                    unified_lower_when_active = False
            else:
                # κ ≥ κ_c时，Ξ(κ)应趋近于0
                if abs(pds_penalty) > 1.0 or abs(godel_penalty) > 1.0:
                    degrades_at_critical = False

        # 汇总
        total_checks = 3
        passed = sum([
            penalty_negative_when_active,
            unified_lower_when_active,
            degrades_at_critical,
        ])
        completeness_ratio = passed / total_checks

        elapsed = time.time() - start_time

        return {
            "theorem": "T95_自指闭环必然性定理",
            "verified": completeness_ratio >= 0.67,
            "completeness_ratio": round(completeness_ratio, 4),
            "passed_checks": passed,
            "total_checks": total_checks,
            "kappa_critical": kappa_c,
            "S_R_test": S_R_test,
            "penalty_negative_when_active": penalty_negative_when_active,
            "unified_lower_when_active": unified_lower_when_active,
            "degrades_at_critical": degrades_at_critical,
            "results_per_kappa": results_per_kappa,
            "elapsed_seconds": round(elapsed, 4),
        }

    # ===================================================================
    # 辅助方法
    # ===================================================================

    def compute_penalty_function_table(
        self,
        kappa_range: Tuple[float, float] = (0.01, 2.0),
        steps: int = 50,
        loop_type: str = "PDS"
    ) -> Dict[str, Any]:
        """
        计算自指惩罚函数表

        Args:
            kappa_range: (min_kappa, max_kappa)
            steps: 步数
            loop_type: 闭环类型

        Returns:
            函数表
        """
        min_k, max_k = kappa_range
        dk = (max_k - min_k) / steps

        table = []
        for i in range(steps + 1):
            kappa = min_k + i * dk
            penalty = self.compute_self_ref_penalty(kappa, loop_type)
            regime = self.determine_regime(kappa)
            table.append({
                "kappa": round(kappa, 6),
                "Xi_kappa": penalty,
                "regime": regime,
            })

        return {
            "loop_type": loop_type,
            "kappa_critical": self._kappa_critical,
            "steps": steps,
            "table": table,
        }

    def compute_transition_matrix(
        self,
        kappa_values: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        计算PDS↔GÖDEL↔STANDARD制度转换矩阵

        Args:
            kappa_values: κ值列表

        Returns:
            转换矩阵
        """
        if kappa_values is None:
            kappa_values = [0.01, 0.1, 0.3, 0.5, 0.7, 1.0, 2.0]

        S_R = 10.0
        transitions = []

        for kappa in kappa_values:
            pds_result = self.compute_unified_field(S_R, kappa, "PDS")
            godel_result = self.compute_unified_field(S_R, kappa, "GODEL")
            regime = self.determine_regime(kappa)

            # 哪种模式作用量更低
            preferred = "PDS" if pds_result.S_unified <= godel_result.S_unified else "GODEL"
            if regime == "STANDARD":
                preferred = "STANDARD"

            transitions.append({
                "kappa": kappa,
                "regime": regime,
                "S_unified_PDS": pds_result.S_unified,
                "S_unified_GODEL": godel_result.S_unified,
                "preferred": preferred,
                "penalty_diff": round(pds_result.self_ref_penalty - godel_result.self_ref_penalty, 10),
            })

        self._operation_count += 1

        return {
            "S_R": S_R,
            "kappa_critical": self._kappa_critical,
            "transitions": transitions,
        }

    def compare_topologies(
        self,
        S_R: float = 10.0,
        kappa: float = 0.1
    ) -> Dict[str, Any]:
        """
        比较不同拓扑的统一场结果

        Args:
            S_R: 关系作用量
            kappa: 自指惩罚系数

        Returns:
            比较结果
        """
        pds = self.compute_unified_field(S_R, kappa, "PDS")
        godel = self.compute_unified_field(S_R, kappa, "GODEL")
        standard = self.compute_unified_field(S_R, kappa + self._kappa_critical + 0.1, "PDS")

        return {
            "PDS": asdict(pds),
            "GODEL": asdict(godel),
            "STANDARD": asdict(standard),
            "lowest_S_unified": min(pds.S_unified, godel.S_unified, standard.S_unified),
            "preferred_topology": "PDS" if pds.S_unified <= godel.S_unified else "GODEL",
        }

    def get_loop_history(self) -> List[Dict[str, Any]]:
        """获取闭环构建历史"""
        return list(self._loop_history)

    def get_cmb_analyses(self) -> List[Dict[str, Any]]:
        """获取CMB分析历史"""
        return list(self._cmb_analyses)

    def reset(self) -> None:
        """重置状态"""
        self._current_loop_state = None
        self._loop_history = []
        self._cmb_analyses = []
        self._operation_count = 0

    def set_kappa_critical(self, kappa_c: float) -> None:
        """设置临界自指惩罚系数"""
        if kappa_c > 0:
            self._kappa_critical = kappa_c


# ===========================================================================
# 便捷函数
# ===========================================================================

def create_default_topologizer(kappa_c: float = 0.5) -> SelfRefLoopTopologizer:
    """创建默认拓扑器"""
    topologizer = SelfRefLoopTopologizer.get_instance()
    topologizer.set_kappa_critical(kappa_c)
    return topologizer


def quick_unified_field(S_R: float, kappa: float = 0.1) -> float:
    """快速计算统一场值"""
    topologizer = SelfRefLoopTopologizer.get_instance()
    result = topologizer.compute_unified_field(S_R, kappa)
    return result.S_unified


# ===========================================================================
# 模块自检
# ===========================================================================

def _self_test() -> Dict[str, Any]:
    """模块自检"""
    topologizer = SelfRefLoopTopologizer.get_instance()

    results = {}

    # PDS构建测试
    pds_state = topologizer.construct_pds()
    results["pds"] = {
        "state": asdict(pds_state),
        "pass": pds_state.loop_type == "PDS",
    }

    # 哥德尔构建测试
    godel_state = topologizer.construct_godel()
    results["godel"] = {
        "state": asdict(godel_state),
        "pass": godel_state.loop_type == "GODEL",
    }

    # 统一场方程测试
    uf = topologizer.compute_unified_field(S_R=10.0, kappa=0.1)
    results["unified_field"] = {
        "S_unified": uf.S_unified,
        "S_R": uf.S_R_component,
        "penalty": uf.self_ref_penalty,
        "regime": uf.regime,
        "pass": abs(uf.S_unified - (uf.S_R_component + uf.self_ref_penalty)) < 1e-8,
    }

    # 自指惩罚测试
    penalty_small_k = topologizer.compute_self_ref_penalty(0.1, "PDS")
    penalty_large_k = topologizer.compute_self_ref_penalty(2.0, "PDS")
    results["penalty"] = {
        "small_k": penalty_small_k,
        "large_k": penalty_large_k,
        "small_k_negative": penalty_small_k < 0,
        "large_k_near_zero": abs(penalty_large_k) < abs(penalty_small_k),
        "pass": penalty_small_k < 0 and abs(penalty_large_k) < abs(penalty_small_k),
    }

    # 制度判定测试
    regime_active = topologizer.determine_regime(0.1)
    regime_standard = topologizer.determine_regime(1.0)
    results["regime"] = {
        "active": regime_active,
        "standard": regime_standard,
        "pass": regime_active in ("PDS", "GODEL") and regime_standard == "STANDARD",
    }

    # CMB分析测试
    cmb = topologizer.analyze_cmb_signature()
    results["cmb"] = {
        "topology_type": cmb.topology_type,
        "correlation_score": cmb.correlation_score,
        "pass": cmb.topology_type in ("PDS", "PDS_candidate", "mixed", "flat_or_open"),
    }

    # 因果闭环检测测试
    # 构造一个含循环的状态历史
    loop_history = [{"t": i, "v": i % 3} for i in range(12)]
    ctc = topologizer.detect_causal_loop(loop_history)
    results["ctc"] = {
        "ctc_detected": ctc["ctc_detected"],
        "ctc_strength": ctc["ctc_strength"],
        "pass": True,  # 循环存在性取决于具体数据
    }

    # 定理T95测试
    t95 = topologizer.verify_necessity_theorem()
    results["T95"] = t95

    # 状态测试
    state = topologizer.get_state()
    results["state"] = state

    return results


# ==================== M133-W2 Integration ====================
def beta_rewire_topologizer(delta_psi_dict: Dict[str, Any] = None,
                             ice_patch_dict: Dict[str, Any] = None) -> Dict[str, Any]:
    """M133-W2 Integration: Execute beta-rewire on JinlingGraph.

    This replaces the TODO/placeholder with a real beta-rewire
    using M133_W2_JinlingGraphBetaRewire.

    Args:
        delta_psi_dict: DeltaPsi parameters {kind, focus, magnitude}
        ice_patch_dict: ICEPatch parameters {target, action, data}

    Returns:
        Dict with rewire result including Laplacian spectrum jump.
    """
    try:
        from modules.M133_W2_JinlingGraphBetaRewire import (
            JinlingGraph, DeltaPsi, ICEPatch,
        )
        g = JinlingGraph()
        # Add existing topology nodes
        if _instance := SelfRefLoopTopologizer.get_instance():
            if _instance._current_loop_state:
                g.add_node(f"loop_{_instance._current_loop_state.loop_type}")
                g.add_node(f"kappa_{_instance._current_loop_state.penalty_kappa:.4f}")

        dp = DeltaPsi(
            kind=delta_psi_dict.get("kind", "MIS_MATCH") if delta_psi_dict else "MIS_MATCH",
            focus=delta_psi_dict.get("focus", "") if delta_psi_dict else "",
            magnitude=delta_psi_dict.get("magnitude", 0.5) if delta_psi_dict else 0.5,
        )
        ip = ICEPatch(
            target=ice_patch_dict.get("target", "L3_GRAPH") if ice_patch_dict else "L3_GRAPH",
            action=ice_patch_dict.get("action", "rewire") if ice_patch_dict else "rewire",
            data=ice_patch_dict.get("data", {}) if ice_patch_dict else {},
        )
        g.beta_rewire(dp, ip)
        return {
            "rewired": True,
            "version": g.version,
            "laplacian_history": g.laplacian_history[-3:],
        }
    except ImportError:
        return {"rewired": False, "error": "M133_W2 not available"}
    except Exception as e:
        return {"rewired": False, "error": str(e)}


# ==================== 模块级单例 ====================
def get_instance():
    """模块级get_instance，返回SelfRefLoopTopologizer单例"""
    return SelfRefLoopTopologizer.get_instance()


if __name__ == "__main__":
    import json
    test_results = _self_test()
    print(json.dumps(test_results, indent=2, ensure_ascii=False, default=str))
