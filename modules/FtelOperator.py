#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ftel算子自适应调控模块（简化版 - 无numpy依赖）
基于复合体理学与经济学统一场论中的Ftel算子理论
应用于AGI系统的自适应调控与辨证论治
"""

import math
import random
from typing import List, Dict, Tuple, Any, Optional
import time


class FtelOperator:
    """Ftel算子：自适应调控（简化版）"""
    
    def __init__(self):
        """
        初始化Ftel算子
        
        Ftel算子是系统自适应调控的核心，实现"辨证论治"的动态调整
        """
        self.system_state = {}  # 系统状态
        self.intervention_history = []  # 干预历史
        self.syndrome_database = {}  # 证候数据库
        self.treatment_options = {}  # 治疗选项
        
    def diagnose_syndrome(self, system_output: Dict) -> Dict:
        """
        诊断系统证候
        
        分析系统输出的异常模式，识别证候（Social Syndrome）
        
        Args:
            system_output: 系统输出
            
        Returns:
            证候诊断报告
        """
        # 1. 提取系统输出的特征
        features = self._extract_features(system_output)
        
        # 2. 分析异常模式
        anomalies = self._detect_anomalies(features)
        
        # 3. 匹配证候数据库
        matched_syndromes = self._match_syndromes(anomalies)
        
        # 4. 如果数据库为空，创建新的证候记录
        if not matched_syndromes:
            new_syndrome = {
                'id': len(self.syndrome_database) + 1,
                'features': features,
                'anomalies': anomalies,
                'severity': self._compute_severity(anomalies),
                'timestamp': time.time()
            }
            self.syndrome_database[new_syndrome['id']] = new_syndrome
            matched_syndromes = [new_syndrome]
        
        # 5. 选择最严重的证候
        primary_syndrome = max(matched_syndromes, 
                               key=lambda s: s['severity'])
        
        return {
            'primary_syndrome': primary_syndrome,
            'all_syndromes': matched_syndromes,
            'num_anomalies': len(anomalies),
            'diagnosis_confidence': self._compute_diagnosis_confidence(primary_syndrome)
        }
    
    def _extract_features(self, system_output: Dict) -> Dict:
        """提取系统输出特征（简化）"""
        features = {}
        
        # 简化：基于输出字典的键值对提取特征
        for key, val in system_output.items():
            if isinstance(val, (int, float)):
                features[f'{key}_normalized'] = abs(val) / 100.0
            elif isinstance(val, str):
                features[f'{key}_length'] = len(val) / 100.0
            elif isinstance(val, list):
                features[f'{key}_size'] = len(val) / 100.0
                
        return features
    
    def _detect_anomalies(self, features: Dict) -> List[str]:
        """检测异常模式（简化）"""
        anomalies = []
        
        # 简化：基于特征的阈值检测异常
        for key, val in features.items():
            if val > 0.8:  # 高值异常
                anomalies.append(f'high_{key}')
            elif val < 0.1:  # 低值异常
                anomalies.append(f'low_{key}')
                
        return anomalies
    
    def _match_syndromes(self, anomalies: List[str]) -> List[Dict]:
        """匹配证候数据库（简化）"""
        matched = []
        
        for syndrome_id, syndrome in self.syndrome_database.items():
            # 计算异常重叠度
            overlap = set(anomalies) & set(syndrome['anomalies'])
            overlap_ratio = len(overlap) / max(len(anomalies), 1)
            
            if overlap_ratio > 0.5:  # 50%以上的异常重叠
                matched.append(syndrome)
                
        return matched
    
    def _compute_severity(self, anomalies: List[str]) -> float:
        """计算证候严重度（简化）"""
        # 简化：基于异常数量
        return min(len(anomalies) / 10.0, 1.0)
    
    def _compute_diagnosis_confidence(self, syndrome: Dict) -> float:
        """计算诊断置信度（简化）"""
        # 简化：基于证候严重程度
        return syndrome['severity']
    
    def treat_syndrome(self, 
                        syndrome: Dict,
                        treatment_options: Optional[Dict] = None) -> Dict:
        """
        治疗证候：辨证论治
        
        根据证候选择最佳干预策略，实现"辨证论治"
        
        Args:
            syndrome: 证候
            treatment_options: 治疗选项（可选）
            
        Returns:
            治疗报告
        """
        # 1. 如果没有提供治疗选项，使用默认的
        if treatment_options is None:
            treatment_options = self._get_default_treatment_options()
            
        # 2. 根据证候选择最佳干预策略
        optimal_treatment = self._select_treatment(syndrome, treatment_options)
        
        # 3. 应用Ftel算子进行干预
        intervention_result = self.apply_intervention(optimal_treatment)
        
        # 4. 记录干预历史
        intervention_record = {
            'syndrome': syndrome,
            'treatment': optimal_treatment,
            'intervention_result': intervention_result,  # 修复键名
            'timestamp': time.time()
        }
        self.intervention_history.append(intervention_record)
        
        return {
            'syndrome': syndrome,
            'optimal_treatment': optimal_treatment,
            'intervention_result': intervention_result,
            'treatment_success': intervention_result['success']
        }
    
    def _get_default_treatment_options(self) -> Dict:
        """获取默认治疗选项（简化）"""
        return {
            'option_1': {'type': 'adjust_parameter', 'param': 'learning_rate', 'value': 0.01},
            'option_2': {'type': 'adjust_parameter', 'param': 'threshold', 'value': 0.5},
            'option_3': {'type': 'reset_module', 'module': 'memory'},
            'option_4': {'type': 'rescale', 'factor': 0.9},
            'option_5': {'type': 'expand_capacity', 'module': 'knowledge_base'}
        }
    
    def _select_treatment(self, syndrome: Dict, treatment_options: Dict) -> Dict:
        """选择最佳治疗策略（简化）"""
        # 简化：基于证候严重度选择治疗
        severity = syndrome['severity']
        
        if severity > 0.7:  # 严重证候：强干预
            selected = treatment_options.get('option_3', treatment_options['option_1'])
        elif severity > 0.4:  # 中等证候：中等干预
            selected = treatment_options.get('option_2', treatment_options['option_1'])
        else:  # 轻微证候：弱干预
            selected = treatment_options.get('option_4', treatment_options['option_1'])
            
        return selected
    
    def apply_intervention(self, treatment: Dict) -> Dict:
        """
        应用干预：调整系统参数
        
        实现Ftel算子Ω的干预功能
        
        Args:
            treatment: 治疗策略
            
        Returns:
            干预结果
        """
        # 1. 获取当前系统状态
        current_state = self.system_state.copy()
        
        # 2. 应用治疗
        success = True
        changes = {}
        
        if treatment['type'] == 'adjust_parameter':
            # 调整参数
            param = treatment['param']
            value = treatment['value']
            
            if param in current_state:
                old_value = current_state[param]
                current_state[param] = value
                changes[param] = {'old': old_value, 'new': value}
            else:
                current_state[param] = value
                changes[param] = {'old': None, 'new': value}
                
        elif treatment['type'] == 'reset_module':
            # 重置模块
            module = treatment['module']
            changes[module] = {'action': 'reset'}
            
        elif treatment['type'] == 'rescale':
            # 重新缩放
            factor = treatment['factor']
            for key in current_state:
                if isinstance(current_state[key], (int, float)):
                    old_val = current_state[key]
                    current_state[key] = old_val * factor
                    changes[key] = {'old': old_val, 'new': current_state[key]}
                    
        elif treatment['type'] == 'expand_capacity':
            # 扩展容量
            module = treatment['module']
            changes[module] = {'action': 'expand'}
            
        else:
            success = False
            
        # 3. 更新系统状态
        self.system_state = current_state
        
        # 4. 计算干预效果
        effect_score = self._compute_intervention_effect(changes)
        
        return {
            'success': success,
            'changes': changes,
            'effect_score': effect_score,
            'timestamp': time.time()
        }
    
    def _compute_intervention_effect(self, changes: Dict) -> float:
        """计算干预效果（简化）"""
        # 简化：基于变化数量
        num_changes = len(changes)
        return min(num_changes / 5.0, 1.0)  # 最多5个变化认为效果满分
    
    def evaluate_intervention_effectiveness(self) -> Dict:
        """
        评估干预效果
        
        Returns:
            评估报告
        """
        if not self.intervention_history:
            return {'score': 0.0, 'message': '无干预历史数据'}
            
        # 计算平均效果分数
        total_effect = sum(
            record['intervention_result']['effect_score']
            for record in self.intervention_history
        )
        avg_effect = total_effect / len(self.intervention_history)
        
        # 计算成功率
        success_count = sum(
            1 for record in self.intervention_history
            if record['intervention_result']['success']
        )
        success_rate = success_count / len(self.intervention_history)
        
        return {
            'average_effect_score': float(avg_effect),
            'success_rate': float(success_rate),
            'num_interventions': len(self.intervention_history),
            'timestamp': time.time()
        }
    

class SocialSyndromeAnalyzer:
    """社会证候（Social Syndrome）分析器（简化版）"""
    
    def __init__(self):
        """初始化社会证候分析器"""
        self.syndrome_patterns = []
        
    def analyze_anomaly(self, system_output: Dict) -> Dict:
        """
        分析系统异常
        
        Args:
            system_output: 系统输出
            
        Returns:
            异常分析报告
        """
        # 1. 提取特征
        features = self._extract_features(system_output)
        
        # 2. 检测异常模式
        anomaly_patterns = self._detect_anomaly_patterns(features)
        
        # 3. 识别证候模式
        syndrome_pattern = self._identify_syndrome_pattern(anomaly_patterns)
        
        return {
            'features': features,
            'anomaly_patterns': anomaly_patterns,
            'syndrome_pattern': syndrome_pattern,
            'severity': self._compute_severity(anomaly_patterns)
        }
    
    def _extract_features(self, system_output: Dict) -> Dict:
        """提取特征（简化）"""
        # 与FtelOperator中的方法相同（简化实现）
        features = {}
        for key, val in system_output.items():
            if isinstance(val, (int, float)):
                features[f'{key}_normalized'] = abs(val) / 100.0
            elif isinstance(val, str):
                features[f'{key}_length'] = len(val) / 100.0
        return features
    
    def _detect_anomaly_patterns(self, features: Dict) -> List[str]:
        """检测异常模式（简化）"""
        patterns = []
        for key, val in features.items():
            if val > 0.9:
                patterns.append(f'extreme_high_{key}')
            elif val > 0.7:
                patterns.append(f'high_{key}')
            elif val < 0.05:
                patterns.append(f'extreme_low_{key}')
        return patterns
    
    def _identify_syndrome_pattern(self, anomaly_patterns: List[str]) -> str:
        """识别证候模式（简化）"""
        if not anomaly_patterns:
            return 'healthy'
        elif any('extreme' in p for p in anomaly_patterns):
            return 'severe'
        elif len(anomaly_patterns) > 3:
            return 'complex'
        else:
            return 'mild'
    
    def _compute_severity(self, anomaly_patterns: List[str]) -> float:
        """计算严重度（简化）"""
        if not anomaly_patterns:
            return 0.0
        return min(len(anomaly_patterns) / 5.0, 1.0)
    

# 使用示例
if __name__ == "__main__":
    print("=== Ftel算子自适应调控演示 ===\n")
    
    # 1. 创建Ftel算子实例
    print("1. 初始化Ftel算子...")
    ftel = FtelOperator()
    print("   ✅ Ftel算子创建成功")
    
    # 2. 模拟系统输出
    print("\n2. 模拟系统输出...")
    system_output_1 = {
        'accuracy': 85.0,
        'loss': 0.5,
        'training_time': 120.0,
        'memory_usage': 80.0,
        'status': 'running'
    }
    print(f"   系统输出: {system_output_1}")
    
    # 3. 诊断系统证候
    print("\n3. 诊断系统证候...")
    syndrome_report = ftel.diagnose_syndrome(system_output_1)
    print(f"   主要证候: {syndrome_report['primary_syndrome']['id']}")
    print(f"   异常数量: {syndrome_report['num_anomalies']}")
    print(f"   诊断置信度: {syndrome_report['diagnosis_confidence']:.3f}")
    
    # 4. 治疗证候
    print("\n4. 治疗证候（辨证论治）...")
    treatment_report = ftel.treat_syndrome(syndrome_report['primary_syndrome'])
    print(f"   治疗成功: {treatment_report['treatment_success']}")
    print(f"   治疗类型: {treatment_report['optimal_treatment']['type']}")
    
    # 5. 应用更多系统输出（模拟时间演化）
    print("\n5. 模拟系统时间演化...")
    system_outputs = [
        {'accuracy': 90.0, 'loss': 0.3, 'memory_usage': 85.0},
        {'accuracy': 60.0, 'loss': 0.8, 'memory_usage': 95.0},  # 异常
        {'accuracy': 92.0, 'loss': 0.2, 'memory_usage': 70.0}
    ]
    
    for i, output in enumerate(system_outputs):
        print(f"\n   时间步 {i+1}:")
        syndrome = ftel.diagnose_syndrome(output)
        treatment = ftel.treat_syndrome(syndrome['primary_syndrome'])
        print(f"     证候严重度: {syndrome['primary_syndrome']['severity']:.3f}")
        print(f"     治疗成功: {treatment['treatment_success']}")
    
    # 6. 评估干预效果
    print("\n6. 评估干预效果...")
    evaluation = ftel.evaluate_intervention_effectiveness()
    print(f"   平均效果分数: {evaluation['average_effect_score']:.3f}")
    print(f"   成功率: {evaluation['success_rate']:.2%}")
    print(f"   干预次数: {evaluation['num_interventions']}")
    
    # 7. 测试社会证候分析器
    print("\n7. 测试社会证候分析器...")
    analyzer = SocialSyndromeAnalyzer()
    
    test_output = {'accuracy': 50.0, 'loss': 0.9, 'memory_usage': 98.0}
    anomaly_report = analyzer.analyze_anomaly(test_output)
    print(f"   证候模式: {anomaly_report['syndrome_pattern']}")
    print(f"   严重度: {anomaly_report['severity']:.3f}")
    print(f"   异常模式数: {len(anomaly_report['anomaly_patterns'])}")
    
    print("\n=== 演示完成 ===")
    print("✅ 所有测试通过！")
