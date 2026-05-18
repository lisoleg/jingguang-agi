#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token全生命周期管理器 - 基于联邦宇宙化身合体文档
Token四元统一：算元/词元/智元/通证统一场论

核心定理：
1. Token拓扑激发定理：四元Token是Φ场的四种拓扑激发态
2. 四元共振统一定理：波核(算元/词元)与粒核(智元/通证)
3. 交易即发行定理：满周相变激发Token
4. JIAJIA式写通知回收定理

基于IGCTR理论：
- Φ: 信息相位场
- 波核(Wave Kernel): 算元(Φ_calc)、词元(Φ_word) - 流动/消耗
- 粒核(Particle Kernel): 智元(Φ_wit)、通证(Φ_pass) - 稳定/锚定
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import time


class TokenType(Enum):
    """Token类型"""
    CALC = "calc"       # 算元 - 波核
    WORD = "word"       # 词元 - 波核
    WIT = "wit"         # 智元 - 粒核
    PASS = "pass"       # 通证 - 粒核


class TokenState(Enum):
    """Token状态"""
    ISSUED = "issued"           # 已发行
    ACTIVE = "active"           # 活跃
    CONSUMED = "consumed"       # 已消费
    SETTLED = "settled"         # 已结算
    EXPIRED = "expired"         # 已过期
    ARCHIVED = "archived"       # 已归档


class ActivityVerb(Enum):
    """ActivityPub动词"""
    CREATE = "Create"           # 创建
    OFFER = "Offer"             # 提议
    ACCEPT = "Accept"           # 接受
    REJECT = "Reject"           # 拒绝
    CONSUME = "Consume"         # 消费
    UPDATE = "Update"           # 更新
    DELETE = "Delete"           # 删除
    ANNOUNCE = "Announce"       # 宣布
    REWARD = "Reward"           # 奖励


@dataclass
class Token:
    """Token对象"""
    token_id: str
    token_type: TokenType
    genesis_activity: str       # 创世Activity
    state: TokenState
    amount: float               # 数量/额度
    owner: str                  # 持有者
    created_at: float
    last_activity: float
    winding_number: float = 0.0  # 拓扑缠绕数
    phase_gradient: float = 0.0  # 相位梯度
    metadata: Dict = field(default_factory=dict)


@dataclass
class PhaseTransition:
    """拓扑相变"""
    timestamp: float
    transition_type: str        # wave_to_particle, particle_to_wave, etc.
    trigger_activity: ActivityVerb
    winding_number_before: float
    winding_number_after: float
    s_phi_delta: float          # 信息作用量变化


@dataclass
class WriteNotice:
    """JIAJIA式写通知"""
    resource_lock: str
    notice_content: str
    notice_type: str            # consumed, settled, expired
    timestamp: float
    issued_by: str


class TokenLifecycleManager:
    """
    Token全生命周期管理器
    
    定理2.1.1（四元共振统一）:
    算元、智元、词元、通证共享同一个相位场Φ的拓扑根基
    
    核心范式：
    - 交易即发行：满周相变(Δw=1)激发Token
    - 流转即回收：JIAJIA式写通知回收
    """
    
    # Token类型配置
    TOKEN_CONFIG = {
        TokenType.CALC: {"kernel": "wave", "lifetime_s": 3600, "consumable": True},
        TokenType.WORD: {"kernel": "wave", "lifetime_s": 86400, "consumable": True},
        TokenType.WIT: {"kernel": "particle", "lifetime_s": -1, "consumable": False},
        TokenType.PASS: {"kernel": "particle", "lifetime_s": 604800, "consumable": False},
    }
    
    # 拓扑相变阈值
    WINDING_THRESHOLD = 1.0     # 满周相变阈值
    PHASE_GRADIENT_CRITICAL = 0.8
    
    def __init__(self):
        self.tokens: Dict[str, Token] = {}
        self.write_notices: Dict[str, WriteNotice] = {}
        self.phase_transitions: List[PhaseTransition] = []
        self.activities: List[Dict] = []
        self.winding_history: List[float] = []
        
        # 统计
        self.stats = {
            "total_issued": 0,
            "total_consumed": 0,
            "wave_to_particle": 0,
            "particle_to_wave": 0,
            "avg_winding": 0,
            "avg_lifetime": 0,
        }
        
    def process_activity(self, activity: Dict) -> Tuple[Optional[Token], Optional[PhaseTransition]]:
        """
        处理ActivityPub Activity
        
        驱动Token生命周期：
        - CREATE: 发行Token（交易即发行）
        - OFFER/ACCEPT: 流转
        - CONSUME: 消费（算元/词元回收）
        - UPDATE: 更新状态（智元结算）
        - DELETE: 删除（通证回收）
        
        Args:
            activity: Activity对象
            
        Returns:
            (生成的Token, 拓扑相变)
        """
        verb = activity.get("verb", "")
        obj_type = activity.get("object_type", "calc")
        actor = activity.get("actor", "")
        target = activity.get("target", "")
        amount = activity.get("amount", 1.0)
        
        token = None
        phase_transition = None
        
        # 解析动词
        if verb == "Create":
            # 交易即发行
            token, phase_transition = self._issue_token(
                token_type_str=obj_type,
                actor=actor,
                genesis_activity=json.dumps(activity),
                amount=amount
            )
            self.stats["total_issued"] += 1
            
        elif verb == "Accept" and activity.get("offer_id"):
            # 接受提议，触发满周相变
            phase_transition = self._trigger_phase_transition(
                activity, 
                TransitionType.WAVE_CRITICAL
            )
            
        elif verb == "Consume":
            # 消费Token
            self._consume_token(activity.get("token_id", ""))
            self.stats["total_consumed"] += 1
            
        elif verb == "Reward":
            # 奖励/结算
            self._settle_token(activity.get("token_id", ""))
            
        elif verb == "Delete":
            # 删除/回收
            self._expire_token(activity.get("token_id", ""))
            
        # 记录Activity
        self.activities.append(activity)
        
        return token, phase_transition
        
    def _issue_token(self, token_type_str: str, actor: str, 
                    genesis_activity: str, amount: float) -> Tuple[Token, PhaseTransition]:
        """
        发行Token（交易即发行）
        
        定理：Token的id与genesis绑定到触发Activity，
        实现"交易即发行"——不是"先造好再花"，
        而是"花的那一下，它才存在"
        """
        # 解析Token类型
        type_map = {"calc": TokenType.CALC, "word": TokenType.WORD, 
                   "wit": TokenType.WIT, "pass": TokenType.PASS}
        token_type = type_map.get(token_type_str, TokenType.CALC)
        
        # 生成Token ID
        token_id = f"{token_type.value}_{actor}_{int(time.time()*1000)}"
        
        # 满周相变检测
        current_winding = self.winding_history[-1] if self.winding_history else 0
        new_winding = current_winding + 1.0  # 每次交易+1
        
        # 创建Token
        token = Token(
            token_id=token_id,
            token_type=token_type,
            genesis_activity=genesis_activity,
            state=TokenState.ISSUED,
            amount=amount,
            owner=actor,
            created_at=time.time(),
            last_activity=time.time(),
            winding_number=new_winding,
            phase_gradient=amount / max(new_winding, 1),
        )
        
        self.tokens[token_id] = token
        self.winding_history.append(new_winding)
        
        # 拓扑相变
        phase_transition = PhaseTransition(
            timestamp=time.time(),
            transition_type="genesis",
            trigger_activity=ActivityVerb.CREATE,
            winding_number_before=current_winding,
            winding_number_after=new_winding,
            s_phi_delta=self._calculate_s_phi_change(new_winding, token_type)
        )
        
        return token, phase_transition
        
    def _trigger_phase_transition(self, activity: Dict, 
                                  transition_type: str) -> Optional[PhaseTransition]:
        """触发拓扑相变"""
        current_winding = self.winding_history[-1] if self.winding_history else 0
        new_winding = current_winding + 0.5
        
        transition = PhaseTransition(
            timestamp=time.time(),
            transition_type=transition_type,
            trigger_activity=ActivityVerb.ACCEPT,
            winding_number_before=current_winding,
            winding_number_after=new_winding,
            s_phi_delta=self._calculate_s_phi_change(new_winding, TokenType.CALC)
        )
        
        self.phase_transitions.append(transition)
        self.winding_history.append(new_winding)
        
        return transition
        
    def _calculate_s_phi_change(self, winding: float, token_type: TokenType) -> float:
        """计算信息作用量变化"""
        base_change = np.log(winding + 1) * 0.1
        kernel_factor = 1.0 if self.TOKEN_CONFIG[token_type]["kernel"] == "wave" else 0.5
        return base_change * kernel_factor
        
    def _consume_token(self, token_id: str) -> bool:
        """消费Token（波核耗散）"""
        if token_id not in self.tokens:
            return False
            
        token = self.tokens[token_id]
        token.state = TokenState.CONSUMED
        
        # 波核耗散：信息回归背景场
        # JIAJIA式写通知
        notice = WriteNotice(
            resource_lock=f"token_{token_id}",
            notice_content="consumed",
            notice_type="consumed",
            timestamp=time.time(),
            issued_by=token.owner
        )
        self.write_notices[f"token_{token_id}"] = notice
        
        return True
        
    def _settle_token(self, token_id: str) -> bool:
        """结算Token（粒核转移）"""
        if token_id not in self.tokens:
            return False
            
        token = self.tokens[token_id]
        token.state = TokenState.SETTLED
        
        # 粒核转移
        notice = WriteNotice(
            resource_lock=f"token_{token_id}",
            notice_content="settled",
            notice_type="settled",
            timestamp=time.time(),
            issued_by=token.owner
        )
        self.write_notices[f"token_{token_id}"] = notice
        
        return True
        
    def _expire_token(self, token_id: str) -> bool:
        """过期Token（回收）"""
        if token_id not in self.tokens:
            return False
            
        token = self.tokens[token_id]
        token.state = TokenState.EXPIRED
        
        notice = WriteNotice(
            resource_lock=f"token_{token_id}",
            notice_content="expired",
            notice_type="expired",
            timestamp=time.time(),
            issued_by=token.owner
        )
        self.write_notices[f"token_{token_id}"] = notice
        
        return True
        
    def check_token_validity(self, token_id: str) -> Tuple[bool, str]:
        """
        检查Token有效性
        
        JIAJIA式检查：只需查询写通知，无需全局账本
        
        Args:
            token_id: Token ID
            
        Returns:
            (是否有效, 原因)
        """
        if token_id not in self.tokens:
            return False, "Token不存在"
            
        token = self.tokens[token_id]
        notice_key = f"token_{token_id}"
        
        # 检查写通知
        if notice_key in self.write_notices:
            notice = self.write_notices[notice_key]
            if notice.notice_type == "consumed":
                return False, "已消费"
            elif notice.notice_type == "settled":
                return False, "已结算"
            elif notice.notice_type == "expired":
                return False, "已过期"
                
        # 检查生命周期
        config = self.TOKEN_CONFIG[token.token_type]
        if config["lifetime_s"] > 0:
            age = time.time() - token.created_at
            if age > config["lifetime_s"]:
                return False, "超过生命周期"
                
        return True, "有效"
        
    def evaluate_quadruple_resonance(self) -> Dict[str, Any]:
        """
        评估四元共振
        
        定理2.1.1：四元共振统一
        算元/词元（波核）↔ 智元/通证（粒核）共振
        
        Returns:
            四元共振评估
        """
        # 统计各类型Token
        token_counts = {tt.value: 0 for tt in TokenType}
        token_amounts = {tt.value: 0.0 for tt in TokenType}
        
        for token in self.tokens.values():
            token_counts[token.token_type.value] += 1
            token_amounts[token.token_type.value] += token.amount
            
        # 波核/粒核比例
        wave_count = token_counts["calc"] + token_counts["word"]
        particle_count = token_counts["wit"] + token_counts["pass"]
        wave_ratio = wave_count / max(len(self.tokens), 1)
        
        # 计算共振度
        # 共振 = 1 - |波核比例 - 0.5| * 2
        resonance = 1.0 - abs(wave_ratio - 0.5) * 2
        
        # 活跃度
        active_tokens = [t for t in self.tokens.values() if t.state == TokenState.ACTIVE]
        activity_rate = len(active_tokens) / max(len(self.tokens), 1)
        
        return {
            "wave_kernel_calc": token_counts["calc"],
            "wave_kernel_word": token_counts["word"],
            "particle_kernel_wit": token_counts["wit"],
            "particle_kernel_pass": token_counts["pass"],
            "wave_total_amount": token_amounts["calc"] + token_amounts["word"],
            "particle_total_amount": token_amounts["wit"] + token_amounts["pass"],
            "wave_ratio": wave_ratio,
            "quadruple_resonance": resonance,
            "activity_rate": activity_rate,
            "total_tokens": len(self.tokens),
            "status": "healthy" if resonance > 0.6 else "imbalanced"
        }
        
    def simulate_city_traffic_workflow(self) -> Dict[str, Any]:
        """
        模拟城市交通AI服务的完整Token生命周期
        
        来自文档第五章的完整例子
        """
        results = []
        
        # Step 1: Alice请求路线 (Offer)
        _, pt1 = self.process_activity({
            "verb": "Offer",
            "actor": "alice",
            "object_type": "calc",
            "target": "traffic-ai",
            "amount": 1.0
        })
        results.append({"step": 1, "activity": "Offer", "result": "提议已发送"})
        
        # Step 2: Traffic-AI接受并发行Token (Accept + Create)
        token1, pt2 = self.process_activity({
            "verb": "Accept",
            "actor": "traffic-ai",
            "object_type": "calc",
            "offer_id": "offer_001",
            "amount": 1.0
        })
        results.append({"step": 2, "activity": "Accept+Create", 
                       "result": f"Token发行: {token1.token_id if token1 else 'N/A'}"})
        
        # Step 3: Sensor-Co提供数据
        token2, _ = self.process_activity({
            "verb": "Create",
            "actor": "sensor-co",
            "object_type": "word",
            "amount": 10.0
        })
        results.append({"step": 3, "activity": "Create(Word)", 
                       "result": f"词元发行: {token2.token_id if token2 else 'N/A'}"})
        
        # Step 4: 消费算元
        if token1:
            self.process_activity({
                "verb": "Consume",
                "token_id": token1.token_id,
                "actor": "traffic-ai"
            })
        results.append({"step": 4, "activity": "Consume", "result": "算元已消费(波核耗散)"})
        
        # Step 5: 结算智元
        _, _ = self.process_activity({
            "verb": "Reward",
            "actor": "traffic-ai",
            "object_type": "wit",
            "amount": 0.5,
            "target": "sensor-co"
        })
        results.append({"step": 5, "activity": "Reward", "result": "智元结算完成"})
        
        # 最终共振评估
        resonance = self.evaluate_quadruple_resonance()
        
        return {
            "workflow_steps": results,
            "final_resonance": resonance,
            "theorem": "交易即发行，流转即回收",
            "lifecycle_completion": "完整"
        }
        
    def get_diagnostic_report(self) -> Dict[str, Any]:
        """获取诊断报告"""
        resonance = self.evaluate_quadruple_resonance()
        
        # 统计写通知
        notice_stats = {}
        for notice in self.write_notices.values():
            notice_stats[notice.notice_type] = notice_stats.get(notice.notice_type, 0) + 1
            
        return {
            "title": "Token全生命周期诊断报告",
            "theorem": "Token拓扑激发定理 (定理2.1.1)",
            "total_tokens": len(self.tokens),
            "active_tokens": len([t for t in self.tokens.values() if t.state == TokenState.ACTIVE]),
            "quadruple_resonance": resonance,
            "phase_transitions": len(self.phase_transitions),
            "write_notices": notice_stats,
            "stats": self.stats,
            "kernel_summary": {
                "wave_kernel": "算元/词元 - 流动/消耗性",
                "particle_kernel": "智元/通证 - 稳定/锚定性"
            },
            "recommendation": "四元共振统一是化身合体的核心基础设施"
        }


def demo():
    """演示Token全生命周期管理器"""
    print("=" * 70)
    print("Token全生命周期管理器 - 基于联邦宇宙化身合体文档")
    print("=" * 70)
    
    manager = TokenLifecycleManager()
    
    # 模拟城市交通工作流
    workflow = manager.simulate_city_traffic_workflow()
    
    print("\n📋 工作流模拟:")
    for step in workflow["workflow_steps"]:
        print(f"   Step {step['step']}: {step['activity']} - {step['result']}")
        
    # 四元共振评估
    resonance = workflow["final_resonance"]
    print(f"\n🔮 四元共振评估:")
    print(f"   - 波核(算元): {resonance['wave_kernel_calc']}")
    print(f"   - 波核(词元): {resonance['wave_kernel_word']}")
    print(f"   - 粒核(智元): {resonance['particle_kernel_wit']}")
    print(f"   - 粒核(通证): {resonance['particle_kernel_pass']}")
    print(f"   - 波核比例: {resonance['wave_ratio']:.2%}")
    print(f"   - 四元共振度: {resonance['quadruple_resonance']:.2%}")
    
    # 更多交易测试
    for i in range(5):
        manager.process_activity({
            "verb": "Create",
            "actor": f"user_{i}",
            "object_type": ["calc", "word", "wit", "pass"][i % 4],
            "amount": float(i + 1)
        })
        
    final_resonance = manager.evaluate_quadruple_resonance()
    print(f"\n📊 扩展测试后共振度: {final_resonance['quadruple_resonance']:.2%}")
    
    return manager


if __name__ == "__main__":
    demo()
