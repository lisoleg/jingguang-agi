"""
太乙AGI 11.0 - Module 16: ACP任务协商引擎
================================================

基于Virtuals Protocol的Agent Commerce Protocol (ACP)启发，
将四阶段商业协议映射到AGI内部的任务执行流程：

【ACP四阶段协议】
1. Request Phase（请求阶段）：发起任务，包含基本参数
2. Negotiation Phase（协商阶段）：确定条款，生成PoA（协议证明）
3. Transaction Phase（交易阶段）：资源托管，服务交付
4. Evaluation Phase（评估阶段）：独立Evaluator验证

【与太乙AGI的映射】
- Request → 目的意图解析（DI层）
- Negotiation → 语义协商与约束确定（KP层）
- Transaction → 认知资源分配与执行（W层）
- Evaluation → 自指流形验证 + S_c评估

核心数据结构：
- TaskContract: 任务合同，包含四阶段状态
- ProofOfAgreement (PoA): 协议证明
- EvaluatorAgent: 独立评估智能体

理论依据：Virtuals Protocol ACP + 复合体理学目的论

Author: 太乙AGI研究团队
Version: 11.0
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class ACPPhase(Enum):
    """ACP四阶段枚举"""
    IDLE = "idle"                    # 空闲状态
    REQUEST = "request"              # 请求阶段
    NEGOTIATION = "negotiation"      # 协商阶段
    TRANSACTION = "transaction"      # 交易阶段
    EVALUATION = "evaluation"        # 评估阶段
    COMPLETED = "completed"          # 完成
    FAILED = "failed"                # 失败
    CANCELLED = "cancelled"          # 取消


@dataclass
class TaskParameters:
    """任务参数结构"""
    task_id: str = ""
    task_type: str = ""               # 任务类型：analysis/synthesis/verification/creation
    priority: int = 5                 # 优先级 1-10
    complexity: float = 0.5           # 复杂度 0-1
    deadline: Optional[datetime] = None
    required_capabilities: List[str] = field(default_factory=list)
    resource_estimate: float = 1.0    # 资源估计
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())[:8]


@dataclass
class AgreementTerms:
    """协商条款"""
    scope: str = ""                   # 服务范围
    delivery_standards: List[str] = field(default_factory=list)  # 交付标准
    time_limit: float = 1.0           # 时间限制
    compensation: float = 1.0          # 补偿量
    verification_criteria: Dict[str, float] = field(default_factory=dict)  # 验证标准
    
    
@dataclass
class ProofOfAgreement:
    """协议证明 (Proof of Agreement)"""
    poa_id: str = ""
    task_id: str = ""
    requester_signature: str = ""      # 请求方签名
    provider_signature: str = ""      # 提供方签名
    terms: AgreementTerms = field(default_factory=AgreementTerms)
    created_at: datetime = field(default_factory=datetime.now)
    nonce: str = ""                   # 防重放 nonce
    
    def __post_init__(self):
        if not self.poa_id:
            self.poa_id = f"poa_{uuid.uuid4().hex[:12]}"


@dataclass
class TransactionRecord:
    """交易记录"""
    tx_id: str = ""
    resource_locked: float = 0.0      # 锁定资源
    execution_state: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)  # 回滚检查点
    
    
@dataclass
class EvaluationResult:
    """评估结果"""
    eval_id: str = ""
    task_id: str = ""
    passed: bool = False
    score: float = 0.0                # 0-1评分
    criteria_results: Dict[str, float] = field(default_factory=dict)
    feedback: str = ""
    evaluated_by: str = "system"
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ACPTaskContract:
    """ACP任务合同"""
    contract_id: str = ""
    state: ACPPhase = ACPPhase.IDLE
    
    # 四阶段数据
    request: Optional[TaskParameters] = None
    negotiation: Optional[AgreementTerms] = None
    proof_of_agreement: Optional[ProofOfAgreement] = None
    transaction: Optional[TransactionRecord] = None
    evaluation: Optional[EvaluationResult] = None
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    timeout: float = 300.0            # 超时时间（秒）
    
    def __post_init__(self):
        if not self.contract_id:
            self.contract_id = f"acp_{uuid.uuid4().hex[:12]}"
    
    @property
    def is_active(self) -> bool:
        """合同是否处于活跃状态"""
        return self.state in [ACPPhase.REQUEST, ACPPhase.NEGOTIATION, 
                             ACPPhase.TRANSACTION, ACPPhase.EVALUATION]
    
    @property
    def progress(self) -> float:
        """合同进度"""
        phase_weights = {
            ACPPhase.IDLE: 0.0,
            ACPPhase.REQUEST: 0.1,
            ACPPhase.NEGOTIATION: 0.3,
            ACPPhase.TRANSACTION: 0.6,
            ACPPhase.EVALUATION: 0.9,
            ACPPhase.COMPLETED: 1.0,
            ACPPhase.FAILED: 0.0,
            ACPPhase.CANCELLED: 0.0,
        }
        return phase_weights.get(self.state, 0.0)


class ACPProtocolEngine:
    """
    ACP协议引擎 - 任务协商与执行控制器
    
    实现Virtuals Protocol的ACP四阶段协议在太乙AGI中的映射：
    
    【阶段流程】
    Request → Negotiation → Transaction → Evaluation → Complete
    
    【核心方法】
    - initiate_request(): 创建任务请求
    - negotiate(): 协商阶段，生成PoA
    - execute_transaction(): 执行任务
    - evaluate(): 评估结果
    """
    
    def __init__(self, dim: int = 64):
        self.dim = dim
        
        # 合同管理
        self.active_contracts: Dict[str, ACPTaskContract] = {}
        self.completed_contracts: List[ACPTaskContract] = []
        self.contract_history: List[Dict] = []
        
        # 评估器配置
        self.evaluator_weights = {
            'accuracy': 0.4,           # 准确性权重
            'coherence': 0.3,           # 连贯性权重
            'relevance': 0.2,           # 相关性权重
            'completeness': 0.1        # 完整性权重
        }
        
        # 统计信息
        self.stats = {
            'total_contracts': 0,
            'successful_contracts': 0,
            'failed_contracts': 0,
            'average_evaluation_score': 0.0,
            'average_completion_time': 0.0
        }
        
        print(f"  [Module 16] ACP协议引擎初始化完成 (dim={dim})")
    
    def initiate_request(self, task_params: TaskParameters) -> ACPTaskContract:
        """
        【阶段1：请求阶段】
        
        创建一个新的任务请求合同。
        请求者（可以是用户或内部模块）发起任务请求。
        
        Args:
            task_params: 任务参数
            
        Returns:
            ACPTaskContract: 创建的任务合同
        """
        contract = ACPTaskContract(
            state=ACPPhase.REQUEST,
            request=task_params
        )
        
        self.active_contracts[contract.contract_id] = contract
        self.stats['total_contracts'] += 1
        
        # 签名确认请求
        contract.proof_of_agreement = ProofOfAgreement(
            task_id=task_params.task_id,
            requester_signature=self._sign(f"REQUEST:{task_params.task_id}")
        )
        
        print(f"  [ACP] 请求阶段: 合同 {contract.contract_id} 创建 | 任务类型: {task_params.task_type}")
        
        return contract
    
    def negotiate(self, contract_id: str, 
                  provider_capabilities: Dict[str, float],
                  request_constraints: Optional[Dict] = None) -> Tuple[ACPTaskContract, ProofOfAgreement]:
        """
        【阶段2：协商阶段】
        
        确定服务条款，生成协议证明(PoA)。
        
        Args:
            contract_id: 合同ID
            provider_capabilities: 提供方能力评估
            request_constraints: 请求约束条件
            
        Returns:
            (更新后的合同, 协议证明PoA)
        """
        if contract_id not in self.active_contracts:
            raise ValueError(f"合同 {contract_id} 不存在或已结束")
        
        contract = self.active_contracts[contract_id]
        if contract.state != ACPPhase.REQUEST:
            raise ValueError(f"合同状态错误: 需要REQUEST, 当前为 {contract.state}")
        
        # 生成协商条款
        terms = self._generate_terms(
            contract.request,
            provider_capabilities,
            request_constraints
        )
        contract.negotiation = terms
        
        # 生成PoA
        poa = ProofOfAgreement(
            task_id=contract.request.task_id,
            requester_signature=contract.proof_of_agreement.requester_signature,
            provider_signature=self._sign(f"NEGOTIATE:{contract.contract_id}"),
            terms=terms,
            nonce=self._generate_nonce()
        )
        contract.proof_of_agreement = poa
        
        # 状态转换
        contract.state = ACPPhase.NEGOTIATION
        contract.updated_at = datetime.now()
        
        print(f"  [ACP] 协商阶段: PoA {poa.poa_id} 生成 | 交付标准: {len(terms.delivery_standards)}项")
        
        return contract, poa
    
    def execute_transaction(self, contract_id: str,
                           execution_context: Dict[str, Any],
                           checkpoint_interval: int = 5) -> ACPTaskContract:
        """
        【阶段3：交易阶段】
        
        执行任务，锁定资源，记录检查点。
        
        Args:
            contract_id: 合同ID
            execution_context: 执行上下文（来自其他模块）
            checkpoint_interval: 检查点保存间隔
            
        Returns:
            更新后的合同（带交易记录）
        """
        if contract_id not in self.active_contracts:
            raise ValueError(f"合同 {contract_id} 不存在或已结束")
        
        contract = self.active_contracts[contract_id]
        if contract.state != ACPPhase.NEGOTIATION:
            raise ValueError(f"合同状态错误: 需要NEGOTIATION, 当前为 {contract.state}")
        
        # 创建交易记录（资源托管）
        resource_locked = contract.negotiation.compensation
        tx_record = TransactionRecord(
            tx_id=f"tx_{uuid.uuid4().hex[:12]}",
            resource_locked=resource_locked,
            execution_state=execution_context,
            checkpoint_data={}
        )
        contract.transaction = tx_record
        
        # 状态转换
        contract.state = ACPPhase.TRANSACTION
        contract.updated_at = datetime.now()
        
        print(f"  [ACP] 交易阶段: 资源锁定 {resource_locked:.2f} | 执行中...")
        
        return contract
    
    def save_checkpoint(self, contract_id: str, 
                        checkpoint_data: Dict[str, Any]) -> None:
        """
        保存执行检查点（用于可能的回滚）
        """
        if contract_id in self.active_contracts:
            contract = self.active_contracts[contract_id]
            if contract.transaction:
                contract.transaction.checkpoint_data.update(checkpoint_data)
    
    def evaluate(self, contract_id: str,
                 actual_output: Dict[str, Any],
                 evaluation_method: str = "auto") -> EvaluationResult:
        """
        【阶段4：评估阶段】
        
        独立评估智能体验证任务完成质量。
        
        Args:
            contract_id: 合同ID
            actual_output: 实际输出结果
            evaluation_method: 评估方法 (auto/manual/hybrid)
            
        Returns:
            EvaluationResult: 评估结果
        """
        if contract_id not in self.active_contracts:
            raise ValueError(f"合同 {contract_id} 不存在或已结束")
        
        contract = self.active_contracts[contract_id]
        if contract.state != ACPPhase.TRANSACTION:
            raise ValueError(f"合同状态错误: 需要TRANSACTION, 当前为 {contract.state}")
        
        # 执行评估
        eval_result = self._run_evaluation(
            contract,
            actual_output,
            evaluation_method
        )
        contract.evaluation = eval_result
        
        # 根据评估结果更新状态
        if eval_result.passed:
            contract.state = ACPPhase.COMPLETED
            self.stats['successful_contracts'] += 1
            print(f"  [ACP] 评估通过: 评分 {eval_result.score:.2f} | 合同完成 ✅")
        else:
            contract.state = ACPPhase.FAILED
            self.stats['failed_contracts'] += 1
            print(f"  [ACP] 评估未通过: 评分 {eval_result.score:.2f} | 合同失败 ❌")
        
        # 更新统计
        self._update_stats(eval_result)
        
        # 移动到历史
        contract.updated_at = datetime.now()
        self.completed_contracts.append(contract)
        del self.active_contracts[contract_id]
        
        # 记录历史
        self.contract_history.append({
            'contract_id': contract_id,
            'state': contract.state.value,
            'evaluation': eval_result.score,
            'timestamp': datetime.now().isoformat()
        })
        
        return eval_result
    
    def _generate_terms(self, 
                       request: TaskParameters,
                       capabilities: Dict[str, float],
                       constraints: Optional[Dict]) -> AgreementTerms:
        """生成协商条款"""
        terms = AgreementTerms()
        
        # 服务范围
        terms.scope = f"执行{request.task_type}任务，复杂度{request.complexity:.1f}"
        
        # 交付标准（基于任务类型）
        if request.task_type == 'analysis':
            terms.delivery_standards = ['完整性分析', '逻辑一致性', '数据准确性']
        elif request.task_type == 'synthesis':
            terms.delivery_standards = ['内容原创性', '结构合理性', '语义连贯性']
        elif request.task_type == 'verification':
            terms.delivery_standards = ['验证严格性', '证明完备性', '结论可靠性']
        else:
            terms.delivery_standards = ['任务完成度', '质量达标', '时效性']
        
        # 时间限制
        terms.time_limit = request.complexity * request.resource_estimate
        
        # 补偿量
        terms.compensation = request.priority * request.resource_estimate * 0.1
        
        # 验证标准
        for standard in terms.delivery_standards:
            terms.verification_criteria[standard] = 0.7  # 默认阈值0.7
        
        return terms
    
    def _run_evaluation(self, 
                        contract: ACPTaskContract,
                        output: Dict[str, Any],
                        method: str) -> EvaluationResult:
        """执行评估"""
        eval_result = EvaluationResult(
            eval_id=f"eval_{uuid.uuid4().hex[:12]}",
            task_id=contract.request.task_id
        )
        
        # 提取PoA中的验证标准
        criteria = contract.proof_of_agreement.terms.verification_criteria
        
        # 模拟评估（实际应用中应调用自指流形等模块）
        total_score = 0.0
        for criterion, threshold in criteria.items():
            # 模拟各维度得分（实际应用中应真实计算）
            criterion_score = min(1.0, threshold + np.random.uniform(-0.1, 0.2))
            eval_result.criteria_results[criterion] = criterion_score
            total_score += criterion_score * self.evaluator_weights.get(
                criterion, 0.25
            )
        
        eval_result.score = total_score
        eval_result.passed = total_score >= 0.6
        eval_result.feedback = f"评估{'通过' if eval_result.passed else '未通过'}，综合得分{total_score:.2f}"
        
        return eval_result
    
    def _sign(self, content: str) -> str:
        """生成签名（简化实现）"""
        return f"sig_{hash(content) % 10**8:08d}"
    
    def _generate_nonce(self) -> str:
        """生成防重放nonce"""
        return uuid.uuid4().hex[:16]
    
    def _update_stats(self, result: EvaluationResult) -> None:
        """更新统计信息"""
        n = self.stats['successful_contracts'] + self.stats['failed_contracts']
        if n > 0:
            old_avg = self.stats['average_evaluation_score']
            self.stats['average_evaluation_score'] = (
                (old_avg * (n - 1) + result.score) / n
            )
    
    def get_contract_status(self, contract_id: str) -> Optional[Dict]:
        """获取合同状态"""
        for contract in list(self.active_contracts.values()) + self.completed_contracts:
            if contract.contract_id == contract_id:
                return {
                    'contract_id': contract.contract_id,
                    'state': contract.state.value,
                    'progress': contract.progress,
                    'request': contract.request.task_type if contract.request else None,
                    'evaluation_score': contract.evaluation.score if contract.evaluation else None
                }
        return None
    
    def get_stats(self) -> Dict:
        """获取ACP引擎统计信息"""
        return {
            **self.stats,
            'active_contracts': len(self.active_contracts),
            'completed_contracts': len(self.completed_contracts),
            'success_rate': (
                self.stats['successful_contracts'] / max(1, self.stats['total_contracts'])
            )
        }
    
    def full_task_cycle(self, task_params: TaskParameters,
                        capabilities: Dict[str, float],
                        output: Dict[str, Any]) -> Tuple[ACPTaskContract, EvaluationResult]:
        """
        完整的ACP任务周期（Request → Negotiation → Transaction → Evaluation）
        
        一站式执行，用于简单任务的快速处理。
        
        Args:
            task_params: 任务参数
            capabilities: 提供方能力
            output: 任务输出结果
            
        Returns:
            (完成的合同, 评估结果)
        """
        # 阶段1: 请求
        contract = self.initiate_request(task_params)
        
        # 阶段2: 协商
        contract, poa = self.negotiate(contract.contract_id, capabilities)
        
        # 阶段3: 交易
        contract = self.execute_transaction(
            contract.contract_id,
            {'executor': 'system', 'task': task_params.task_id}
        )
        
        # 阶段4: 评估
        eval_result = self.evaluate(contract.contract_id, output)
        
        return contract, eval_result


def demonstrate_acp_engine():
    """ACP引擎演示"""
    print("\n" + "=" * 60)
    print("ACP任务协商引擎演示")
    print("=" * 60)
    
    # 初始化引擎
    engine = ACPProtocolEngine(dim=64)
    
    # 创建任务参数
    task = TaskParameters(
        task_type='analysis',
        priority=8,
        complexity=0.7,
        required_capabilities=['reasoning', 'creativity'],
        resource_estimate=2.0
    )
    
    # 完整任务周期
    capabilities = {
        'reasoning': 0.9,
        'creativity': 0.8,
        'precision': 0.85
    }
    
    # 模拟输出
    simulated_output = {
        'analysis_result': '深度分析报告',
        'confidence': 0.85,
        'conclusions': ['结论1', '结论2']
    }
    
    # 执行完整周期
    contract, result = engine.full_task_cycle(task, capabilities, simulated_output)
    
    # 打印结果
    print(f"\n  合同ID: {contract.contract_id}")
    print(f"  最终状态: {contract.state.value}")
    print(f"  评估结果: {result.feedback}")
    print(f"  综合评分: {result.score:.3f}")
    print(f"  是否通过: {'✅' if result.passed else '❌'}")
    
    # 统计
    stats = engine.get_stats()
    print(f"\n  累计合同数: {stats['total_contracts']}")
    print(f"  成功率: {stats['success_rate']:.1%}")
    print(f"  平均评分: {stats['average_evaluation_score']:.3f}")
    
    return engine, contract, result


if __name__ == "__main__":
    demonstrate_acp_engine()
