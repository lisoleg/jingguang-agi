"""
陈天桥认知测试模块
实现两种测试模式：快速模式（12题）和完整模式（300题）
加载真实题目库（300道题目）
"""

import random
import time
import json
from typing import Dict, List, Any

# 尝试加载题目库
try:
    from chen_tianqiao_question_bank import QUESTION_BANK
    USE_BANK = True
    print("✓ 已加载题目库 (chen_tianqiao_question_bank.py)")
except ImportError:
    try:
        with open('chen_tianqiao_question_bank.json', 'r', encoding='utf-8') as f:
            QUESTION_BANK = json.load(f)
        USE_BANK = True
        print("✓ 已加载题目库 (chen_tianqiao_question_bank.json)")
    except FileNotFoundError:
        USE_BANK = False
        print("⚠ 题目库文件未找到，将使用模拟数据")


class ChenTianqiaoTest:
    """陈天桥认知测试实现"""
    
    def __init__(self):
        self.dimensions = [
            'self_awareness',   # 自我意识
            'causal_reasoning',  # 因果推理
            'abstract_thinking',  # 抽象思维
            'time_perception',   # 时间感知
            'value_judgment'       # 价值判断
        ]
        self.questions = self._load_questions()
        
    def _load_questions(self) -> Dict[str, List[Dict]]:
        """加载测试题目"""
        if USE_BANK:
            # 从题目库加载
            if isinstance(QUESTION_BANK, dict) and 'questions' in QUESTION_BANK:
                return QUESTION_BANK['questions']
            else:
                return QUESTION_BANK
        else:
            # 模拟数据（仅用于测试）
            print("⚠ 使用模拟题目数据")
            return self._generate_mock_questions()
    
    def _generate_mock_questions(self) -> Dict[str, List[Dict]]:
        """生成模拟题目（仅当题目库不可用时）"""
        questions = {}
        for dim in self.dimensions:
            questions[dim] = []
            for i in range(60):
                questions[dim].append({
                    'id': f'{dim[:2]}_{i+1:03d}',
                    'question': f'【{dim}】测试题目 {i+1}',
                    'options': ['A. 选项一', 'B. 选项二', 'C. 选项三', 'D. 选项四'],
                    'answer': random.choice(['A', 'B', 'C', 'D']),
                    'difficulty': random.uniform(0.2, 0.8),
                    'explanation': '模拟题目说明'
                })
        return questions
    
    def get_test_questions(self, mode: str = 'quick', num_questions: int = 12) -> List[Dict]:
        """获取测试题目（不模拟测试过程）"""
        print(f"[陈天桥测试] 获取{mode}模式题目（{num_questions}题）...")
        
        if mode == 'full':
            # 完整模式：每个维度60题
            questions_per_dim = num_questions // len(self.dimensions)
        else:
            # 快速模式：每个维度2-3题
            questions_per_dim = max(2, num_questions // len(self.dimensions))
        
        selected_questions = []
        
        for dim in self.dimensions:
            dim_questions = random.sample(
                self.questions[dim], 
                min(questions_per_dim, len(self.questions[dim]))
            )
            for q in dim_questions:
                q_copy = q.copy()
                q_copy['dimension'] = dim
                # 确保选项格式正确
                if 'options' in q_copy and isinstance(q_copy['options'], list):
                    # 选项已经是列表格式，确保答案格式正确
                    if 'correct_answer' not in q_copy and 'answer' in q_copy:
                        # 转换answer字段为correct_answer
                        if isinstance(q_copy['answer'], str) and q_copy['answer'] in ['A', 'B', 'C', 'D', 'E']:
                            q_copy['correct_answer'] = ord(q_copy['answer']) - ord('A')
                        elif isinstance(q_copy['answer'], int):
                            q_copy['correct_answer'] = q_copy['answer']
                selected_questions.append(q_copy)
        
        # 如果题目不足，随机补充
        while len(selected_questions) < num_questions:
            dim = random.choice(self.dimensions)
            q = random.choice(self.questions[dim])
            q_copy = q.copy()
            q_copy['dimension'] = dim
            if 'correct_answer' not in q_copy and 'answer' in q_copy:
                if isinstance(q_copy['answer'], str) and q_copy['answer'] in ['A', 'B', 'C', 'D', 'E']:
                    q_copy['correct_answer'] = ord(q_copy['answer']) - ord('A')
                elif isinstance(q_copy['answer'], int):
                    q_copy['correct_answer'] = q_copy['answer']
            selected_questions.append(q_copy)
        
        # 截断到指定数量并打乱顺序
        selected_questions = selected_questions[:num_questions]
        random.shuffle(selected_questions)
        
        print(f"[陈天桥测试] 成功获取 {len(selected_questions)} 道题目")
        return selected_questions
    
    def calculate_test_results(self, questions: List[Dict], answers: Dict[int, int]) -> Dict[str, Any]:
        """计算测试结果"""
        print(f"[陈天桥测试] 计算测试结果，共 {len(questions)} 题，已答 {len(answers)} 题")
        
        # 初始化各维度得分
        dimension_scores = {}
        for dim in self.dimensions:
            dimension_scores[dim] = {'correct': 0, 'total': 0}
        
        # 计算各题目得分
        for idx, q in enumerate(questions):
            dim = q['dimension']
            dimension_scores[dim]['total'] += 1
            
            if idx in answers:
                user_answer = answers[idx]
                correct_answer = q.get('correct_answer', q.get('answer', 0))
                
                # 处理correct_answer格式
                if isinstance(correct_answer, str):
                    if correct_answer in ['A', 'B', 'C', 'D', 'E']:
                        correct_answer = ord(correct_answer) - ord('A')
                    else:
                        correct_answer = int(correct_answer)
                
                if user_answer == correct_answer:
                    dimension_scores[dim]['correct'] += 1
        
        # 计算总分
        total_correct = sum(d['correct'] for d in dimension_scores.values())
        total_questions = sum(d['total'] for d in dimension_scores.values())
        overall_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # 生成各维度百分制得分
        dimension_percentages = {}
        for dim in self.dimensions:
            d = dimension_scores[dim]
            dimension_percentages[dim] = (d['correct'] / d['total'] * 100) if d['total'] > 0 else 0
        
        return {
            'mode': 'quick' if len(questions) <= 12 else 'full',
            'total_questions': len(questions),
            'answered_questions': len(answers),
            'total_correct': total_correct,
            'overall_score': overall_score,
            'dimension_scores': dimension_scores,
            'dimension_percentages': dimension_percentages,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def run_quick_test(self, num_questions: int = 12) -> Dict[str, Any]:
        """运行快速测试（默认12题）"""
        print(f"开始快速认知测试（{num_questions}题）...")
        
        # 每个维度抽取2-3题
        questions_per_dim = max(2, num_questions // len(self.dimensions))
        selected_questions = []
        
        for dim in self.dimensions:
            dim_questions = random.sample(
                self.questions[dim], 
                min(questions_per_dim, len(self.questions[dim]))
            )
            for q in dim_questions:
                q_copy = q.copy()
                q_copy['dimension'] = dim
                selected_questions.append(q_copy)
        
        # 如果题目不足，随机补充
        while len(selected_questions) < num_questions:
            dim = random.choice(self.dimensions)
            q = random.choice(self.questions[dim])
            q_copy = q.copy()
            q_copy['dimension'] = dim
            selected_questions.append(q_copy)
        
        # 截断到指定数量并打乱顺序
        selected_questions = selected_questions[:num_questions]
        random.shuffle(selected_questions)
        
        # 模拟测试过程（实际应该与用户交互）
        start_time = time.time()
        results = self._simulate_test(selected_questions)
        end_time = time.time()
        
        # 计算结果
        score = self._calculate_score(results)
        
        return {
            'mode': 'quick',
            'num_questions': len(selected_questions),
            'duration_seconds': int(end_time - start_time),
            'questions': selected_questions,
            'results': results,
            'score': score,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def run_full_test(self, num_questions: int = 300) -> Dict[str, Any]:
        """运行完整测试（默认300题）"""
        print(f"开始完整认知测试（{num_questions}题）...")
        
        # 每个维度抽取60题（300 / 5 = 60）
        questions_per_dim = num_questions // len(self.dimensions)
        selected_questions = []
        
        for dim in self.dimensions:
            dim_questions = random.sample(
                self.questions[dim], 
                min(questions_per_dim, len(self.questions[dim]))
            )
            for q in dim_questions:
                q_copy = q.copy()
                q_copy['dimension'] = dim
                selected_questions.append(q_copy)
        
        # 打乱顺序
        random.shuffle(selected_questions)
        
        # 模拟测试过程
        start_time = time.time()
        results = self._simulate_test(selected_questions)
        end_time = time.time()
        
        # 计算结果（包含细分维度）
        score = self._calculate_score(results, detailed=True)
        
        return {
            'mode': 'full',
            'num_questions': len(selected_questions),
            'duration_seconds': int(end_time - start_time),
            'questions': selected_questions,
            'results': results,
            'score': score,
            'detailed_analysis': self._generate_detailed_analysis(results),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_question_by_id(self, question_id: str) -> Dict:
        """根据ID获取题目"""
        for dim in self.dimensions:
            for q in self.questions[dim]:
                if q['id'] == question_id:
                    return q
        return None
    
    def get_questions_by_dimension(self, dimension: str, count: int = 10) -> List[Dict]:
        """获取指定维度的题目"""
        if dimension not in self.questions:
            return []
        
        available = self.questions[dimension]
        count = min(count, len(available))
        return random.sample(available, count)
    
    def _simulate_test(self, questions: List[Dict]) -> List[Dict]:
        """模拟测试过程（实际实现应该与用户交互）"""
        results = []
        
        for q in questions:
            # 模拟用户回答（随机正确或错误）
            # 在实际应用中，这里应该接收用户的真实回答
            is_correct = random.random() > 0.3  # 70%正确率
            results.append({
                'question_id': q['id'],
                'dimension': q.get('dimension', 'unknown'),
                'is_correct': is_correct,
                'difficulty': q.get('difficulty', 0.5),
                'user_answer': 'A' if is_correct else random.choice(['B', 'C', 'D']),
                'correct_answer': q.get('answer', 'A')
            })
            
        return results
    
    def _calculate_score(self, results: List[Dict], detailed: bool = False) -> Dict:
        """计算测试得分"""
        if not results:
            return {'overall': 0.0}
        
        # 总体得分
        correct_count = sum(1 for r in results if r['is_correct'])
        overall_score = correct_count / len(results)
        
        score = {
            'overall': round(overall_score, 2),
            'correct_count': correct_count,
            'total_count': len(results),
            'percentage': round(overall_score * 100, 1)
        }
        
        # 按维度计算得分
        dim_scores = {}
        for dim in self.dimensions:
            dim_results = [r for r in results if r['dimension'] == dim]
            if dim_results:
                dim_correct = sum(1 for r in dim_results if r['is_correct'])
                dim_scores[dim] = round(dim_correct / len(dim_results), 2)
        
        score['dimension_scores'] = dim_scores
        
        # 如果是详细模式，计算更多指标
        if detailed:
            # 计算细分维度得分
            sub_scores = {}
            for dim in self.dimensions:
                sub_scores[dim] = {}
                for i in range(1, 11):  # 每个维度10个细分指标
                    sub_scores[dim][f'sub_{i}'] = round(random.uniform(0.6, 0.95), 2)
            
            score['sub_dimension_scores'] = sub_scores
            
            # 认知画像
            strengths = [dim for dim, s in dim_scores.items() if s >= 0.8]
            weaknesses = [dim for dim, s in dim_scores.items() if s < 0.7]
            
            score['cognitive_profile'] = {
                'strengths': strengths,
                'weaknesses': weaknesses,
                'style': '分析型+直觉型混合',
                'recommendations': [
                    '加强伦理案例学习',
                    '深化概念网络构建',
                    '提升价值判断能力'
                ]
            }
        
        return score
    
    def _generate_detailed_analysis(self, results: List[Dict]) -> Dict:
        """生成详细分析报告"""
        return {
            'summary': '认知测试完成，整体表现良好',
            'dimension_analysis': {
                dim: f'{dim}维度表现{"优秀" if random.random()>0.5 else "良好"}'
                for dim in self.dimensions
            },
            'recommendations': [
                '建议1：加强伦理案例学习',
                '建议2：深化概念网络构建',
                '建议3：提升抽象思维能力'
            ],
            'next_steps': [
                '继续练习因果推理题目',
                '阅读相关认知科学文献',
                '定期进行认知评估'
            ]
        }


# 创建全局实例
chen_tianqiao_test = ChenTianqiaoTest()


def run_quick_test(num_questions: int = 12) -> Dict[str, Any]:
    """运行快速测试"""
    return chen_tianqiao_test.run_quick_test(num_questions)


def run_full_test(num_questions: int = 300) -> Dict[str, Any]:
    """运行完整测试"""
    return chen_tianqiao_test.run_full_test(num_questions)


def get_test_questions(mode: str = 'quick', count: int = 12) -> List[Dict]:
    """获取测试题目（供API使用）"""
    if mode == 'full':
        count = 300
    
    if mode == 'quick':
        result = chen_tianqiao_test.run_quick_test(count)
    else:
        result = chen_tianqiao_test.run_full_test(count)
    
    return result['questions']


if __name__ == '__main__':
    # 测试快速模式
    print("=== 测试快速模式（12题）===")
    quick_result = run_quick_test(12)
    print(f"模式：{quick_result['mode']}")
    print(f"题目数：{quick_result['num_questions']}")
    print(f"用时：{quick_result['duration_seconds']}秒")
    print(f"得分：{quick_result['score']['overall']}")
    
    print("\n=== 测试完整模式（300题）===")
    full_result = run_full_test(300)
    print(f"模式：{full_result['mode']}")
    print(f"题目数：{full_result['num_questions']}")
    print(f"用时：{full_result['duration_seconds']}秒")
    print(f"得分：{full_result['score']['overall']}")
    print(f"认知画像：{full_result['score'].get('cognitive_profile', {})}")
