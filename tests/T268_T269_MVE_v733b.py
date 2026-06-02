# -*- coding: utf-8 -*-
"""
MVE Tests: v7.33b — M226 PCTChecker (T2.40) + M155 IDO (T2.41)

T268: M226 PCT 四条件校验 (6 cases)
T269: M155 IDO 信息力+时间箭头 (6 cases)

Author: Kou (寇豆码) — 太乙AGI团队
"""

import sys
import math
import pytest

# 项目根目录
sys.path.insert(0, 'D:/WorkBuddy/2026-05-06-task-1')


# ══════════════════════════════════════════════════
# T268: M226 PCT 四条件校验
# ══════════════════════════════════════════════════

class TestT268M226PCT:
    """T268: PCT端口兼容性定理 MVE"""

    @pytest.fixture(autouse=True)
    def setup(self):
        from modules.M226_PCTChecker import PCTChecker, PCTSphere
        self.checker = PCTChecker()
        self.PCTSphere = PCTSphere

    def test_268_1_constructive_compatible(self):
        """T268.1: 同手性构造端口兼容"""
        src = self.PCTSphere(ports=0x03, phase=0.1, chi=1, grade=2, name="S1")  # cn|cx
        dst = self.PCTSphere(ports=0x01, phase=0.1, chi=1, grade=2, name="S2")  # cn
        result = self.checker.check_pct(src, dst, target_phase=0.1)
        assert result.direction_ok is True
        assert result.chirality_ok is True
        assert result.compatible is True

    def test_268_2_direction_incompatible(self):
        """T268.2: 方向不互补"""
        src = self.PCTSphere(ports=0x05, phase=0.0, chi=1, grade=2, name="S3")  # cn|ce (无出端口)
        dst = self.PCTSphere(ports=0x01, phase=0.0, chi=1, grade=2, name="S4")  # cn (无出端口)
        result = self.checker.check_pct(src, dst)
        assert result.direction_ok is False

    def test_268_3_chirality_incompatible(self):
        """T268.3: 手性不相容"""
        src = self.PCTSphere(ports=0x03, phase=0.0, chi=1, grade=2, name="S5")   # 构造
        dst = self.PCTSphere(ports=0x50, phase=0.0, chi=-1, grade=2, name="S6")  # 消解
        result = self.checker.check_pct(src, dst)
        assert result.chirality_ok is False

    def test_268_4_meta_chirality_compatible(self):
        """T268.4: meta手性与任何手性相容"""
        src = self.PCTSphere(ports=0x42, phase=0.0, chi=0, grade=2, name="S7")   # meta
        dst = self.PCTSphere(ports=0x50, phase=0.0, chi=-1, grade=2, name="S8")  # 消解
        result = self.checker.check_pct(src, dst)
        assert result.chirality_ok is True

    def test_268_5_grade_not_conserved(self):
        """T268.5: 构造连接奇数阶不守恒"""
        src = self.PCTSphere(ports=0x03, phase=0.0, chi=1, grade=1, name="S9")   # 构造+奇数阶
        dst = self.PCTSphere(ports=0x01, phase=0.0, chi=1, grade=2, name="S10")
        result = self.checker.check_pct(src, dst)
        assert result.grade_ok is False  # 1+2=3 (奇数)

    def test_268_6_full_compatible(self):
        """T268.6: 全条件兼容"""
        src = self.PCTSphere(ports=0x06, phase=0.1, chi=1, grade=4, name="S11")  # cx|ce
        dst = self.PCTSphere(ports=0x05, phase=0.1, chi=1, grade=4, name="S12")  # cn|ce
        result = self.checker.check_pct(src, dst, target_phase=0.1)
        assert result.compatible is True
        assert result.direction_ok is True
        assert result.chirality_ok is True
        assert result.phase_ok is True
        assert result.grade_ok is True


# ══════════════════════════════════════════════════
# T269: M155 IDO 信息力+时间箭头
# ══════════════════════════════════════════════════

class TestT269M155IDO:
    """T269: IDO信息力时间箭头 MVE"""

    @pytest.fixture(autouse=True)
    def setup(self):
        from modules.M155_FtelOptimizer import FtelOptimizer
        self.engine = FtelOptimizer()

    def test_269_1_info_amount_uniform(self):
        """T269.1: 均匀分布信息量 = log₂(N)"""
        heap = {"A": 3, "B": 3, "C": 3, "D": 3}
        I = self.engine.compute_info_amount(heap)
        assert abs(I - math.log2(4)) < 1e-6

    def test_269_2_info_force_rare_higher(self):
        """T269.2: 低度数(稀有)节点信息力更高"""
        heap = {"center": 5, "leaf1": 1, "leaf2": 1, "leaf3": 1, "leaf4": 1}
        F_center, _ = self.engine.compute_info_force("center", heap)
        F_leaf, _ = self.engine.compute_info_force("leaf1", heap)
        assert F_leaf > F_center  # 稀有节点信息力更高

    def test_269_3_time_arrow_forward(self):
        """T269.3: 递增信息量 → forward"""
        history = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = self.engine.get_time_arrow(history)
        assert result.direction == "forward"
        assert result.slope > 0

    def test_269_4_time_arrow_backward(self):
        """T269.4: 递减信息量 → backward"""
        history = [5.0, 4.0, 3.0, 2.0, 1.0]
        result = self.engine.get_time_arrow(history)
        assert result.direction == "backward"
        assert result.slope < 0

    def test_269_5_ido_update_mod_direction(self):
        """T269.5: IDO更新 mod 方向正确"""
        heap = {"high": 10, "low": 1}
        result_low = self.engine.ido_update("low", heap, current_mod=1.0, dt=0.1)
        result_high = self.engine.ido_update("high", heap, current_mod=1.0, dt=0.1)
        # 低度数→高信息力→F>0.5→mod增长
        assert result_low.info_force > 0.5
        # 高度数→低信息力→F<0.5→mod衰减
        assert result_high.info_force < 0.5

    def test_269_6_theorem_t241_verified(self):
        """T269.6: 定理T2.41验证通过"""
        result = self.engine.verify_theorem_t241()
        assert result['verified'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
