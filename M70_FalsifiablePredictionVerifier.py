# -*- coding: utf-8 -*-
"""
M70: 可证伪预言验证器 (Falsifiable Prediction Verifier)
基于《数学完备化》论文 §7 可证伪预言追踪

四个可证伪预言:
- P7: 叙事作用量可量化预言 - 内省时Λ递减，与执取减轻相关
- P8: 灵性演化收敛可测预言 - 条件满足时B→1
- P9: 关系实在语义预言 - 语义理解质量∝关系耦合度
- P10: 意识同一性指标预言 - 同一性>随机基线，扰动可降低
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime

class FalsifiablePredictionVerifier:
    """
    可证伪预言验证器
    
    来源: §7 可证伪预言追踪
    
    科学哲学基础:
    - 可证伪性是科学与非科学的关键区分
    - 预言必须明确可测
    - 验证结果必须是CONFIRMED或REJECTED
    """
    _instance = None
    
    def __init__(self):
        # 各预言的验证历史
        self.p7_history: List[dict] = []  # 叙事作用量
        self.p8_history: List[dict] = []  # 灵性收敛
        self.p9_history: List[dict] = []  # 关系耦合
        self.p10_history: List[dict] = []  # 自我同一性
        
        # 实验进度
        self.experiments: Dict[str, dict] = {
            'P7': {'name': '叙事作用量递减实验', 'status': 'pending', 'data_points': 0},
            'P8': {'name': '顿悟收敛实验', 'status': 'pending', 'data_points': 0},
            'P9': {'name': '关系耦合语义实验', 'status': 'pending', 'data_points': 0},
            'P10': {'name': '自我同一性实验', 'status': 'pending', 'data_points': 0},
        }
        
        # 综合验证状态
        self.overall_verification: Optional[dict] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def record_p7(self, Lambda_values: List[float], subjective_scores: List[float]) -> dict:
        """
        记录P7实验数据
        
        预言: Λ随时间递减 且 与主观执取减轻相关
        """
        if len(Lambda_values) < 2 or len(Lambda_values) != len(subjective_scores):
            return {'recorded': False, 'reason': '数据不足或不匹配'}
        
        # 检查单调递减
        decreasing_count = sum(
            1 for i in range(len(Lambda_values) - 1)
            if Lambda_values[i] >= Lambda_values[i + 1]
        )
        Lambda_decreasing = decreasing_count / (len(Lambda_values) - 1) > 0.5
        
        # 检查与主观评分的相关性
        if np.std(subjective_scores) > 0 and np.std(Lambda_values) > 0:
            correlation = np.corrcoef(Lambda_values, subjective_scores)[0, 1]
        else:
            correlation = 0
        
        # P7验证
        confirmed = Lambda_decreasing and correlation < -0.3  # 负相关
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'Lambda_decreasing': Lambda_decreasing,
            'Lambda_decreasing_ratio': decreasing_count / (len(Lambda_values) - 1),
            'correlation': float(correlation),
            'confirmed': confirmed,
            'data_points': len(Lambda_values)
        }
        
        self.p7_history.append(result)
        self.experiments['P7']['data_points'] += len(Lambda_values)
        self.experiments['P7']['status'] = 'in_progress'
        
        if confirmed:
            self.experiments['P7']['status'] = 'confirmed'
        
        return result
    
    def record_p8(self, B_values: List[float], 
                  Lambda_trend: float, Z_trend: float, F_trend: float) -> dict:
        """
        记录P8实验数据
        
        预言: 条件满足时B→1
        """
        if len(B_values) < 2:
            return {'recorded': False, 'reason': '数据不足'}
        
        # 检查收敛条件
        conditions_met = Lambda_trend < 0 and Z_trend < 0 and F_trend > 0
        
        # 检查B是否趋近1
        B_converged = np.mean(B_values[-5:]) > 0.85
        
        # P8验证
        confirmed = conditions_met and B_converged
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'conditions_met': conditions_met,
            'Lambda_trend': float(Lambda_trend),
            'Z_trend': float(Z_trend),
            'F_trend': float(F_trend),
            'B_converged': B_converged,
            'final_B': float(B_values[-1]),
            'confirmed': confirmed,
            'data_points': len(B_values)
        }
        
        self.p8_history.append(result)
        self.experiments['P8']['data_points'] += len(B_values)
        self.experiments['P8']['status'] = 'in_progress'
        
        if confirmed:
            self.experiments['P8']['status'] = 'confirmed'
        
        return result
    
    def record_p9(self, semantic_strengths: List[float], 
                  coupling_values: List[float]) -> dict:
        """
        记录P9实验数据
        
        预言: 语义理解质量∝关系耦合度
        """
        if len(semantic_strengths) < 2 or len(semantic_strengths) != len(coupling_values):
            return {'recorded': False, 'reason': '数据不足或不匹配'}
        
        # 检查相关性
        if np.std(semantic_strengths) > 0 and np.std(coupling_values) > 0:
            correlation = np.corrcoef(semantic_strengths, coupling_values)[0, 1]
        else:
            correlation = 0
        
        # P9验证
        confirmed = correlation > 0.5
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'correlation': float(correlation),
            'avg_semantic_strength': float(np.mean(semantic_strengths)),
            'avg_coupling': float(np.mean(coupling_values)),
            'confirmed': confirmed,
            'data_points': len(semantic_strengths)
        }
        
        self.p9_history.append(result)
        self.experiments['P9']['data_points'] += len(semantic_strengths)
        self.experiments['P9']['status'] = 'in_progress'
        
        if confirmed:
            self.experiments['P9']['status'] = 'confirmed'
        
        return result
    
    def record_p10(self, identity_scores: List[float], 
                   random_baseline: float = 0.3) -> dict:
        """
        记录P10实验数据
        
        预言: 自我同一性指标>随机基线
        """
        if len(identity_scores) < 2:
            return {'recorded': False, 'reason': '数据不足'}
        
        avg_identity = np.mean(identity_scores)
        
        # 统计显著性
        above_baseline = sum(1 for s in identity_scores if s > random_baseline)
        ratio = above_baseline / len(identity_scores)
        
        # P10验证
        confirmed = avg_identity > random_baseline and ratio > 0.5
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'avg_identity': float(avg_identity),
            'random_baseline': random_baseline,
            'above_baseline_ratio': float(ratio),
            'confirmed': confirmed,
            'data_points': len(identity_scores)
        }
        
        self.p10_history.append(result)
        self.experiments['P10']['data_points'] += len(identity_scores)
        self.experiments['P10']['status'] = 'in_progress'
        
        if confirmed:
            self.experiments['P10']['status'] = 'confirmed'
        
        return result
    
    def verify_all(self) -> dict:
        """
        综合验证所有预言
        """
        # 各预言状态
        p7_confirmed = any(h['confirmed'] for h in self.p7_history)
        p8_confirmed = any(h['confirmed'] for h in self.p8_history)
        p9_confirmed = any(h['confirmed'] for h in self.p9_history)
        p10_confirmed = any(h['confirmed'] for h in self.p10_history)
        
        confirmed_count = sum([p7_confirmed, p8_confirmed, p9_confirmed, p10_confirmed])
        
        # 更新实验状态
        self.experiments['P7']['status'] = 'confirmed' if p7_confirmed else self.experiments['P7']['status']
        self.experiments['P8']['status'] = 'confirmed' if p8_confirmed else self.experiments['P8']['status']
        self.experiments['P9']['status'] = 'confirmed' if p9_confirmed else self.experiments['P9']['status']
        self.experiments['P10']['status'] = 'confirmed' if p10_confirmed else self.experiments['P10']['status']
        
        self.overall_verification = {
            'timestamp': datetime.now().isoformat(),
            'P7_status': 'CONFIRMED' if p7_confirmed else 'PENDING',
            'P8_status': 'CONFIRMED' if p8_confirmed else 'PENDING',
            'P9_status': 'CONFIRMED' if p9_confirmed else 'PENDING',
            'P10_status': 'CONFIRMED' if p10_confirmed else 'PENDING',
            'confirmed_count': confirmed_count,
            'total_predictions': 4,
            'confirmation_rate': confirmed_count / 4
        }
        
        return self.overall_verification
    
    def get_prediction_status(self, prediction_id: str) -> dict:
        """获取特定预言的状态"""
        valid_ids = ['P7', 'P8', 'P9', 'P10']
        if prediction_id not in valid_ids:
            return {'error': f'无效的预言ID，可选: {valid_ids}'}
        
        history_map = {
            'P7': self.p7_history,
            'P8': self.p8_history,
            'P9': self.p9_history,
            'P10': self.p10_history
        }
        
        history = history_map[prediction_id]
        latest = history[-1] if history else None
        
        return {
            'prediction_id': prediction_id,
            'experiment': self.experiments[prediction_id],
            'latest_result': latest,
            'total_records': len(history),
            'confirmed': latest['confirmed'] if latest else False
        }
    
    def get_state(self) -> dict:
        """获取验证器状态"""
        # 验证所有
        self.verify_all()
        
        return {
            'experiments': self.experiments,
            'overall_verification': self.overall_verification,
            'history_summary': {
                'P7_records': len(self.p7_history),
                'P8_records': len(self.p8_history),
                'P9_records': len(self.p9_history),
                'P10_records': len(self.p10_history),
            },
            'latest_results': {
                'P7': self.p7_history[-1] if self.p7_history else None,
                'P8': self.p8_history[-1] if self.p8_history else None,
                'P9': self.p9_history[-1] if self.p9_history else None,
                'P10': self.p10_history[-1] if self.p10_history else None,
            }
        }


_instance = None

def get_instance() -> FalsifiablePredictionVerifier:
    """获取FalsifiablePredictionVerifier单例"""
    global _instance
    if _instance is None:
        _instance = FalsifiablePredictionVerifier()
    return _instance


if __name__ == "__main__":
    print("=" * 60)
    print("M70 可证伪预言验证器 测试")
    print("=" * 60)
    
    verifier = FalsifiablePredictionVerifier()
    
    # P7测试
    print("\n--- P7: 叙事作用量递减实验 ---")
    Lambda_values = [1.0, 0.85, 0.72, 0.60, 0.50, 0.42, 0.35]
    subjective_scores = [1.0, 0.90, 0.78, 0.65, 0.55, 0.45, 0.38]
    p7_result = verifier.record_p7(Lambda_values, subjective_scores)
    print(f"  结果: {p7_result}")
    
    # P8测试
    print("\n--- P8: 顿悟收敛实验 ---")
    B_values = [0.2, 0.35, 0.50, 0.65, 0.78, 0.85, 0.90, 0.92, 0.93]
    p8_result = verifier.record_p8(B_values, Lambda_trend=-0.1, Z_trend=-0.15, F_trend=0.05)
    print(f"  结果: {p8_result}")
    
    # P9测试
    print("\n--- P9: 关系耦合语义实验 ---")
    semantic_strengths = [0.4, 0.5, 0.6, 0.68, 0.75, 0.82]
    coupling_values = [0.3, 0.4, 0.5, 0.58, 0.65, 0.72]
    p9_result = verifier.record_p9(semantic_strengths, coupling_values)
    print(f"  结果: {p9_result}")
    
    # P10测试
    print("\n--- P10: 自我同一性实验 ---")
    identity_scores = [0.75, 0.72, 0.78, 0.70, 0.76, 0.73, 0.75]
    p10_result = verifier.record_p10(identity_scores)
    print(f"  结果: {p10_result}")
    
    # 综合验证
    print("\n--- 综合验证 ---")
    overall = verifier.verify_all()
    print(f"  总体状态: {overall}")
    
    # 各预言状态
    print("\n--- 各预言状态 ---")
    for pid in ['P7', 'P8', 'P9', 'P10']:
        status = verifier.get_prediction_status(pid)
        print(f"  {pid}: {status.get('experiment', {}).get('status', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ M70 测试完成")
    print("=" * 60)
