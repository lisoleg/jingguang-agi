#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具执行验证机制模块
为统一太乙AGI系统提供工具调用的安全验证和审计

功能：
1. 工具执行前验证（参数检查、权限检查、安全检查）
2. 工具执行后验证（结果检查、副作用检查）
3. 工具执行日志和审计
4. 与统一AGI系统的集成

基于复合体理学和太极AGI架构
"""

import json
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import inspect


class VerificationLevel(Enum):
    """验证级别"""
    LOOSE = "loose"        # 宽松：只检查基本参数
    MEDIUM = "medium"      # 中等：检查参数+权限
    STRICT = "strict"       # 严格：检查所有+审计


class VerificationResult(Enum):
    """验证结果"""
    PASSED = "passed"          # 通过
    FAILED = "failed"          # 失败
    WARNING = "warning"        # 警告（可通过）
    BLOCKED = "blocked"        # 被阻止（危险操作）


@dataclass
class ToolCallRecord:
    """工具调用记录"""
    call_id: str
    tool_name: str
    parameters: Dict
    caller: str                  # 调用者（哪个模块）
    timestamp: float
    verification_result: Optional[VerificationResult] = None
    execution_result: Optional[Dict] = None
    execution_time: Optional[float] = None
    side_effects: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'call_id': self.call_id,
            'tool_name': self.tool_name,
            'parameters': self.parameters,
            'caller': self.caller,
            'timestamp': self.timestamp,
            'verification_result': self.verification_result.value if self.verification_result else None,
            'execution_result': self.execution_result,
            'execution_time': self.execution_time,
            'side_effects': self.side_effects
        }


@dataclass
class VerificationRule:
    """验证规则"""
    rule_id: str
    rule_type: str              # 'parameter', 'permission', 'safety', '副作用'
    description: str
    check_function: Callable    # 检查函数
    level: VerificationLevel = VerificationLevel.MEDIUM
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'rule_id': self.rule_id,
            'rule_type': self.rule_type,
            'description': self.description,
            'level': self.level.value,
            'enabled': self.enabled
        }


class ToolVerificationEngine:
    """工具验证引擎"""
    
    def __init__(self, 
                 verification_level: VerificationLevel = VerificationLevel.MEDIUM):
        """
        初始化工具验证引擎
        
        参数:
            verification_level: 验证级别
        """
        self.verification_level = verification_level
        self.rules: List[VerificationRule] = []
        self.call_history: List[ToolCallRecord] = []
        self.max_history = 1000
        
        # 初始化默认规则
        self._init_default_rules()
        
    def _init_default_rules(self):
        """初始化默认验证规则"""
        
        # 规则1：参数类型检查
        self.rules.append(VerificationRule(
            rule_id='rule_001',
            rule_type='parameter',
            description='检查参数类型是否正确',
            check_function=self._check_parameter_types,
            level=VerificationLevel.LOOSE
        ))
        
        # 规则2：必需参数检查
        self.rules.append(VerificationRule(
            rule_id='rule_002',
            rule_type='parameter',
            description='检查必需参数是否存在',
            check_function=self._check_required_parameters,
            level=VerificationLevel.LOOSE
        ))
        
        # 规则3：路径安全检查
        self.rules.append(VerificationRule(
            rule_id='rule_003',
            rule_type='safety',
            description='检查文件路径是否安全（防止路径遍历攻击）',
            check_function=self._check_path_safety,
            level=VerificationLevel.MEDIUM
        ))
        
        # 规则4：危险操作检查
        self.rules.append(VerificationRule(
            rule_id='rule_004',
            rule_type='safety',
            description='检查是否包含危险操作（删除、格式化等）',
            check_function=self._check_dangerous_operations,
            level=VerificationLevel.STRICT
        ))
        
        # 规则5：权限检查
        self.rules.append(VerificationRule(
            rule_id='rule_005',
            rule_type='permission',
            description='检查调用者是否有足够权限',
            check_function=self._check_permissions,
            level=VerificationLevel.MEDIUM
        ))
        
    def verify_before_execution(self, 
                                tool_name: str, 
                                parameters: Dict,
                                caller: str) -> Tuple[VerificationResult, List[str]]:
        """
        执行前验证
        
        参数:
            tool_name: 工具名称
            parameters: 工具参数
            caller: 调用者
            
        返回:
            (result, messages): 验证结果和消息列表
        """
        messages = []
        all_passed = True
        blocked = False
        
        # 生成调用ID
        call_id = self._generate_call_id(tool_name, parameters, caller)
        
        # 创建调用记录
        record = ToolCallRecord(
            call_id=call_id,
            tool_name=tool_name,
            parameters=parameters,
            caller=caller,
            timestamp=time.time()
        )
        
        # 应用所有启用的规则
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            # 检查规则级别
            if self._is_rule_applicable(rule.level):
                try:
                    is_valid, msg = rule.check_function(tool_name, parameters, caller)
                    
                    if not is_valid:
                        if rule.level == VerificationLevel.STRICT:
                            blocked = True
                            messages.append(f"[BLOCKED] {rule.rule_id}: {msg}")
                        else:
                            messages.append(f"[WARNING] {rule.rule_id}: {msg}")
                            all_passed = False
                    else:
                        messages.append(f"[PASSED] {rule.rule_id}: {msg}")
                        
                except Exception as e:
                    messages.append(f"[ERROR] {rule.rule_id}: 检查失败 - {str(e)}")
                    all_passed = False
        
        # 确定验证结果
        if blocked:
            result = VerificationResult.BLOCKED
            record.verification_result = result
            messages.append(f"工具调用被阻止：{tool_name}")
        elif all_passed:
            result = VerificationResult.PASSED
            record.verification_result = result
            messages.append(f"验证通过：{tool_name}")
        else:
            result = VerificationResult.WARNING
            record.verification_result = result
            messages.append(f"验证警告（可通过）：{tool_name}")
            
        # 保存到历史
        self.call_history.append(record)
        if len(self.call_history) > self.max_history:
            self.call_history.pop(0)
            
        return result, messages
    
    def verify_after_execution(self, 
                               call_id: str, 
                               execution_result: Dict,
                               side_effects: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
        """
        执行后验证
        
        参数:
            call_id: 调用ID
            execution_result: 执行结果
            side_effects: 副作用列表（可选）
            
        返回:
            (is_valid, messages): 是否有效和消息列表
        """
        messages = []
        
        # 查找调用记录
        record = None
        for r in self.call_history:
            if r.call_id == call_id:
                record = r
                break
                
        if record is None:
            messages.append("[ERROR] 未找到调用记录")
            return False, messages
            
        # 更新执行结果
        record.execution_result = execution_result
        if side_effects:
            record.side_effects = side_effects
            
        # 验证执行结果
        is_valid = True
        
        # 检查1：执行是否成功
        if execution_result.get('status') == 'error':
            is_valid = False
            messages.append(f"[ERROR] 执行失败：{execution_result.get('message', 'Unknown error')}")
        else:
            messages.append("[PASSED] 执行成功")
            
        # 检查2：副作用检查
        if side_effects:
            for effect in side_effects:
                messages.append(f"[INFO] 副作用：{effect}")
                
        # 检查3：执行时间检查（防止无限循环）
        if record.execution_time and record.execution_time > 60:  # 超过60秒
            messages.append(f"[WARNING] 执行时间过长：{record.execution_time:.2f}秒")
            
        return is_valid, messages
    
    def _check_parameter_types(self, 
                              tool_name: str, 
                              parameters: Dict,
                              caller: str) -> Tuple[bool, str]:
        """
        检查参数类型
        
        返回:
            (is_valid, message)
        """
        # 简化版：检查基本类型
        for key, value in parameters.items():
            if key.startswith('_'):  # 私有参数跳过
                continue
                
            # 检查是否为可接受的类型
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                return False, f"参数 '{key}' 类型不正确：{type(value).__name__}"
                
        return True, "参数类型检查通过"
    
    def _check_required_parameters(self, 
                                  tool_name: str, 
                                  parameters: Dict,
                                  caller: str) -> Tuple[bool, str]:
        """
        检查必需参数
        
        返回:
            (is_valid, message)
        """
        # 简化版：常见必需参数
        required_params = {
            'read_file': ['file_path'],
            'write_file': ['file_path', 'content'],
            'execute_command': ['command'],
            'send_message': ['recipient', 'content']
        }
        
        if tool_name in required_params:
            for req_param in required_params[tool_name]:
                if req_param not in parameters:
                    return False, f"缺少必需参数：'{req_param}'"
                    
        return True, "必需参数检查通过"
    
    def _check_path_safety(self, 
                           tool_name: str, 
                           parameters: Dict,
                           caller: str) -> Tuple[bool, str]:
        """
        检查路径安全性（防止路径遍历攻击）
        
        返回:
            (is_valid, message)
        """
        # 需要检查路径的工具
        path_tools = ['read_file', 'write_file', 'delete_file']
        
        if tool_name in path_tools:
            file_path = parameters.get('file_path', '')
            
            # 检查路径遍历
            if '..' in file_path or '~' in file_path:
                return False, f"路径包含危险字符：{file_path}"
                
            # 检查绝对路径（防止访问系统目录）
            if file_path.startswith('/') or file_path.startswith('C:\\'):
                # 在实际应用中，这里应该检查是否在允许的目录内
                pass
                
        return True, "路径安全检查通过"
    
    def _check_dangerous_operations(self, 
                                   tool_name: str, 
                                   parameters: Dict,
                                   caller: str) -> Tuple[bool, str]:
        """
        检查危险操作
        
        返回:
            (is_valid, message)
        """
        dangerous_tools = ['delete_file', 'format_disk', 'execute_command']
        
        if tool_name in dangerous_tools:
            # 对于delete_file，检查是否有confirm参数
            if tool_name == 'delete_file':
                if not parameters.get('confirm', False):
                    return False, "删除文件需要confirm=True"
                    
            # 对于execute_command，检查命令是否危险
            if tool_name == 'execute_command':
                command = parameters.get('command', '').lower()
                dangerous_keywords = ['rm -rf', 'del /s', 'format', 'mkfs']
                for keyword in dangerous_keywords:
                    if keyword in command:
                        return False, f"命令包含危险关键字：{keyword}"
                        
        return True, "危险操作检查通过"
    
    def _check_permissions(self, 
                           tool_name: str, 
                           parameters: Dict,
                           caller: str) -> Tuple[bool, str]:
        """
        检查权限
        
        返回:
            (is_valid, message)
        """
        # 简化版：检查调用者权限
        # 在实际应用中，这里应该从系统获取调用者的权限
        
        # 假设某些工具需要特殊权限
        restricted_tools = ['delete_file', 'execute_command', 'access_sensitive_data']
        
        if tool_name in restricted_tools:
            # 检查caller是否有足够权限
            # 这里简化：只允许特定调用者
            allowed_callers = ['unified_system', 'agi_core']
            
            if caller not in allowed_callers:
                return False, f"调用者 '{caller}' 没有权限使用 '{tool_name}'"
                
        return True, "权限检查通过"
    
    def _is_rule_applicable(self, rule_level: VerificationLevel) -> bool:
        """
        检查规则是否适用（基于当前验证级别）
        
        返回:
            is_applicable: 是否适用
        """
        level_priority = {
            VerificationLevel.LOOSE: 1,
            VerificationLevel.MEDIUM: 2,
            VerificationLevel.STRICT: 3
        }
        
        return level_priority[rule_level] <= level_priority[self.verification_level]
    
    def _generate_call_id(self, 
                          tool_name: str, 
                          parameters: Dict,
                          caller: str) -> str:
        """
        生成调用ID
        
        返回:
            call_id: 调用ID（哈希值）
        """
        content = f"{tool_name}_{json.dumps(parameters, sort_keys=True)}_{caller}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get_verification_statistics(self) -> Dict:
        """获取验证统计信息"""
        total = len(self.call_history)
        passed = sum(1 for r in self.call_history if r.verification_result == VerificationResult.PASSED)
        failed = sum(1 for r in self.call_history if r.verification_result == VerificationResult.FAILED)
        warning = sum(1 for r in self.call_history if r.verification_result == VerificationResult.WARNING)
        blocked = sum(1 for r in self.call_history if r.verification_result == VerificationResult.BLOCKED)
        
        return {
            'total_calls': total,
            'passed': passed,
            'failed': failed,
            'warning': warning,
            'blocked': blocked,
            'pass_rate': passed / total if total > 0 else 0
        }
    
    def export_audit_log(self, 
                        filepath: str):
        """
        导出审计日志
        
        参数:
            filepath: 文件路径
        """
        log_data = {
            'export_time': time.time(),
            'total_records': len(self.call_history),
            'records': [r.to_dict() for r in self.call_history]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
            
        print(f"✓ 审计日志已导出：{filepath}")


# ==================== 测试函数 ====================

def test_tool_verification():
    """测试工具验证引擎"""
    print("=" * 60)
    print("测试 工具执行验证机制")
    print("=" * 60)
    
    # 1. 创建验证引擎
    print("\n1. 创建工具验证引擎")
    engine = ToolVerificationEngine(verification_level=VerificationLevel.MEDIUM)
    print(f"  ✓ 引擎创建完成")
    print(f"  验证级别：{engine.verification_level.value}")
    print(f"  规则数量：{len(engine.rules)}")
    
    # 2. 测试执行前验证（正常情况）
    print("\n2. 测试执行前验证（正常情况）")
    tool_name = "read_file"
    parameters = {
        'file_path': 'test.txt',
        'encoding': 'utf-8'
    }
    caller = "unified_system"
    
    result, messages = engine.verify_before_execution(
        tool_name=tool_name,
        parameters=parameters,
        caller=caller
    )
    
    print(f"  工具：{tool_name}")
    print(f"  验证结果：{result.value}")
    for msg in messages:
        print(f"    {msg}")
    
    # 3. 测试执行前验证（危险操作）
    print("\n3. 测试执行前验证（危险操作）")
    tool_name = "delete_file"
    parameters = {
        'file_path': '../../etc/passwd',  # 路径遍历攻击
        'confirm': False
    }
    caller = "unauthorized_caller"
    
    result, messages = engine.verify_before_execution(
        tool_name=tool_name,
        parameters=parameters,
        caller=caller
    )
    
    print(f"  工具：{tool_name}")
    print(f"  验证结果：{result.value}")
    for msg in messages:
        print(f"    {msg}")
    
    # 4. 测试执行后验证
    print("\n4. 测试执行后验证")
    call_id = engine.call_history[-1].call_id if engine.call_history else None
    
    if call_id:
        execution_result = {
            'status': 'success',
            'data': 'file content here'
        }
        side_effects = ['modified_file_metadata']
        
        is_valid, messages = engine.verify_after_execution(
            call_id=call_id,
            execution_result=execution_result,
            side_effects=side_effects
        )
        
        print(f"  调用ID：{call_id}")
        print(f"  执行结果有效：{is_valid}")
        for msg in messages:
            print(f"    {msg}")
    
    # 5. 获取验证统计信息
    print("\n5. 获取验证统计信息")
    stats = engine.get_verification_statistics()
    print(f"  总调用次数：{stats['total_calls']}")
    print(f"  通过：{stats['passed']}")
    print(f"  失败：{stats['failed']}")
    print(f"  警告：{stats['warning']}")
    print(f"  阻止：{stats['blocked']}")
    print(f"  通过率：{stats['pass_rate']:.1%}")
    
    # 6. 导出审计日志
    print("\n6. 导出审计日志")
    log_filepath = "tool_verification_audit_log.json"
    engine.export_audit_log(log_filepath)
    
    print("\n" + "=" * 60)
    print("工具执行验证机制测试完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # 运行测试
    test_tool_verification()
