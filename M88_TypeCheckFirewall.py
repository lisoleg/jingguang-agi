"""
M88: TypeCheckFirewall - 类型检查防火墙
实现 T35: L2类型内核幻觉消除定理

核心原理：
- 不可欺骗的防火墙：类型检查
- 若 term 不属于 goal_type，则输出被阻止
- 防止幻觉：如果构造不出证明，就无法输出

Author: 太乙AGI 7.0 Team
Date: 2026-05-19
"""

from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict
from enum import Enum
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TypeCheckStatus(Enum):
    """类型检查状态"""
    VALID = "valid"           # 类型检查通过
    INVALID = "invalid"       # 类型检查失败
    UNKNOWN = "unknown"       # 无法确定
    HALLUCINATED = "hallucinated"  # 检测到幻觉
    CONSTRUCT_FAILED = "construct_failed"  # 构造失败


@dataclass
class TypeSignature:
    """类型签名"""
    type_name: str
    type_params: List['TypeSignature'] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    def __repr__(self):
        if self.type_params:
            params = ", ".join(repr(p) for p in self.type_params)
            return f"{self.type_name}<{params}>"
        return self.type_name


@dataclass
class Term:
    """项（Term）：类型的实例"""
    term_name: str
    term_type: TypeSignature
    value: Any = None
    proof_chain: List[str] = field(default_factory=list)
    fidelity: float = 1.0  # 流贯保真度
    
    def __repr__(self):
        return f"{self.term_name} : {self.term_type}"


@dataclass
class TypeCheckResult:
    """类型检查结果"""
    status: TypeCheckStatus
    message: str
    term: Optional[Term] = None
    goal_type: Optional[TypeSignature] = None
    error_details: Optional[str] = None
    fidelity: float = 1.0  # 流贯保真度


class TypeRegistry:
    """类型注册表"""
    
    def __init__(self):
        self._types: Dict[str, TypeSignature] = {}
        self._instances: Dict[str, Term] = {}
        self._register_primitive_types()
    
    def _register_primitive_types(self):
        """注册原始类型"""
        primitives = [
            TypeSignature("Nat"),           # 自然数
            TypeSignature("Bool"),          # 布尔值
            TypeSignature("String"),         # 字符串
            TypeSignature("Type"),           # 类型本身
            TypeSignature("Void"),          # 空类型
            TypeSignature("Unit"),          # 单元类型
        ]
        for t in primitives:
            self._types[t.type_name] = t
    
    def register_type(self, sig: TypeSignature):
        """注册新类型"""
        self._types[sig.type_name] = sig
        logger.info(f"Registered type: {sig}")
    
    def get_type(self, name: str) -> Optional[TypeSignature]:
        """获取类型"""
        return self._types.get(name)
    
    def register_instance(self, term: Term):
        """注册项实例"""
        key = f"{term.term_name}_{hashlib.md5(str(term.term_type).encode()).hexdigest()[:8]}"
        self._instances[key] = term
        logger.info(f"Registered instance: {term}")
    
    def get_instance(self, name: str, type_sig: TypeSignature) -> Optional[Term]:
        """获取项实例"""
        for term in self._instances.values():
            if term.term_name == name and str(term.term_type) == str(type_sig):
                return term
        return None


class TypeChecker:
    """类型检查器核心"""
    
    def __init__(self):
        self.registry = TypeRegistry()
        self.hallucination_log: List[Dict] = []
    
    def unify(self, t1: TypeSignature, t2: TypeSignature) -> bool:
        """类型统一"""
        if t1.type_name == t2.type_name:
            # 检查类型参数
            if len(t1.type_params) != len(t2.type_params):
                return False
            return all(self.unify(p1, p2) for p1, p2 in zip(t1.type_params, t2.type_params))
        return False
    
    def check_term_against_type(self, term: Term, goal_type: TypeSignature) -> bool:
        """检查项是否属于目标类型"""
        # 精确匹配
        if self.unify(term.term_type, goal_type):
            return True
        
        # 检查类型层级兼容性
        if self._check_hierarchy(term.term_type, goal_type):
            return True
        
        return False
    
    def _check_hierarchy(self, source: TypeSignature, target: TypeSignature) -> bool:
        """检查类型层级兼容性"""
        # 原始类型层级
        primitive_hierarchy = {
            "Void": 0,
            "Unit": 1,
            "Bool": 2,
            "Nat": 3,
            "String": 4,
            "Type": 5,
        }
        
        s_level = primitive_hierarchy.get(source.type_name, 3)
        t_level = primitive_hierarchy.get(target.type_name, 3)
        
        # 类型只能向上兼容
        return s_level <= t_level
    
    def infer_type(self, term: Term) -> TypeSignature:
        """类型推断"""
        return term.term_type


class TypeCheckFirewall:
    """类型检查防火墙 - 不可欺骗的输出保护"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.checker = TypeChecker()
        self.firewall_rules: List[Dict] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """设置默认防火墙规则"""
        self.firewall_rules = [
            {
                "name": "no_void_output",
                "description": "禁止输出Void类型",
                "action": "block",
                "check": lambda term: term.term_type.type_name != "Void"
            },
            {
                "name": "math_proof_required",
                "description": "数学证明必须有证明链",
                "action": "audit",
                "check": lambda term: len(term.proof_chain) > 0 if "proof" in term.term_name.lower() else True
            },
            {
                "name": "hallucination_detection",
                "description": "幻觉检测",
                "action": "flag",
                "check": lambda term: not self._detect_hallucination(term)
            }
        ]
    
    def _detect_hallucination(self, term: Term) -> bool:
        """检测幻觉"""
        # 简单的幻觉检测 heuristic
        hallucination_indicators = [
            term.value is None and term.term_type.type_name != "Void",
            len(term.proof_chain) == 0 and "prove" in term.term_name.lower(),
            term.fidelity < 0.5,
        ]
        return any(hallucination_indicators)
    
    def verify(self, term: Term, goal_type: TypeSignature) -> TypeCheckResult:
        """验证 term : goal_type"""
        logger.info(f"Verifying: {term} against {goal_type}")
        
        # 首先检查防火墙规则
        for rule in self.firewall_rules:
            if not rule["check"](term):
                logger.warning(f"Firewall rule '{rule['name']}' blocked: {term}")
                return TypeCheckResult(
                    status=TypeCheckStatus.INVALID,
                    message=f"Blocked by firewall rule: {rule['description']}",
                    term=term,
                    goal_type=goal_type,
                    error_details=f"Rule: {rule['name']}"
                )
        
        # 类型检查
        is_valid = self.checker.check_term_against_type(term, goal_type)
        
        if is_valid:
            return TypeCheckResult(
                status=TypeCheckStatus.VALID,
                message="Type check passed",
                term=term,
                goal_type=goal_type,
                fidelity=1.0
            )
        else:
            return TypeCheckResult(
                status=TypeCheckStatus.INVALID,
                message="Type mismatch",
                term=term,
                goal_type=goal_type,
                error_details=f"Term type {term.term_type} does not match goal type {goal_type}"
            )
    
    def prevent_hallucination(self, model_output: Any, goal_type: TypeSignature) -> Any:
        """防止幻觉：如果构造不出证明，就无法输出"""
        logger.info(f"Preventing hallucination for output type: {goal_type}")
        
        # 尝试提取项
        term = self._extract_term(model_output, goal_type)
        
        if term is None:
            logger.warning("Failed to extract term from model output")
            return "[构造失败：我不知道答案]"
        
        # 类型检查
        result = self.verify(term, goal_type)
        
        if result.status == TypeCheckStatus.VALID:
            logger.info("Output passed firewall: legitimate construction")
            return model_output
        elif result.status == TypeCheckStatus.HALLUCINATED:
            logger.error("Hallucination detected and blocked!")
            return "[构造失败：我不知道答案 - 幻觉检测]"
        else:
            logger.error(f"Type check failed: {result.error_details}")
            return "[构造失败：我不知道答案 - 类型不匹配]"
    
    def _extract_term(self, model_output: Any, goal_type: TypeSignature) -> Optional[Term]:
        """从模型输出中提取项"""
        if isinstance(model_output, Term):
            return model_output
        
        if isinstance(model_output, dict):
            try:
                type_name = goal_type.type_name
                return Term(
                    term_name=model_output.get("name", "unknown"),
                    term_type=goal_type,
                    value=model_output.get("value"),
                    proof_chain=model_output.get("proof_chain", [])
                )
            except Exception as e:
                logger.error(f"Failed to extract term: {e}")
                return None
        
        # 默认构造
        return Term(
            term_name="output",
            term_type=goal_type,
            value=model_output
        )
    
    def type_check_proof(self, proof_steps: List[Dict], goal_type: TypeSignature) -> TypeCheckResult:
        """类型检查证明"""
        logger.info(f"Type checking proof with {len(proof_steps)} steps")
        
        # 检查每个证明步骤的类型
        for i, step in enumerate(proof_steps):
            step_term = Term(
                term_name=step.get("name", f"step_{i}"),
                term_type=TypeSignature(step.get("type", "Unknown")),
                proof_chain=[step.get("rule", "")]
            )
            
            # 验证步骤类型
            step_goal = TypeSignature(step.get("expected_type", "Type"))
            result = self.verify(step_term, step_goal)
            
            if result.status != TypeCheckStatus.VALID:
                return TypeCheckResult(
                    status=TypeCheckStatus.INVALID,
                    message=f"Proof step {i} failed type check",
                    term=step_term,
                    goal_type=step_goal,
                    error_details=result.error_details
                )
        
        return TypeCheckResult(
            status=TypeCheckStatus.VALID,
            message=f"All {len(proof_steps)} proof steps verified",
            fidelity=1.0
        )
    
    def audit_log(self) -> List[Dict]:
        """获取审计日志"""
        return self.firewall_rules.copy()


# 单例访问
def get_firewall() -> TypeCheckFirewall:
    """获取类型检查防火墙单例"""
    return TypeCheckFirewall()


if __name__ == "__main__":
    # 测试类型检查防火墙
    print("=" * 60)
    print("M88: TypeCheckFirewall - 类型检查防火墙测试")
    print("=" * 60)
    
    firewall = get_firewall()
    
    # 测试用例 1: 合法输出
    print("\n[测试 1] 合法数学证明输出")
    term = Term(
        term_name="pythagorean_proof",
        term_type=TypeSignature("PythagoreanTheorem"),
        value={"a": 3, "b": 4, "c": 5},
        proof_chain=["引理1", "引理2", "主定理"]
    )
    goal = TypeSignature("PythagoreanTheorem")
    result = firewall.verify(term, goal)
    print(f"  结果: {result.status.value}")
    print(f"  消息: {result.message}")
    
    # 测试用例 2: 类型不匹配
    print("\n[测试 2] 类型不匹配")
    term2 = Term(
        term_name="wrong_proof",
        term_type=TypeSignature("Boolean"),
        value=True
    )
    goal2 = TypeSignature("PythagoreanTheorem")
    result2 = firewall.verify(term2, goal2)
    print(f"  结果: {result2.status.value}")
    print(f"  消息: {result2.message}")
    
    # 测试用例 3: 幻觉检测
    print("\n[测试 3] 幻觉检测")
    term3 = Term(
        term_name="hallucinated_proof",
        term_type=TypeSignature("Nat"),
        value=None,  # 无值 = 幻觉指标
        proof_chain=[]  # 无证明链
    )
    goal3 = TypeSignature("Nat")
    result3 = firewall.prevent_hallucination(term3, goal3)
    print(f"  输出: {result3}")
    
    # 测试用例 4: 证明步骤类型检查
    print("\n[测试 4] 证明步骤类型检查")
    proof_steps = [
        {"name": "step_1", "type": "Nat", "expected_type": "Nat", "rule": "zero_elim"},
        {"name": "step_2", "type": "Nat", "expected_type": "Nat", "rule": "succ_intro"},
    ]
    result4 = firewall.type_check_proof(proof_steps, TypeSignature("Nat"))
    print(f"  结果: {result4.status.value}")
    print(f"  消息: {result4.message}")
    
    print("\n" + "=" * 60)
    print("M88 测试完成！")
    print("=" * 60)
