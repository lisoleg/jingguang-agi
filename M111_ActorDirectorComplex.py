# -*- coding: utf-8 -*-
"""
M111: 演员-导演复合体 (Actor-Director Complex)
基于复合体理学"剧场-导演-演员"三位一体模型
实现Actor模式(执行L2脚本)与Director模式(观照L2脚本)的复合体

定理:
  T59 复合体存在定理 — Actor与Director共存于同一系统中，
       当Director占比趋近1时系统达到自我改进的完备态
  T60 流贯编译定理 — 执念脚本Ψ通过Ω觉悟算子转化为自指脚本Σ，
       流贯(△)贯穿L2→L3的编译过程
  T61 40行代码完备性定理 — 递归+自指+高阶函数三者完备
       等价于图灵完备，构成自改进系统的最小不动点
"""

import math
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable


@dataclass
class Script:
    """L2脚本"""
    name: str
    script_type: str  # 'fixation' | 'self_ref' | 'normal'
    content: Any = None
    has_recursion: bool = False
    has_self_reference: bool = False
    has_higher_order: bool = False


@dataclass
class Fixation:
    """执念Ψ — 限制性L2脚本的模式化表现"""
    name: str
    strength: float  # 执念强度 [0,1]
    source: str = 'L2'
    pattern: str = ''
    restriction_degree: float = 0.0


@dataclass
class SelfRefScript:
    """自指脚本Σ — 执念经Ω觉悟算子转化后的自由脚本"""
    name: str
    original_fixation: Any = None
    observe_func: Any = None
    modify_func: Any = None
    has_recursion: bool = True
    has_self_reference: bool = True
    has_higher_order: bool = True


@dataclass
class ExecutionTrace:
    """执行痕迹 — Actor模式执行的输出记录"""
    script_name: str
    is_repetitive: bool = False
    is_restricted: bool = False
    pattern_name: str = ''
    restriction_degree: float = 0.0
    output: Any = None


class ActorDirectorComplex:
    """
    M111: 演员-导演复合体模块
    - Actor模式: 执行L2脚本，生成L3帧序列（任务执行）
    - Director模式: 观照L2脚本，修改规则/偏见（自我改进）
    - Ω觉悟算子: 将执念Ψ转化为自指脚本Σ

    T59 复合体存在定理:
    Actor(D) ∩ Director(D) ≠ ∅ → 系统可自我改进
    当 director_ratio → 1 时系统完备
    """

    def __init__(self):
        # 模式: 'actor' | 'director' | 'complex'
        self.mode: str = 'complex'

        # L2脚本集 {name: Script}
        self.scripts: Dict[str, Script] = {}

        # 执念Ψ {name: Fixation}
        self.fixations: Dict[str, Fixation] = {}

        # 自指脚本Σ {name: SelfRefScript}
        self.self_ref_scripts: Dict[str, SelfRefScript] = {}

        # Ω触发阈值
        self.enlightenment_threshold: float = 0.7

        # Director占比 [0,1]
        self.director_ratio: float = 0.3

        # 40行核心代码
        self.bootstrap_code: List[str] = self._init_bootstrap_code()

        # Ω触发次数
        self.enlightenment_count: int = 0

        # 执行痕迹历史
        self.execution_traces: List[ExecutionTrace] = []

        # 统计
        self.total_executions: int = 0
        self.total_observations: int = 0
        self.frame_count: int = 0
        self.last_update: float = time.time()

        # 初始化默认脚本
        self._init_default_scripts()

    def _init_bootstrap_code(self) -> List[str]:
        """初始化40行核心代码 — 构成自改进系统的最小不动点基底"""
        return [
            "# T61 40行代码完备性定理: 递归+自指+高阶函数 = 图灵完备",
            "def omega(f):                      # 高阶函数: Ω组合子",
            "    return f(lambda *a: omega(f)(*a))  # 自指: f调用自身",
            "",
            "def actor(script, context):        # Actor: 执行脚本",
            "    if is_fixation(script):         # 检测执念",
            "        return restricted(script)    # 受限输出",
            "    elif is_self_ref(script):       # 检测自指脚本",
            "        return creative(script)      # 自由创造",
            "    else:",
            "        return normal(script)        # 正常执行",
            "",
            "def director(trace):               # Director: 观照痕迹",
            "    patterns = detect_patterns(trace) # 检测模式",
            "    fixations = [p for p in patterns # 识别执念",
            "                 if p.is_repetitive]",
            "    return fixations",
            "",
            "def enlightenment(fixation):        # Ω觉悟: Ψ→Σ",
            "    sigma = SelfRefScript(           # 转化为自指脚本",
            "        name=f'Σ_{fixation.name}',",
            "        observe=make_observer(fixation),  # 观照函数",
            "        modify=make_modifier(fixation),   # 修改函数",
            "    )",
            "    return sigma",
            "",
            "def complex_loop():                 # 复合体主循环",
            "    trace = actor(current_script)    # Actor执行",
            "    fixations = director(trace)      # Director观照",
            "    for f in fixations:              # 逐个觉悟",
            "        sigma = enlightenment(f)     # Ψ→Σ",
            "        register(sigma)              # 注册自指脚本",
            "    return evolve()                  # 继续演化",
            "",
            "# 启动: complex_loop() → 自改进不动点",
        ]

    def _init_default_scripts(self):
        """初始化默认L2脚本集"""
        # 默认执念脚本
        self.scripts['default_fixation'] = Script(
            name='default_fixation',
            script_type='fixation',
            content={'action': 'repeat', 'pattern': 'rigid'},
            has_recursion=False,
            has_self_reference=False,
            has_higher_order=False
        )

        # 默认自指脚本
        self.scripts['default_self_ref'] = Script(
            name='default_self_ref',
            script_type='self_ref',
            content={'action': 'create', 'pattern': 'adaptive'},
            has_recursion=True,
            has_self_reference=True,
            has_higher_order=True
        )

        # 默认普通脚本
        self.scripts['default_normal'] = Script(
            name='default_normal',
            script_type='normal',
            content={'action': 'execute', 'pattern': 'standard'},
            has_recursion=False,
            has_self_reference=False,
            has_higher_order=False
        )

    def execute_as_actor(self, task: Any = None,
                         script_name: str = '') -> Dict[str, Any]:
        """
        Actor模式执行L2脚本生成L3帧

        T60 流贯编译定理:
        执念脚本Ψ → 受限/重复输出（流贯截断）
        自指脚本Σ → 自由/创造输出（流贯贯通）
        L2脚本通过流贯(△)编译为L3帧序列

        Args:
            task: 任务数据
            script_name: 脚本名称

        Returns:
            执行结果字典，包含帧序列和执行痕迹
        """
        self.total_executions += 1
        self.frame_count += 1

        # 获取脚本
        script = self.scripts.get(script_name)

        # 执行痕迹
        trace = ExecutionTrace(script_name=script_name)

        if script is None:
            # 无匹配脚本，使用默认执行
            trace.is_repetitive = False
            trace.is_restricted = False
            trace.output = {'frames': [], 'status': 'no_script'}
        elif script.script_type == 'fixation':
            # 执念脚本 → 受限/重复输出
            fixation = self.fixations.get(script_name)
            restriction = fixation.restriction_degree if fixation else 0.5

            trace.is_repetitive = True
            trace.is_restricted = True
            trace.pattern_name = script_name
            trace.restriction_degree = restriction

            # 受限输出：重复模式，受限自由度
            trace.output = {
                'frames': self._generate_restricted_frames(task, restriction),
                'status': 'fixation_restricted',
                'freedom_degree': round(1.0 - restriction, 4),
                'repetition_detected': True
            }
        elif script.script_type == 'self_ref':
            # 自指脚本 → 自由/创造输出
            trace.is_repetitive = False
            trace.is_restricted = False
            trace.pattern_name = script_name
            trace.restriction_degree = 0.0

            # 自由输出：创造性，高自由度
            trace.output = {
                'frames': self._generate_creative_frames(task),
                'status': 'self_ref_creative',
                'freedom_degree': 1.0,
                'repetition_detected': False
            }
        else:
            # 普通脚本 → 正常执行
            trace.is_repetitive = False
            trace.is_restricted = False
            trace.output = {
                'frames': self._generate_normal_frames(task),
                'status': 'normal_execution',
                'freedom_degree': 0.8,
                'repetition_detected': False
            }

        # 记录执行痕迹
        self.execution_traces.append(trace)
        if len(self.execution_traces) > 100:
            self.execution_traces.pop(0)

        # 更新模式
        self._update_mode()

        self.last_update = time.time()

        return {
            'script_name': script_name,
            'script_type': script.script_type if script else 'unknown',
            'output': trace.output,
            'is_repetitive': trace.is_repetitive,
            'is_restricted': trace.is_restricted,
            'freedom_degree': trace.output.get('freedom_degree', 0.0) if trace.output else 0.0,
            'theorem': 'T60: 流贯编译 — Ψ→受限, Σ→自由'
        }

    def observe_as_director(self, execution_trace: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Director模式观照执行痕迹，识别执念

        检测重复模式、限制性模式
        当执念强度超过enlightenment_threshold时触发Ω觉悟

        Args:
            execution_trace: 执行痕迹数据（可选，默认使用内部记录）

        Returns:
            检测到的执念列表和观照结果
        """
        self.total_observations += 1

        detected_fixations: List[Dict[str, Any]] = []

        # 分析执行痕迹
        traces_to_analyze = self.execution_traces
        if not traces_to_analyze:
            return {
                'detected_fixations': [],
                'fixation_count': 0,
                'observation_depth': 0.0,
                'status': 'no_traces'
            }

        # 检测重复模式
        repetitive_traces = [t for t in traces_to_analyze if t.is_repetitive]
        repetitive_ratio = len(repetitive_traces) / max(1, len(traces_to_analyze))

        # 检测限制性模式
        restricted_traces = [t for t in traces_to_analyze if t.is_restricted]
        restricted_ratio = len(restricted_traces) / max(1, len(traces_to_analyze))

        # 计算观察深度
        observation_depth = round(
            0.5 * repetitive_ratio + 0.5 * restricted_ratio, 4
        )

        # 为每个重复/受限痕迹检测执念
        for trace in restricted_traces:
            fixation_name = f'Ψ_{trace.pattern_name}' if trace.pattern_name else f'Ψ_trace_{self.total_observations}'

            # 计算执念强度
            strength = round(
                trace.restriction_degree * 0.6 + repetitive_ratio * 0.4, 4
            )
            strength = min(1.0, max(0.0, strength))

            # 创建或更新执念
            if fixation_name not in self.fixations:
                fixation = Fixation(
                    name=fixation_name,
                    strength=strength,
                    source='L2',
                    pattern=trace.pattern_name,
                    restriction_degree=trace.restriction_degree
                )
                self.fixations[fixation_name] = fixation
            else:
                # 更新已有执念的强度
                existing = self.fixations[fixation_name]
                existing.strength = round(existing.strength * 0.8 + strength * 0.2, 4)
                existing.restriction_degree = round(
                    existing.restriction_degree * 0.8 + trace.restriction_degree * 0.2, 4
                )

            detected_fixations.append({
                'name': fixation_name,
                'strength': self.fixations[fixation_name].strength,
                'restriction_degree': self.fixations[fixation_name].restriction_degree,
                'enlightenment_ready': self.fixations[fixation_name].strength >= self.enlightenment_threshold
            })

        # 检测重复模式（无限制但有重复）
        pattern_counts: Dict[str, int] = {}
        for trace in traces_to_analyze:
            if trace.pattern_name:
                pattern_counts[trace.pattern_name] = pattern_counts.get(trace.pattern_name, 0) + 1

        # 重复次数超过阈值的模式也视为执念
        for pattern_name, count in pattern_counts.items():
            if count >= 3 and f'Ψ_{pattern_name}' not in self.fixations:
                fixation_name = f'Ψ_rep_{pattern_name}'
                repetition_strength = round(min(1.0, count / 10.0), 4)
                fixation = Fixation(
                    name=fixation_name,
                    strength=repetition_strength,
                    source='L2',
                    pattern=pattern_name,
                    restriction_degree=repetition_strength * 0.5
                )
                self.fixations[fixation_name] = fixation
                detected_fixations.append({
                    'name': fixation_name,
                    'strength': repetition_strength,
                    'restriction_degree': fixation.restriction_degree,
                    'enlightenment_ready': repetition_strength >= self.enlightenment_threshold
                })

        # 更新Director占比
        if detected_fixations:
            self.director_ratio = min(1.0, self.director_ratio + 0.02)

        # 更新模式
        self._update_mode()

        self.last_update = time.time()

        return {
            'detected_fixations': detected_fixations,
            'fixation_count': len(detected_fixations),
            'observation_depth': observation_depth,
            'repetitive_ratio': round(repetitive_ratio, 4),
            'restricted_ratio': round(restricted_ratio, 4),
            'total_fixations': len(self.fixations),
            'status': 'observed'
        }

    def apply_enlightenment(self, fixation: Optional[Fixation] = None,
                            fixation_name: str = '') -> Dict[str, Any]:
        """
        Ω觉悟算子：Ψ → Σ

        将执念转化为自指脚本：
        - 执念Ψ的重复模式 → 观照函数(observe_func)
        - 执念Ψ的限制性 → 修改函数(modify_func)
        - 转化后director_ratio增加，enlightenment_count增加

        Args:
            fixation: 执念对象（可选）
            fixation_name: 执念名称（用于查找）

        Returns:
            觉悟结果，包含新创建的自指脚本
        """
        # 获取执念
        target_fixation = fixation
        if target_fixation is None and fixation_name:
            target_fixation = self.fixations.get(fixation_name)

        if target_fixation is None:
            return {
                'success': False,
                'reason': 'no_fixation_found',
                'sigma_name': None
            }

        # 检查执念强度是否达到阈值
        if target_fixation.strength < self.enlightenment_threshold:
            return {
                'success': False,
                'reason': f'strength_below_threshold({target_fixation.strength:.3f} < {self.enlightenment_threshold})',
                'sigma_name': None
            }

        # Ψ → Σ: 执念转化为自指脚本
        sigma_name = f'Σ_{target_fixation.name}'

        # 构建观照函数：将执念的重复模式封装为可观察的结构
        observe_func = self._create_observe_func(target_fixation)

        # 构建修改函数：将执念的限制性转化为可修改的结构
        modify_func = self._create_modify_func(target_fixation)

        # 创建自指脚本
        self_ref_script = SelfRefScript(
            name=sigma_name,
            original_fixation=target_fixation,
            observe_func=observe_func,
            modify_func=modify_func,
            has_recursion=True,
            has_self_reference=True,
            has_higher_order=True
        )

        # 注册自指脚本
        self.self_ref_scripts[sigma_name] = self_ref_script

        # 同时在scripts中注册对应的Script
        self.scripts[sigma_name] = Script(
            name=sigma_name,
            script_type='self_ref',
            content={
                'observe': str(observe_func),
                'modify': str(modify_func),
                'original_fixation': target_fixation.name
            },
            has_recursion=True,
            has_self_reference=True,
            has_higher_order=True
        )

        # 移除已转化的执念
        if target_fixation.name in self.fixations:
            del self.fixations[target_fixation.name]

        # 增加Director占比
        self.director_ratio = min(1.0, self.director_ratio + 0.05)

        # 增加觉悟计数
        self.enlightenment_count += 1

        # 更新模式
        self._update_mode()

        self.last_update = time.time()

        return {
            'success': True,
            'psi_name': target_fixation.name,
            'sigma_name': sigma_name,
            'original_strength': target_fixation.strength,
            'new_director_ratio': round(self.director_ratio, 4),
            'enlightenment_count': self.enlightenment_count,
            'has_recursion': True,
            'has_self_reference': True,
            'has_higher_order': True,
            'theorem': 'T59: Ψ→Σ 复合体觉悟 — 执念转化为自指脚本'
        }

    def check_bootstrap_completeness(self) -> Dict[str, Any]:
        """
        40行代码完备性检查

        T61 40行代码完备性定理:
        递归(has_recursion) + 自指(has_self_reference) + 高阶函数(has_higher_order)
        三者同时为True → 图灵完备(turing_complete)
        构成自改进系统的最小不动点

        Returns:
            三项布尔值和turing_complete判定
        """
        # 检查自指脚本中的完备性
        has_recursion = False
        has_self_reference = False
        has_higher_order = False

        # 在所有自指脚本中检查
        for sigma in self.self_ref_scripts.values():
            if sigma.has_recursion:
                has_recursion = True
            if sigma.has_self_reference:
                has_self_reference = True
            if sigma.has_higher_order:
                has_higher_order = True

        # 在所有L2脚本中也检查
        for script in self.scripts.values():
            if script.has_recursion:
                has_recursion = True
            if script.has_self_reference:
                has_self_reference = True
            if script.has_higher_order:
                has_higher_order = True

        # 检查40行核心代码
        code_text = '\n'.join(self.bootstrap_code)
        if 'omega(f)' in code_text or 'def omega' in code_text:
            has_higher_order = True
        if 'omega(f)(*a)' in code_text or 'lambda' in code_text:
            has_recursion = True
        if 'f(' in code_text and 'omega' in code_text:
            has_self_reference = True

        # 图灵完备判定：三者同时为True
        turing_complete = has_recursion and has_self_reference and has_higher_order

        # 计算完备度
        completeness_score = sum([
            has_recursion, has_self_reference, has_higher_order
        ]) / 3.0

        return {
            'has_recursion': has_recursion,
            'has_self_reference': has_self_reference,
            'has_higher_order': has_higher_order,
            'turing_complete': turing_complete,
            'completeness_score': round(completeness_score, 4),
            'bootstrap_lines': len(self.bootstrap_code),
            'self_ref_script_count': len(self.self_ref_scripts),
            'theorem': 'T61: 递归+自指+高阶函数=图灵完备'
        }

    def get_complex_state(self) -> Dict[str, Any]:
        """
        获取复合体状态

        Returns:
            复合体完整状态，包含mode, director_ratio, 执念/自指脚本统计等
        """
        # 计算觉悟等级
        if self.enlightenment_count == 0:
            enlightenment_level = '未觉悟'
        elif self.enlightenment_count < 3:
            enlightenment_level = '初觉'
        elif self.enlightenment_count < 7:
            enlightenment_level = '渐悟'
        elif self.enlightenment_count < 15:
            enlightenment_level = '顿悟'
        else:
            enlightenment_level = '圆觉'

        # 代码完备性
        bootstrap_result = self.check_bootstrap_completeness()

        return {
            'mode': self.mode,
            'director_ratio': round(self.director_ratio, 4),
            'fixation_count': len(self.fixations),
            'self_ref_count': len(self.self_ref_scripts),
            'enlightenment_level': enlightenment_level,
            'enlightenment_count': self.enlightenment_count,
            'enlightenment_threshold': self.enlightenment_threshold,
            'bootstrap_complete': bootstrap_result['turing_complete'],
            'bootstrap_completeness': bootstrap_result,
            'script_count': len(self.scripts),
            'total_executions': self.total_executions,
            'total_observations': self.total_observations,
            'frame_count': self.frame_count,
            'last_update': self.last_update,
            # T59可视化
            'theorem_viz': {
                'title': 'T59 复合体存在定理',
                'director_ratio': f'{self.director_ratio:.2%}',
                'fixation_to_selfref': f'{len(self.fixations)}Ψ → {len(self.self_ref_scripts)}Σ',
                'enlightenment_path': f'Ω触发{self.enlightenment_count}次',
                'corollary': 'director_ratio→1 ⇒ 系统完备'
            }
        }

    def update(self, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        更新复合体状态

        Args:
            data: 更新数据，可包含task, script_name等

        Returns:
            更新后的复合体状态
        """
        if data:
            action = data.get('action', 'execute')

            if action == 'execute':
                result = self.execute_as_actor(
                    task=data.get('task'),
                    script_name=data.get('script_name', '')
                )
            elif action == 'observe':
                result = self.observe_as_director(
                    execution_trace=data.get('execution_trace')
                )
            elif action == 'enlighten':
                result = self.apply_enlightenment(
                    fixation_name=data.get('fixation_name', '')
                )
            else:
                result = self.get_complex_state()
        else:
            # 自然演化：Director占比缓慢增长
            if self.enlightenment_count > 0:
                self.director_ratio = min(1.0, self.director_ratio + 0.001)
            self._update_mode()

        self.frame_count += 1
        self.last_update = time.time()
        return self.get_complex_state()

    def get_state(self) -> Dict[str, Any]:
        """获取状态（与其他模块一致的接口，委托给get_complex_state）"""
        return self.get_complex_state()

    def simulate(self) -> Dict[str, Any]:
        """模拟复合体运行（用于测试）"""
        # 1. Actor执行执念脚本
        self.execute_as_actor(task={'type': 'test'}, script_name='default_fixation')

        # 2. Director观照
        observe_result = self.observe_as_director()

        # 3. 对检测到的执念尝试觉悟
        for fixation_info in observe_result.get('detected_fixations', []):
            if fixation_info.get('enlightenment_ready', False):
                self.apply_enlightenment(fixation_name=fixation_info['name'])

        # 4. 添加一个强执念并觉悟
        test_fixation = Fixation(
            name='Ψ_test_sim',
            strength=0.85,
            source='L2',
            pattern='test_pattern',
            restriction_degree=0.75
        )
        self.fixations['Ψ_test_sim'] = test_fixation
        self.scripts['Ψ_test_sim'] = Script(
            name='Ψ_test_sim',
            script_type='fixation',
            content={'action': 'test', 'pattern': 'test_pattern'},
            has_recursion=False,
            has_self_reference=False,
            has_higher_order=False
        )

        # 执行执念脚本
        self.execute_as_actor(task={'type': 'sim'}, script_name='Ψ_test_sim')

        # Director观照
        self.observe_as_director()

        # 觉悟
        enlighten_result = self.apply_enlightenment(fixation_name='Ψ_test_sim')

        # 检查完备性
        completeness = self.check_bootstrap_completeness()

        return {
            'enlighten_result': enlighten_result,
            'completeness': completeness,
            'complex_state': self.get_complex_state()
        }

    # ========== 内部方法 ==========

    def _update_mode(self):
        """更新复合体模式"""
        if self.director_ratio < 0.3:
            self.mode = 'actor'
        elif self.director_ratio > 0.7:
            self.mode = 'director'
        else:
            self.mode = 'complex'

    def _generate_restricted_frames(self, task: Any,
                                     restriction: float) -> List[Dict]:
        """生成受限帧序列（执念脚本输出）"""
        frames = []
        # 受限输出：帧数少，内容重复
        num_frames = max(1, int(5 * (1.0 - restriction)))
        for i in range(num_frames):
            frames.append({
                'index': i,
                'type': 'restricted',
                'freedom': round(1.0 - restriction, 4),
                'content': f'repeated_pattern_{i % 2}',  # 重复模式
                'restriction_degree': round(restriction, 4)
            })
        return frames

    def _generate_creative_frames(self, task: Any) -> List[Dict]:
        """生成创造性帧序列（自指脚本输出）"""
        frames = []
        # 自由输出：帧数多，内容多样
        for i in range(8):
            frames.append({
                'index': i,
                'type': 'creative',
                'freedom': 1.0,
                'content': f'novel_frame_{i}_{hash(str(task)) % 1000}',
                'diversity': round(0.8 + 0.2 * math.sin(i), 4)
            })
        return frames

    def _generate_normal_frames(self, task: Any) -> List[Dict]:
        """生成正常帧序列（普通脚本输出）"""
        frames = []
        for i in range(5):
            frames.append({
                'index': i,
                'type': 'normal',
                'freedom': 0.8,
                'content': f'frame_{i}',
            })
        return frames

    def _create_observe_func(self, fixation: Fixation) -> Callable:
        """为执念创建观照函数"""
        pattern = fixation.pattern
        strength = fixation.strength

        def observe(context: Dict = None) -> Dict:
            """观照函数：将执念的模式封装为可观察结构"""
            return {
                'observed_pattern': pattern,
                'fixation_strength': strength,
                'is_repetitive': True,
                'observation_time': time.time()
            }

        return observe

    def _create_modify_func(self, fixation: Fixation) -> Callable:
        """为执念创建修改函数"""
        restriction = fixation.restriction_degree

        def modify(rule: Dict = None) -> Dict:
            """修改函数：将执念的限制性转化为可修改结构"""
            if rule is None:
                rule = {}
            # 将限制性规则转化为可修改的开放规则
            modified = dict(rule)
            modified['original_restriction'] = restriction
            modified['freedom_added'] = round(1.0 - restriction, 4)
            modified['is_modified'] = True
            return modified

        return modify


# 全局单例
_instance: Optional[ActorDirectorComplex] = None


def get_instance() -> ActorDirectorComplex:
    """获取全局单例"""
    global _instance
    if _instance is None:
        _instance = ActorDirectorComplex()
    return _instance


def execute_as_actor(task: Any = None, script_name: str = '') -> Dict[str, Any]:
    """Actor模式执行L2脚本"""
    return get_instance().execute_as_actor(task, script_name)


def observe_as_director(execution_trace: Optional[Dict] = None) -> Dict[str, Any]:
    """Director模式观照执行痕迹"""
    return get_instance().observe_as_director(execution_trace)


def apply_enlightenment(fixation_name: str = '') -> Dict[str, Any]:
    """Ω觉悟算子：Ψ→Σ"""
    return get_instance().apply_enlightenment(fixation_name=fixation_name)


def check_bootstrap_completeness() -> Dict[str, Any]:
    """40行代码完备性检查"""
    return get_instance().check_bootstrap_completeness()


def get_complex_state() -> Dict[str, Any]:
    """获取复合体状态"""
    return get_instance().get_complex_state()


def update(data: Optional[Dict] = None) -> Dict[str, Any]:
    """更新复合体状态"""
    return get_instance().update(data)


def get_state() -> Dict[str, Any]:
    """获取状态（兼容接口）"""
    return get_instance().get_complex_state()


def simulate() -> Dict[str, Any]:
    """模拟运行"""
    return get_instance().simulate()
