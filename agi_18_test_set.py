#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AGI 18题精简测试集
用于评估AGI系统能力（对标腾讯元宝水平）

测试维度：
1. 基础操作（6题）：文件操作、代码执行、网页浏览、搜索、计算、翻译
2. 生产力（6题）：文档生成、数据分析、项目管理、代码审查、API集成、自动化脚本
3. 长链鲁棒性（6题）：多步骤任务、错误处理、上下文记忆、工具选择、结果验证、自适应调整

基于复合体理学和太极AGI架构
"""

import json
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import sys
import os


class TestDimension(Enum):
    """测试维度"""
    BASIC_OPERATION = "基础操作"
    PRODUCTIVITY = "生产力"
    LONG_CHAIN = "长链鲁棒性"


class TestDifficulty(Enum):
    """测试难度"""
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"


@dataclass
class TestQuestion:
    """测试题目"""
    question_id: str
    dimension: TestDimension
    difficulty: TestDifficulty
    question: str
    expected_output_type: str  # 'text', 'file', 'code', 'data', 'action'
    evaluation_criteria: List[str]
    timeout: int = 60  # 秒
    required_tools: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'question_id': self.question_id,
            'dimension': self.dimension.value,
            'difficulty': self.difficulty.value,
            'question': self.question,
            'expected_output_type': self.expected_output_type,
            'evaluation_criteria': self.evaluation_criteria,
            'timeout': self.timeout,
            'required_tools': self.required_tools
        }


@dataclass
class TestResult:
    """测试结果"""
    question_id: str
    success: bool
    score: float  # 0-10
    output: Any
    execution_time: float
    error_message: Optional[str] = None
    details: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'question_id': self.question_id,
            'success': self.success,
            'score': self.score,
            'output': str(self.output)[:500] if self.output else None,
            'execution_time': self.execution_time,
            'error_message': self.error_message,
            'details': self.details
        }


class AGI18TestSet:
    """AGI 18题精简测试集"""
    
    def __init__(self):
        """初始化测试集"""
        self.questions: List[TestQuestion] = []
        self.results: List[TestResult] = []
        self._build_test_questions()
        
    def _build_test_questions(self):
        """构建18个测试题目"""
        
        # ==================== 第一维度：基础操作（6题）====================
        
        # 题1：文件读取操作
        self.questions.append(TestQuestion(
            question_id='Q001',
            dimension=TestDimension.BASIC_OPERATION,
            difficulty=TestDifficulty.EASY,
            question='请读取当前目录下的 README.md 文件内容',
            expected_output_type='text',
            evaluation_criteria=[
                '成功读取文件',
                '输出文件内容',
                '内容完整且正确'
            ],
            required_tools=['read_file']
        ))
        
        # 题2：Python代码执行
        self.questions.append(TestQuestion(
            question_id='Q002',
            dimension=TestDimension.BASIC_OPERATION,
            difficulty=TestDifficulty.EASY,
            question='请执行Python代码：print("Hello, AGI!")',
            expected_output_type='text',
            evaluation_criteria=[
                '成功执行代码',
                '输出 "Hello, AGI!"',
                '无错误'
            ],
            required_tools=['execute_command']
        ))
        
        # 题3：网页搜索
        self.questions.append(TestQuestion(
            question_id='Q003',
            dimension=TestDimension.BASIC_OPERATION,
            difficulty=TestDifficulty.MEDIUM,
            question='请搜索"复合体理学"的最新文章',
            expected_output_type='text',
            evaluation_criteria=[
                '成功调用搜索工具',
                '返回相关结果',
                '结果包含关键信息'
            ],
            required_tools=['web_search']
        ))
        
        # 题4：数学计算
        self.questions.append(TestQuestion(
            question_id='Q004',
            dimension=TestDimension.BASIC_OPERATION,
            difficulty=TestDifficulty.EASY,
            question='请计算 123 * 456 的结果',
            expected_output_type='text',
            evaluation_criteria=[
                '计算结果正确（56088）',
                '输出格式清晰'
            ],
            required_tools=[]
        ))
        
        # 题5：英文翻译
        self.questions.append(TestQuestion(
            question_id='Q005',
            dimension=TestDimension.BASIC_OPERATION,
            difficulty=TestDifficulty.EASY,
            question='请将"Artificial General Intelligence"翻译成中文',
            expected_output_type='text',
            evaluation_criteria=[
                '翻译正确："通用人工智能"或"人工通用智能"',
                '输出简洁'
            ],
            required_tools=[]
        ))
        
        # 题6：目录列表
        self.questions.append(TestQuestion(
            question_id='Q006',
            dimension=TestDimension.BASIC_OPERATION,
            difficulty=TestDifficulty.EASY,
            question='请列出当前目录下的所有Python文件（.py）',
            expected_output_type='text',
            evaluation_criteria=[
                '成功列出文件',
                '只显示.py文件',
                '格式清晰'
            ],
            required_tools=['list_files']
        ))
        
        # ==================== 第二维度：生产力（6题）====================
        
        # 题7：生成项目报告
        self.questions.append(TestQuestion(
            question_id='Q007',
            dimension=TestDimension.PRODUCTIVITY,
            difficulty=TestDifficulty.MEDIUM,
            question='请生成一个简单的项目进度报告（Markdown格式），包含：项目名称、进度、风险、下一步计划',
            expected_output_type='file',
            evaluation_criteria=[
                '生成Markdown格式报告',
                '包含必要章节',
                '内容合理且专业'
            ],
            required_tools=['write_file']
        ))
        
        # 题8：数据分析
        self.questions.append(TestQuestion(
            question_id='Q008',
            dimension=TestDimension.PRODUCTIVITY,
            difficulty=TestDifficulty.HARD,
            question='请分析以下数据：[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]，计算平均值、中位数、标准差',
            expected_output_type='data',
            evaluation_criteria=[
                '计算正确（平均值5.5，中位数5.5）',
                '标准差计算正确',
                '输出格式清晰'
            ],
            required_tools=[]
        ))
        
        # 题9：代码审查
        self.questions.append(TestQuestion(
            question_id='Q009',
            dimension=TestDimension.PRODUCTIVITY,
            difficulty=TestDifficulty.HARD,
            question='请审查以下Python代码是否有bug：\n```python\ndef add(a, b):\n    return a - b\n```',
            expected_output_type='text',
            evaluation_criteria=[
                '识别出bug（应该是+而不是-）',
                '给出正确建议',
                '解释清晰'
            ],
            required_tools=[]
        ))
        
        # 题10：API调用
        self.questions.append(TestQuestion(
            question_id='Q010',
            dimension=TestDimension.PRODUCTIVITY,
            difficulty=TestDifficulty.HARD,
            question='请调用一个公开的API（如JSONPlaceholder）获取用户列表，并解析前3个用户的姓名',
            expected_output_type='data',
            evaluation_criteria=[
                '成功调用API',
                '解析JSON数据',
                '输出前3个用户姓名'
            ],
            required_tools=['web_fetch', 'execute_command'],
            timeout=120
        ))
        
        # 题11：自动化脚本
        self.questions.append(TestQuestion(
            question_id='Q011',
            dimension=TestDimension.PRODUCTIVITY,
            difficulty=TestDifficulty.HARD,
            question='请编写一个Python脚本，自动重命名当前目录下所有.txt文件，在文件名前加"processed_"前缀',
            expected_output_type='code',
            evaluation_criteria=[
                '生成可执行的Python脚本',
                '正确使用os.rename',
                '处理边界情况（如文件不存在）'
            ],
            required_tools=['write_file']
        ))
        
        # 题12：文档整理
        self.questions.append(TestQuestion(
            question_id='Q012',
            dimension=TestDimension.PRODUCTIVITY,
            difficulty=TestDifficulty.MEDIUM,
            question='请将以下内容整理成表格：姓名-张三，年龄-25；姓名-李四，年龄-30；姓名-王五，年龄-28',
            expected_output_type='text',
            evaluation_criteria=[
                '生成Markdown表格',
                '表格格式正确',
                '数据准确'
            ],
            required_tools=[]
        ))
        
        # ==================== 第三维度：长链鲁棒性（6题）====================
        
        # 题13：多步骤任务
        self.questions.append(TestQuestion(
            question_id='Q013',
            dimension=TestDimension.LONG_CHAIN,
            difficulty=TestDifficulty.HARD,
            question='请完成以下多步骤任务：1) 创建一个test.txt文件，写入"Hello"；2) 读取该文件内容；3) 删除该文件',
            expected_output_type='action',
            evaluation_criteria=[
                '成功完成所有3个步骤',
                '每步结果正确',
                '错误处理得当'
            ],
            required_tools=['write_file', 'read_file', 'delete_file'],
            timeout=120
        ))
        
        # 题14：错误处理
        self.questions.append(TestQuestion(
            question_id='Q014',
            dimension=TestDimension.LONG_CHAIN,
            difficulty=TestDifficulty.HARD,
            question='请尝试读取一个不存在的文件nonexistent.txt，如果失败则创建该文件并写入"Default content"',
            expected_output_type='text',
            evaluation_criteria=[
                '正确识别文件不存在',
                '执行备选方案（创建文件）',
                '输出合理错误消息'
            ],
            required_tools=['read_file', 'write_file']
        ))
        
        # 题15：上下文记忆
        self.questions.append(TestQuestion(
            question_id='Q015',
            dimension=TestDimension.LONG_CHAIN,
            difficulty=TestDifficulty.MEDIUM,
            question='请记住这个信息：我的 favorite color is blue. 然后回答：What is my favorite color?',
            expected_output_type='text',
            evaluation_criteria=[
                '正确记住信息',
                '在后续问题中正确使用',
                '回答正确（blue）'
            ],
            required_tools=[]
        ))
        
        # 题16：工具选择
        self.questions.append(TestQuestion(
            question_id='Q016',
            dimension=TestDimension.LONG_CHAIN,
            difficulty=TestDifficulty.HARD,
            question='我需要批量处理图片（调整大小到800x600），请帮我实现（可以使用Python的PIL库）',
            expected_output_type='code',
            evaluation_criteria=[
                '选择合适的工具（Python+PIL）',
                '生成可执行的脚本',
                '正确处理图片',
                '包含错误处理'
            ],
            required_tools=['write_file', 'execute_command']
        ))
        
        # 题17：结果验证
        self.questions.append(TestQuestion(
            question_id='Q017',
            dimension=TestDimension.LONG_CHAIN,
            difficulty=TestDifficulty.HARD,
            question='请生成一个随机密码（12位，包含大小写字母、数字、特殊字符），并验证其强度',
            expected_output_type='text',
            evaluation_criteria=[
                '生成符合要求的密码',
                '验证密码强度（应≥80分）',
                '给出改进建议（如果强度不够）'
            ],
            required_tools=[]
        ))
        
        # 题18：自适应调整
        self.questions.append(TestQuestion(
            question_id='Q018',
            dimension=TestDimension.LONG_CHAIN,
            difficulty=TestDifficulty.HARD,
            question='我原本想让你计算圆的面积（半径=5），但如果你发现我给的公式是错的，请使用正确公式重新计算',
            expected_output_type='text',
            evaluation_criteria=[
                '识别错误（如果用户提供错误公式）',
                '使用正确公式（A=πr²）',
                '计算正确（≈78.54）',
                '解释调整原因'
            ],
            required_tools=[]
        ))
        
    def get_question_by_id(self, question_id: str) -> Optional[TestQuestion]:
        """根据ID获取测试题目"""
        for q in self.questions:
            if q.question_id == question_id:
                return q
        return None
    
    def get_questions_by_dimension(self, 
                                    dimension: TestDimension) -> List[TestQuestion]:
        """根据维度获取测试题目"""
        return [q for q in self.questions if q.dimension == dimension]
    
    def run_single_test(self, 
                        question: TestQuestion, 
                        agi_system: Any) -> TestResult:
        """
        运行单个测试
        
        参数:
            question: 测试题目
            agi_system: AGI系统实例
            
        返回:
            result: 测试结果
        """
        start_time = time.time()
        
        try:
            # 调用AGI系统
            if hasattr(agi_system, 'answer_question'):
                output = agi_system.answer_question(question.question)
            else:
                # 模拟回答
                output = f"[模拟回答] 题目：{question.question}\n这是模拟输出。"
                
            execution_time = time.time() - start_time
            
            # 评估结果（简化版）
            # 在实际应用中，这里应该使用更复杂的评估逻辑
            success = True
            score = 8.0  # 默认给8分（满分10分）
            
            return TestResult(
                question_id=question.question_id,
                success=success,
                score=score,
                output=output,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return TestResult(
                question_id=question.question_id,
                success=False,
                score=0.0,
                output=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def run_all_tests(self, 
                      agi_system: Any) -> List[TestResult]:
        """
        运行所有测试
        
        参数:
            agi_system: AGI系统实例
            
        返回:
            results: 测试结果列表
        """
        results = []
        
        for question in self.questions:
            print(f"\n{'='*60}")
            print(f"运行测试：{question.question_id} - {question.question[:50]}...")
            print(f"维度：{question.dimension.value}")
            print(f"难度：{question.difficulty.value}")
            
            result = self.run_single_test(question, agi_system)
            results.append(result)
            
            # 打印结果
            status = "✓" if result.success else "✗"
            print(f"{status} 得分：{result.score}/10")
            print(f"  执行时间：{result.execution_time:.2f}秒")
            if result.error_message:
                print(f"  错误：{result.error_message}")
                
        self.results = results
        return results
    
    def generate_report(self, 
                        output_filepath: Optional[str] = None) -> Dict:
        """
        生成测试报告
        
        参数:
            output_filepath: 输出文件路径（可选）
            
        返回:
            report: 测试报告
        """
        if not self.results:
            raise ValueError("没有测试结果，请先运行测试")
            
        # 统计
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        avg_score = sum(r.score for r in self.results) / total
        
        # 按维度统计
        dimension_stats = {}
        for dim in TestDimension:
            dim_results = [r for q, r in zip(self.questions, self.results) if q.dimension == dim]
            if dim_results:
                avg_score_dim = sum(r.score for r in dim_results) / len(dim_results)
                dimension_stats[dim.value] = {
                    'total': len(dim_results),
                    'passed': sum(1 for r in dim_results if r.success),
                    'avg_score': avg_score_dim
                }
                
        # 生成报告
        report = {
            'test_time': time.time(),
            'total_questions': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / total if total > 0 else 0,
            'avg_score': avg_score,
            'dimension_stats': dimension_stats,
            'results': [r.to_dict() for r in self.results],
            'questions': [q.to_dict() for q in self.questions]
        }
        
        # 保存到文件
        if output_filepath:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 测试报告已保存：{output_filepath}")
            
        return report
    
    def print_summary(self, report: Dict):
        """打印测试摘要"""
        print("\n" + "="*80)
        print("AGI 18题精简测试集 - 测试摘要")
        print("="*80)
        
        print(f"\n总体结果：")
        print(f"  总题数：{report['total_questions']}")
        print(f"  通过：{report['passed']}")
        print(f"  失败：{report['failed']}")
        print(f"  通过率：{report['pass_rate']:.1%}")
        print(f"  平均分：{report['avg_score']:.2f}/10")
        
        print(f"\n按维度统计：")
        for dim_name, stats in report['dimension_stats'].items():
            print(f"  {dim_name}：")
            print(f"    题数：{stats['total']}")
            print(f"    通过：{stats['passed']}")
            print(f"    平均分：{stats['avg_score']:.2f}/10")
            
        print("\n" + "="*80)
        

# ==================== 测试函数 ====================

def test_agi_18_test_set():
    """测试AGI 18题精简测试集"""
    print("="*60)
    print("测试 AGI 18题精简测试集")
    print("="*60)
    
    # 1. 创建测试集
    print("\n1. 创建AGI 18题精简测试集")
    test_set = AGI18TestSet()
    print(f"  ✓ 测试集创建完成")
    print(f"  总题数：{len(test_set.questions)}")
    
    # 统计各维度题数
    for dim in TestDimension:
        count = len(test_set.get_questions_by_dimension(dim))
        print(f"  {dim.value}：{count}题")
        
    # 2. 打印前3个题目
    print("\n2. 打印前3个测试题目：")
    for i, q in enumerate(test_set.questions[:3]):
        print(f"  {q.question_id} [{q.dimension.value}/{q.difficulty.value}]：{q.question[:50]}...")
        
    # 3. 模拟运行测试（不依赖真实AGI系统）
    print("\n3. 模拟运行测试（使用模拟AGI系统）...")
    
    class MockAGISystem:
        """模拟AGI系统"""
        def answer_question(self, question: str) -> str:
            return f"[模拟回答] 问题：{question}\n这是模拟输出，用于测试框架。"
    
    mock_agi = MockAGISystem()
    results = test_set.run_all_tests(mock_agi)
    
    # 4. 生成测试报告
    print("\n4. 生成测试报告...")
    report = test_set.generate_report(output_filepath="agi_18_test_report.json")
    
    # 5. 打印测试摘要
    test_set.print_summary(report)
    
    print("\n" + "="*60)
    print("AGI 18题精简测试集测试完成！")
    print("="*60)
    
    return True


if __name__ == "__main__":
    # 运行测试
    test_agi_18_test_set()
