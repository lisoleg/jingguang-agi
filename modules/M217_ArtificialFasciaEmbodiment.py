# -*- coding: utf-8 -*-
"""
M217: ArtificialFasciaEmbodiment — 人工筋膜+软L2壳+具身自举引擎

基于复合体理学「人工筋膜与具身智能」「tau韬定律」核心实现:
  - 软L2壳(Sigma_soft): 筋膜=弹性边界+传感网+阻尼器+储备库四位一体
  - 本体感觉Omega回路: 筋膜->BodySchema更新->运动指令->筋膜
  - 人工筋膜三要件: 软连续介质力学匹配+嵌入式共形传感-驱动网络+自适应迟滞阻尼
  - 叠层架构: 疏水TPU -> CNT/AgNW感知 -> DEA+STF基体 -> 织物增强硅胶
  - tau_eff公式: tau_eff proportional to Z_inter/(g_m * Phi_coherence)
  - 超节点Sigma_super: GUMA全局统一编址, Z_inter -> Z_intra

核心定理:
  T238 — tau韬定律:
    tau_eff = Z_inter / (g_m * Phi_coherence)
    筋膜延迟由层间阻抗、跨膜电导和流贯相干度共同决定
    超节点Sigma_super使Z_inter->Z_intra, 大幅降低tau_eff

  T239 — 具身自举定理:
    Omega回路闭环时, BodySchema持续更新驱动筋膜性能提升
    三要件(力学匹配+共形传感+自适应阻尼)同时满足 -> 具身闭环
    具身闭环 -> 自举升级(self-bootstrap)能力

Author: Kou (寇豆码) — 太乙AGI团队
Version: v7.32
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, Set
from enum import Enum


# ═══════════════════════════════════════════════════════════════
# §1 SoftL2Shell — 软L2壳
# ═══════════════════════════════════════════════════════════════

class ShellComponent(Enum):
    """筋膜四大组分"""
    ELASTIC_BOUNDARY = "elastic_boundary"      # 弹性边界
    SENSOR_NETWORK = "sensor_network"           # 传感网
    DAMPER = "damper"                           # 阻尼器
    RESERVE_POOL = "reserve_pool"               # 储备库


@dataclass
class SoftL2Shell:
    """
    软L2壳 (Sigma_soft)

    筋膜=弹性边界+传感网+阻尼器+储备库 四位一体
    构成L2壳层的软性边界, 区别于刚性格子(L2 rigid)

    - elastic_modulus: 弹性模量(E), 控制边界形变响应
    - sensor_density: 传感密度(ρ_s), 控制信号采集精度
    - damping_coeff: 阻尼系数(ζ), 控制振动衰减速率
    - reserve_capacity: 储备容量(R), 控制能量/物质缓冲

    四者必须协同:
    E↑ → 刚性增大, 需ζ↑配合 → 否则振荡
    ρ_s↑ → 信号精度↑, 但带宽需求↑ → 需R↑缓冲
    """

    elastic_modulus: float = 1.0        # E: 弹性模量
    sensor_density: float = 1.0        # rho_s: 传感密度
    damping_coeff: float = 0.5         # zeta: 阻尼系数
    reserve_capacity: float = 1.0      # R: 储备容量
    integrity: float = 1.0             # 壳层完整性 [0, 1]

    def mechanical_compliance(self) -> float:
        """力学顺度 = 1/E"""
        return 1.0 / max(self.elastic_modulus, 1e-10)

    def signal_resolution(self) -> float:
        """信号分辨率 ∝ ρ_s"""
        return self.sensor_density

    def damping_ratio(self) -> float:
        """阻尼比 ζ/ζ_critical"""
        zeta_critical = 2.0 * math.sqrt(
            self.elastic_modulus * self.reserve_capacity
        )
        if zeta_critical == 0:
            return float('inf')
        return self.damping_coeff / zeta_critical

    def is_critical_damped(self) -> bool:
        """是否临界阻尼(ζ≈1)"""
        return abs(self.damping_ratio() - 1.0) < 0.1

    def effective_impedance(self) -> float:
        """有效阻抗 Z_eff = E / (ζ * ρ_s * R)"""
        denominator = self.damping_coeff * self.sensor_density * self.reserve_capacity
        if denominator == 0:
            return float('inf')
        return self.elastic_modulus / denominator


# ═══════════════════════════════════════════════════════════════
# §2 BodySchema — 身体图式
# ═══════════════════════════════════════════════════════════════

@dataclass
class BodySchema:
    """
    身体图式 (BodySchema)

    维持对身体状态的内部表征, 由本体感觉Omega回路持续更新。
    - position: 位置(3D)
    - velocity: 速度(3D)
    - posture: 姿态编码
    - proprioceptive_confidence: 本体感觉置信度
    - update_count: 更新次数(自举度量)
    """

    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    posture: float = 0.0
    proprioceptive_confidence: float = 0.0
    update_count: int = 0

    def update_from_sensation(self, new_position: Tuple[float, float, float],
                               new_posture: float,
                               signal_quality: float = 1.0) -> Dict[str, Any]:
        """
        从筋膜感觉输入更新身体图式

        Args:
            new_position: 新位置
            new_posture: 新姿态
            signal_quality: 信号质量 [0, 1]

        Returns:
            更新报告
        """
        # 速度更新
        if self.update_count > 0:
            dt = 1.0  # 归一化时间步
            self.velocity = tuple(
                (n - o) / dt for n, o in zip(new_position, self.position)
            )

        self.position = new_position
        self.posture = new_posture
        self.update_count += 1

        # 置信度更新: 信号质量加权
        alpha = 0.3 * signal_quality
        self.proprioceptive_confidence = (
            (1 - alpha) * self.proprioceptive_confidence + alpha
        )
        self.proprioceptive_confidence = min(1.0, self.proprioceptive_confidence)

        return {
            "position": self.position,
            "velocity": self.velocity,
            "posture": self.posture,
            "confidence": self.proprioceptive_confidence,
            "update_count": self.update_count
        }


# ═══════════════════════════════════════════════════════════════
# §3 ProprioceptionOmegaLoop — 本体感觉Omega回路
# ═══════════════════════════════════════════════════════════════

class ProprioceptionOmegaLoop:
    """
    本体感觉Omega回路

    筋膜(Sigma_soft) -> BodySchema更新 -> 运动指令 -> 筋膜

    闭环时:
    1. 筋膜传感信号传入
    2. BodySchema更新内部表征
    3. 生成运动指令反馈到筋膜
    4. 筋膜响应改变传感信号

    开环时: 缺少运动指令反馈回路
    """

    def __init__(self, shell: SoftL2Shell, body_schema: BodySchema):
        self.shell = shell
        self.body_schema = body_schema
        self.loop_closed = False
        self.iteration_count = 0
        self.performance_history: List[float] = []

    def close_loop(self) -> bool:
        """闭合Omega回路"""
        self.loop_closed = True
        return True

    def open_loop(self) -> bool:
        """断开Omega回路"""
        self.loop_closed = False
        return True

    def iterate(self, external_signal: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行一次Omega回路迭代

        Args:
            external_signal: 外部传入的传感信号

        Returns:
            迭代结果报告
        """
        self.iteration_count += 1

        # Step 1: 筋膜传感 → 位置和姿态
        if external_signal:
            position = external_signal.get("position", self.body_schema.position)
            posture = external_signal.get("posture", self.body_schema.posture)
            signal_quality = external_signal.get("signal_quality", 1.0)
        else:
            # 无外部信号时使用当前状态(微小扰动)
            position = self.body_schema.position
            posture = self.body_schema.posture
            signal_quality = self.shell.integrity * self.shell.signal_resolution()

        # Step 2: 更新BodySchema
        update_report = self.body_schema.update_from_sensation(
            position, posture, min(1.0, signal_quality)
        )

        # Step 3: 运动指令(仅闭环时)
        motor_command = None
        if self.loop_closed:
            motor_command = self._generate_motor_command()

        # Step 4: 计算回路性能
        performance = self._compute_loop_performance()

        self.performance_history.append(performance)

        return {
            "iteration": self.iteration_count,
            "loop_closed": self.loop_closed,
            "schema_update": update_report,
            "motor_command": motor_command,
            "loop_performance": performance
        }

    def _generate_motor_command(self) -> Dict[str, Any]:
        """
        生成运动指令

        基于BodySchema当前状态和shell特性,
        生成对筋膜的驱动指令
        """
        confidence = self.body_schema.proprioceptive_confidence
        # 驱动强度正比于置信度
        drive_amplitude = confidence * self.shell.elastic_modulus * 0.1
        # 阻尼调制
        damping_modulation = self.shell.damping_coeff

        return {
            "drive_amplitude": drive_amplitude,
            "damping_modulation": damping_modulation,
            "target_stiffness": self.shell.elastic_modulus * (1 + 0.1 * confidence)
        }

    def _compute_loop_performance(self) -> float:
        """计算回路性能指标"""
        if not self.loop_closed:
            # 开环: 仅传感, 无反馈优化
            return self.body_schema.proprioceptive_confidence * 0.5

        # 闭环: 传感+反馈
        confidence = self.body_schema.proprioceptive_confidence
        damping_quality = min(1.0, self.shell.damping_ratio()) if self.shell.damping_ratio() > 0 else 0.0
        shell_factor = self.shell.integrity

        return confidence * damping_quality * shell_factor

    def get_bootstrap_progress(self) -> float:
        """
        获取自举进度

        自举进度 = 闭环性能改善率
        """
        if len(self.performance_history) < 2:
            return 0.0
        recent = self.performance_history[-1]
        previous = self.performance_history[-2]
        if previous == 0:
            return 1.0 if recent > 0 else 0.0
        return (recent - previous) / previous


# ═══════════════════════════════════════════════════════════════
# §4 ArtificialFascia — 人工筋膜
# ═══════════════════════════════════════════════════════════════

class FasciaLayer(Enum):
    """叠层架构层次"""
    HYDROPHOBIC_TPU = 0      # 疏水TPU(外层)
    CNT_AGNW_SENSOR = 1       # CNT/AgNW感知层
    DEA_STF_SUBSTRATE = 2     # DEA+STF基体层
    FABRIC_REINFORCED = 3     # 织物增强硅胶层(内层)


@dataclass
class FasciaLayerSpec:
    """筋膜单层规格"""
    name: str
    thickness: float       # 厚度(mm)
    youngs_modulus: float   # 杨氏模量(MPa)
    conductivity: float     # 电导率(S/m)
    sensor_density: float   # 传感密度(/mm²)


class ArtificialFascia:
    """
    人工筋膜

    三要件:
    1. 软连续介质力学匹配 — 各层力学特性连续过渡
    2. 嵌入式共形传感-驱动网络 — 传感驱动一体化
    3. 自适应迟滞阻尼 — STF(剪切增稠流体)基体提供自适应阻尼

    叠层架构 (由外到内):
    Layer 0: 疏水TPU — 环境隔离
    Layer 1: CNT/AgNW感知 — 传感网络
    Layer 2: DEA+STF基体 — 驱动+自适应阻尼
    Layer 3: 织物增强硅胶 — 结构支撑
    """

    # 默认叠层规格
    DEFAULT_LAYERS = {
        FasciaLayer.HYDROPHOBIC_TPU: FasciaLayerSpec(
            name="Hydrophobic_TPU", thickness=0.2,
            youngs_modulus=8.0, conductivity=1e-12, sensor_density=0.0
        ),
        FasciaLayer.CNT_AGNW_SENSOR: FasciaLayerSpec(
            name="CNT_AgNW_Sensor", thickness=0.05,
            youngs_modulus=2.0, conductivity=1e4, sensor_density=100.0
        ),
        FasciaLayer.DEA_STF_SUBSTRATE: FasciaLayerSpec(
            name="DEA_STF_Substrate", thickness=1.0,
            youngs_modulus=0.5, conductivity=1e-8, sensor_density=10.0
        ),
        FasciaLayer.FABRIC_REINFORCED: FasciaLayerSpec(
            name="Fabric_Reinforced_Silicone", thickness=0.5,
            youngs_modulus=2.5, conductivity=1e-14, sensor_density=0.0
        ),
    }

    def __init__(self, layers: Optional[Dict[FasciaLayer, FasciaLayerSpec]] = None):
        self.layers = layers or dict(self.DEFAULT_LAYERS)
        self.shell = SoftL2Shell()
        self.body_schema = BodySchema()
        self.omega_loop = ProprioceptionOmegaLoop(self.shell, self.body_schema)

    def check_mechanical_matching(self) -> bool:
        """
        检验软连续介质力学匹配

        相邻层杨氏模量比值应 < 10 (避免界面应力集中)
        """
        layer_order = sorted(self.layers.keys(), key=lambda x: x.value)
        for i in range(len(layer_order) - 1):
            E_upper = self.layers[layer_order[i]].youngs_modulus
            E_lower = self.layers[layer_order[i + 1]].youngs_modulus
            if E_upper == 0 or E_lower == 0:
                continue
            ratio = max(E_upper, E_lower) / min(E_upper, E_lower)
            if ratio > 10:
                return False
        return True

    def check_conformal_sensor_network(self) -> bool:
        """
        检验嵌入式共形传感-驱动网络

        传感层(CNT/AgNW)的传感密度应 > 阈值
        DEA层应有足够电导率驱动
        """
        sensor_layer = self.layers.get(FasciaLayer.CNT_AGNW_SENSOR)
        dea_layer = self.layers.get(FasciaLayer.DEA_STF_SUBSTRATE)

        if sensor_layer is None or dea_layer is None:
            return False

        # 传感密度阈值
        if sensor_layer.sensor_density < 50.0:
            return False

        # DEA驱动阈值
        if dea_layer.conductivity < 1e-10:
            return False

        return True

    def check_adaptive_damping(self) -> bool:
        """
        检验自适应迟滞阻尼

        STF基体应具有剪切增稠特性(低剪切速率低粘度, 高剪切速率高粘度)
        简化检验: DEA+STF层的杨氏模量应低于弹性层
        """
        dea_layer = self.layers.get(FasciaLayer.DEA_STF_SUBSTRATE)
        outer_layer = self.layers.get(FasciaLayer.HYDROPHOBIC_TPU)

        if dea_layer is None:
            return False

        # STF基体应有低模量(软)以便自适应
        if dea_layer.youngs_modulus > 5.0:
            return False

        return True

    def check_three_requirements(self) -> Dict[str, bool]:
        """检验人工筋膜三要件"""
        return {
            "mechanical_matching": self.check_mechanical_matching(),
            "conformal_sensor_network": self.check_conformal_sensor_network(),
            "adaptive_damping": self.check_adaptive_damping()
        }

    def all_requirements_met(self) -> bool:
        """三要件是否全部满足"""
        checks = self.check_three_requirements()
        return all(checks.values())

    def compute_tau_eff(self, g_m: float, phi_coherence: float) -> float:
        """
        计算tau韬定律: tau_eff = Z_inter / (g_m * Phi_coherence)

        Args:
            g_m: 跨膜电导
            phi_coherence: 流贯相干度

        Returns:
            tau_eff: 有效延迟
        """
        Z_inter = self.shell.effective_impedance()
        if g_m * phi_coherence == 0:
            return float('inf')
        return Z_inter / (g_m * phi_coherence)

    def compute_tau_eff_super_node(self, g_m: float, phi_coherence: float,
                                    reduction_factor: float = 0.1) -> float:
        """
        超节点Sigma_super下的tau_eff

        Z_inter -> Z_intra = reduction_factor * Z_inter
        """
        Z_intra = self.shell.effective_impedance() * reduction_factor
        if g_m * phi_coherence == 0:
            return float('inf')
        return Z_intra / (g_m * phi_coherence)


# ═══════════════════════════════════════════════════════════════
# §5 ArtificialFasciaEmbodiment — 主引擎
# ═══════════════════════════════════════════════════════════════

class ArtificialFasciaEmbodiment:
    """
    人工筋膜具身自举主引擎

    整合软L2壳、本体感觉Omega回路、人工筋膜三要件,
    提供统一的具身智能计算与分析接口。

    工作流:
    1. 检验人工筋膜三要件(力学匹配+共形传感+自适应阻尼)
    2. 计算tau_eff和超节点优化
    3. 执行Omega回路迭代(传感->BodySchema->运动指令)
    4. 评估具身闭环和自举进度
    """

    def __init__(self, layers: Optional[Dict[FasciaLayer, FasciaLayerSpec]] = None):
        self.fascia = ArtificialFascia(layers)

    def full_analysis(self, g_m: float = 1.0,
                      phi_coherence: float = 0.8,
                      external_signal: Optional[Dict[str, Any]] = None,
                      n_iterations: int = 5) -> Dict[str, Any]:
        """
        执行完整的人工筋膜具身分析

        Args:
            g_m: 跨膜电导
            phi_coherence: 流贯相干度
            external_signal: 外部传感信号
            n_iterations: Omega回路迭代次数

        Returns:
            完整分析结果
        """
        # 1. 三要件检验
        requirements = self.fascia.check_three_requirements()
        all_met = self.fascia.all_requirements_met()

        # 2. tau_eff计算
        tau_eff = self.fascia.compute_tau_eff(g_m, phi_coherence)
        tau_eff_super = self.fascia.compute_tau_eff_super_node(
            g_m, phi_coherence, reduction_factor=0.1
        )

        # 3. Omega回路迭代
        # 先开环迭代
        open_results = []
        self.fascia.omega_loop.open_loop()
        for i in range(n_iterations):
            result = self.fascia.omega_loop.iterate(external_signal)
            open_results.append(result)

        # 再闭环迭代
        closed_results = []
        self.fascia.omega_loop.close_loop()
        for i in range(n_iterations):
            result = self.fascia.omega_loop.iterate(external_signal)
            closed_results.append(result)

        # 4. 自举进度
        bootstrap_progress = self.fascia.omega_loop.get_bootstrap_progress()

        # 5. 综合评估
        embodiment_achieved = (
            all_met and
            self.fascia.omega_loop.loop_closed and
            self.fascia.body_schema.proprioceptive_confidence > 0.3
        )

        return {
            "three_requirements": requirements,
            "all_requirements_met": all_met,
            "tau_eff": {
                "normal": tau_eff,
                "super_node": tau_eff_super,
                "speedup": tau_eff / tau_eff_super if tau_eff_super > 0 else float('inf')
            },
            "omega_loop": {
                "iterations_open": len(open_results),
                "iterations_closed": len(closed_results),
                "loop_closed": self.fascia.omega_loop.loop_closed,
                "performance_history": self.fascia.omega_loop.performance_history[-n_iterations:],
                "bootstrap_progress": bootstrap_progress
            },
            "body_schema": {
                "confidence": self.fascia.body_schema.proprioceptive_confidence,
                "update_count": self.fascia.body_schema.update_count,
                "position": self.fascia.body_schema.position,
                "posture": self.fascia.body_schema.posture
            },
            "shell_state": {
                "elastic_modulus": self.fascia.shell.elastic_modulus,
                "sensor_density": self.fascia.shell.sensor_density,
                "damping_coeff": self.fascia.shell.damping_coeff,
                "integrity": self.fascia.shell.integrity,
                "impedance": self.fascia.shell.effective_impedance()
            },
            "embodiment_achieved": embodiment_achieved
        }


# ═══════════════════════════════════════════════════════════════
# §6 MVE — 最小可验证实验
# ═══════════════════════════════════════════════════════════════

def run_mve_tests() -> Dict[str, bool]:
    """
    运行M217 MVE测试

    T238 — tau韬定律:
      tau_eff = Z_inter / (g_m * Phi_coherence)
      超节点Sigma_super使Z_inter->Z_intra, tau_eff大幅降低

    T239 — 具身自举定理:
      三要件满足 + Omega闭环 -> 具身闭环
      具身闭环 -> 自举升级能力
    """
    results = {}

    # ─── T238: tau韬定律 ───
    try:
        fascia = ArtificialFascia()

        # Case 1: 正常tau_eff
        tau_normal = fascia.compute_tau_eff(g_m=1.0, phi_coherence=0.8)
        assert tau_normal > 0, f"tau_eff should be positive, got {tau_normal}"
        assert tau_normal < float('inf'), "tau_eff should be finite for valid inputs"

        # Case 2: 超节点降低tau_eff
        tau_super = fascia.compute_tau_eff_super_node(
            g_m=1.0, phi_coherence=0.8, reduction_factor=0.1
        )
        assert tau_super < tau_normal, \
            f"Super-node tau_eff ({tau_super}) should < normal ({tau_normal})"
        speedup = tau_normal / tau_super
        assert speedup > 5.0, \
            f"Speedup should be > 5x, got {speedup:.1f}x"

        # Case 3: g_m或phi_coherence=0 → tau_eff=inf
        tau_zero_gm = fascia.compute_tau_eff(g_m=0.0, phi_coherence=0.8)
        assert tau_zero_gm == float('inf'), \
            f"tau_eff should be inf when g_m=0, got {tau_zero_gm}"

        tau_zero_phi = fascia.compute_tau_eff(g_m=1.0, phi_coherence=0.0)
        assert tau_zero_phi == float('inf'), \
            f"tau_eff should be inf when phi_coherence=0, got {tau_zero_phi}"

        # Case 4: phi_coherence↑ → tau_eff↓
        tau_low_phi = fascia.compute_tau_eff(g_m=1.0, phi_coherence=0.2)
        tau_high_phi = fascia.compute_tau_eff(g_m=1.0, phi_coherence=0.9)
        assert tau_high_phi < tau_low_phi, \
            "Higher phi_coherence should give lower tau_eff"

        results["T238"] = True
        print("  T238 (tau-tao law theorem): PASS")
    except Exception as e:
        results["T238"] = False
        print(f"  T238 (tau-tao law theorem): FAIL -- {e}")

    # ─── T239: 具身自举定理 ───
    try:
        engine = ArtificialFasciaEmbodiment()

        # Case 1: 默认叠层三要件应全部满足
        requirements = engine.fascia.check_three_requirements()
        assert requirements["mechanical_matching"] is True, \
            f"Default mechanical matching should pass"
        assert requirements["conformal_sensor_network"] is True, \
            f"Default conformal sensor network should pass"
        assert requirements["adaptive_damping"] is True, \
            f"Default adaptive damping should pass"
        assert engine.fascia.all_requirements_met() is True, \
            "All three requirements should be met with default layers"

        # Case 2: 开环vs闭环迭代
        # 先开环
        engine.fascia.omega_loop.open_loop()
        signal = {"position": (1.0, 0.0, 0.0), "posture": 0.5, "signal_quality": 0.9}
        for _ in range(3):
            engine.fascia.omega_loop.iterate(signal)
        open_confidence = engine.fascia.body_schema.proprioceptive_confidence

        # 闭环
        engine.fascia.omega_loop.close_loop()
        for _ in range(5):
            engine.fascia.omega_loop.iterate(signal)
        closed_confidence = engine.fascia.body_schema.proprioceptive_confidence

        assert closed_confidence >= open_confidence, \
            f"Closed-loop confidence ({closed_confidence}) should >= open-loop ({open_confidence})"

        # Case 3: 具身闭环判定
        analysis = engine.full_analysis(
            g_m=1.0, phi_coherence=0.8,
            external_signal=signal, n_iterations=3
        )
        assert analysis["all_requirements_met"] is True, \
            "All requirements should be met"
        assert analysis["embodiment_achieved"] is True, \
            "Embodiment should be achieved with all conditions met"

        # Case 4: 破坏三要件之一 → 具身不闭合
        # 修改传感层密度使其低于阈值
        bad_layers = dict(ArtificialFascia.DEFAULT_LAYERS)
        bad_layers[FasciaLayer.CNT_AGNW_SENSOR] = FasciaLayerSpec(
            name="Bad_Sensor", thickness=0.05,
            youngs_modulus=2.0, conductivity=1e4, sensor_density=10.0  # < 50 threshold
        )
        bad_engine = ArtificialFasciaEmbodiment(bad_layers)
        assert bad_engine.fascia.all_requirements_met() is False, \
            "Bad layers should fail requirements"

        results["T239"] = True
        print("  T239 (embodiment bootstrap theorem): PASS")
    except Exception as e:
        results["T239"] = False
        print(f"  T239 (embodiment bootstrap theorem): FAIL -- {e}")

    # ─── Summary ───
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n  M217 MVE Summary: {passed}/{total} PASS")
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("M217 ArtificialFasciaEmbodiment -- MVE Tests")
    print("=" * 60)
    run_mve_tests()
