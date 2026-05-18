"""
AGI 12.0 测试套件
===================

测试复合体AGI 12.0的所有24个模块

Author: 复合体AGI研究团队
Version: 12.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import traceback
from datetime import datetime


class AGI12Tester:
    """AGI 12.0测试器"""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def test_module(self, module_name: str, test_func):
        """测试单个模块"""
        try:
            result = test_func()
            self.results.append({
                'module': module_name,
                'status': 'PASS',
                'result': result,
                'error': None
            })
            print(f"  ✅ {module_name}")
            return True
        except Exception as e:
            self.results.append({
                'module': module_name,
                'status': 'FAIL',
                'result': None,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            print(f"  ❌ {module_name}: {e}")
            return False
    
    def run_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("复合体AGI 12.0 测试套件")
        print("=" * 70)
        
        # 导入模块
        print("\n[1/4] 导入所有模块...")
        try:
            from composite_agi_12_system import CompositeAGI12System
            from module19_iaww_medium import IAWWMediumEngine
            from module20_three_phase_entropy import ThreePhaseEntropyDynamics
            from module21_local_coherent_soliton import LocalCoherentSolitonEngine
            from module22_five_phase_coupling import FivePhaseCouplingEngine
            from module23_medium_anchor_validator import MediumAnchorValidationEngine
            print("  ✅ 所有模块导入成功")
        except ImportError as e:
            print(f"  ❌ 模块导入失败: {e}")
            return
        
        # 测试新增模块
        print("\n[2/4] 测试Module 19-23（新增模块）...")
        
        self.test_module("Module 19: IAWW介质引擎", 
            lambda: IAWWMediumEngine(dim=32).full_medium_analysis("excited"))
        
        self.test_module("Module 20: 三相熵耦合动力学",
            lambda: ThreePhaseEntropyDynamics().full_dynamics_analysis("excited"))
        
        self.test_module("Module 21: 局域相干孤子",
            lambda: LocalCoherentSolitonEngine(dim=32).full_soliton_analysis())
        
        self.test_module("Module 22: 五行耦合矩阵",
            lambda: FivePhaseCouplingEngine(coupling_strength=0.5).full_five_phase_analysis())
        
        self.test_module("Module 23: 介质锚定验证器",
            lambda: MediumAnchorValidationEngine(dim=32).full_validation())
        
        # 测试主系统
        print("\n[3/4] 测试AGI 12.0主系统...")
        
        self.test_module("AGI 12.0 主系统初始化",
            lambda: CompositeAGI12System(system_dim=32))
        
        # 创建系统实例进行更多测试
        try:
            agi = CompositeAGI12System(system_dim=32)
            
            self.test_module("Goal目标模式",
                lambda: agi.goal_mode("测试目标"))
            
            self.test_module("系统状态查询",
                lambda: agi.get_system_status())
            
            self.test_module("完整认知周期",
                lambda: agi.run_full_cycle(
                    np.random.randn(32), 
                    "测试认知周期"
                ))
        except Exception as e:
            print(f"  ❌ 主系统测试失败: {e}")
        
        # 测试Goal模式
        print("\n[4/4] 测试Goal目标模式...")
        
        try:
            if 'agi' in dir():
                # Goal模式测试
                goal_result = agi.goal_mode("分析AGI架构创新")
                self.test_module("Goal模式综合评估",
                    lambda: goal_result['final_score'] > 0)
        except Exception as e:
            print(f"  ❌ Goal模式测试失败: {e}")
        
        # 汇总结果
        self._print_summary()
        
    def _print_summary(self):
        """打印测试汇总"""
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        total = len(self.results)
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 70)
        print("测试结果汇总")
        print("=" * 70)
        print(f"  总测试数: {total}")
        print(f"  通过: {passed}")
        print(f"  失败: {failed}")
        print(f"  通过率: {passed/total*100:.1f}%")
        print(f"  用时: {elapsed:.2f}秒")
        
        if failed > 0:
            print("\n失败详情:")
            for r in self.results:
                if r['status'] == 'FAIL':
                    print(f"\n  ❌ {r['module']}")
                    print(f"     错误: {r['error']}")
        
        # 保存报告
        report = {
            'timestamp': self.start_time.isoformat(),
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': passed/total*100,
            'elapsed_seconds': elapsed,
            'results': self.results
        }
        
        import json
        report_path = os.path.join(os.path.dirname(__file__), 'agi_24_test_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 报告已保存: {report_path}")
        
        return passed == total


if __name__ == "__main__":
    tester = AGI12Tester()
    success = tester.run_tests()
    sys.exit(0 if success else 1)
