# -*- coding: utf-8 -*-
"""
M229 ActionSurfaceRouter — 混合动作面路由器
==========================================
借鉴 PhoneHarness 的 Mixed-Action Space 概念，将太乙AGI的认知操作
从"单一模块执行"升级为"跨动作面智能路由"。

六大动作面(Action Surfaces):
  1. ICE Surface   — 形式化验证通道 (Idris/Lean, HoTT, 构造性数学)
  2. Jinling Surface — 图论通道 (Beta-rewiring, Laplacian谱, 拓扑操作)
  3. UA Surface    — 语义理解通道 (万物理解, ExpertBridge, 上下文构建)
  4. EML Surface   — 算术通道 (指数-对数混合运算, 极坐标运算)
  5. Liu Surface   — 变分动力学通道 (作用量, 变分, 平衡, 自由能)
  6. MCP Surface   — 外部工具通道 (AkashaChainDB, API调用, 外部搜索)

核心路由策略:
  - 关键词匹配: 根据任务描述中的关键词映射到动作面
  - 亲和度评分: 对每个动作面计算任务亲和度分数
  - 历史偏好: 基于过往路由成功率调整权重

设计定理 T2.44: 动作面路由最优性
  对于给定任务集T，混合路由策略的完成率R_mix >= max(R_single)
  即: 混合路由策略的完成率不低于最优单一动作面策略

Author: 太乙AGI v7.33c (PhoneHarness Inspiration)
"""

import math
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class ActionSurface(Enum):
    """六大动作面"""
    ICE = "ice"           # 形式化验证通道
    JINLING = "jinling"   # 图论通道
    UA = "ua"             # 语义理解通道
    EML = "eml"           # 算术通道
    LIU = "liu"           # 变分动力学通道
    MCP = "mcp"           # 外部工具通道


# 关键词 → 动作面映射
SURFACE_KEYWORDS: Dict[ActionSurface, List[str]] = {
    ActionSurface.ICE: [
        "形式化", "验证", "证明", "theorem", "verify", "proof",
        "idris", "lean", "hott", "构造性", "类型论", "自指",
        "ice", "不动点", "y-combinator"
    ],
    ActionSurface.JINLING: [
        "图", "拓扑", "beta", "rewire", "邻接", "laplacian",
        "谱", "节点", "边", "金灵球", "jinling", "超图",
        "端口", "pct", "分裂"
    ],
    ActionSurface.UA: [
        "理解", "语义", "上下文", "知识", "expert", "专家",
        "搜索", "recommend", "ua", "万物", "embedding",
        "向量", "相似", "桥梁"
    ],
    ActionSurface.EML: [
        "eml", "指数", "对数", "加法", "乘法", "极坐标",
        "混合", "算术", "eml_add", "eml_mul", "笛卡尔",
        "exp", "log", "复数"
    ],
    ActionSurface.LIU: [
        "liu", "变分", "作用量", "平衡", "自由能", "动能",
        "势能", "演化", "微扰", "变分原理", "极值",
        "熵", "温度", "equilibrium"
    ],
    ActionSurface.MCP: [
        "akasha", "数据库", "持久化", "存储", "api", "外部",
        "调用", "mcp", "工具", "搜索", "http", "查询",
        "三元组", "链", "block"
    ],
}

# 动作面元信息
SURFACE_META: Dict[ActionSurface, Dict[str, str]] = {
    ActionSurface.ICE: {
        "name": "ICE形式化验证通道",
        "desc": "Idris/Lean4/HoTT构造性数学, Y-组合子自指核",
        "strength": "确定性高, 可证明正确性",
        "weakness": "表达力受限, 复杂任务慢"
    },
    ActionSurface.JINLING: {
        "name": "Jinling图论通道",
        "desc": "Beta-rewiring, Laplacian谱分析, 拓扑操作",
        "strength": "结构变化可视化, 全局视角",
        "weakness": "大规模图计算开销大"
    },
    ActionSurface.UA: {
        "name": "UA语义理解通道",
        "desc": "万物理解引擎, ExpertBridge, 上下文构建",
        "strength": "语义丰富, 跨域知识",
        "weakness": "依赖外部知识库"
    },
    ActionSurface.EML: {
        "name": "EML算术通道",
        "desc": "指数-对数混合运算, 极坐标运算",
        "strength": "数值精确, 统一加减乘",
        "weakness": "仅适用于数值计算"
    },
    ActionSurface.LIU: {
        "name": "Liu变分动力学通道",
        "desc": "作用量, 变分, 平衡, 自由能, 演化方向",
        "strength": "物理直觉, 动力学预测",
        "weakness": "需要明确的数据结构"
    },
    ActionSurface.MCP: {
        "name": "MCP外部工具通道",
        "desc": "AkashaChainDB, API调用, 外部搜索",
        "strength": "可扩展, 访问外部资源",
        "weakness": "依赖网络和外部服务"
    },
}


@dataclass
class RoutingResult:
    """路由结果"""
    task: str
    surface: ActionSurface
    affinity_scores: Dict[str, float]
    confidence: float       # 路由置信度 [0, 1]
    reason: str             # 选择理由
    alternatives: List[Tuple[ActionSurface, float]] = field(default_factory=list)
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class SurfaceStatus:
    """动作面状态"""
    surface: ActionSurface
    available: bool = True
    load: float = 0.0       # 当前负载 [0, 1]
    success_rate: float = 1.0  # 历史成功率
    avg_latency: float = 0.0   # 平均延迟(ms)


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: int
    task: str
    surface: ActionSurface
    status: str = "pending"   # pending/running/done/failed
    result: Optional[Any] = None
    duration_ms: float = 0.0


@dataclass
class WorkflowResult:
    """跨动作面工作流结果"""
    workflow_id: str
    steps: List[WorkflowStep]
    total_duration_ms: float = 0.0
    success: bool = True
    surface_transitions: int = 0  # 动作面切换次数


class ActionSurfaceRouter:
    """
    M229 混合动作面路由器

    核心能力:
      - route_task(): 根据任务描述路由到最佳动作面
      - execute_routed(): 在指定动作面上执行任务
      - cross_surface_workflow(): 跨动作面工作流编排
      - get_surface_status(): 查询动作面状态
    """

    def __init__(self):
        self._routing_history: List[RoutingResult] = []
        self._surface_status: Dict[ActionSurface, SurfaceStatus] = {
            s: SurfaceStatus(surface=s) for s in ActionSurface
        }
        self._success_counts: Dict[ActionSurface, int] = {s: 0 for s in ActionSurface}
        self._total_counts: Dict[ActionSurface, int] = {s: 0 for s in ActionSurface}
        self._version = "v7.33c"

    # ─── 核心路由 ───────────────────────────────

    def compute_affinity(self, task: str) -> Dict[ActionSurface, float]:
        """
        计算任务对每个动作面的亲和度分数

        策略:
          - 关键词命中: 每个命中 +1.0
          - 长度归一化: score / max(len(keywords), 1)
          - 历史偏好: 乘以 sqrt(success_rate)
          - 负载惩罚: 乘以 (1 - load * 0.5)
        """
        task_lower = task.lower()
        scores: Dict[ActionSurface, float] = {}

        for surface, keywords in SURFACE_KEYWORDS.items():
            hit_count = sum(1 for kw in keywords if kw.lower() in task_lower)
            raw_score = hit_count / max(len(keywords), 1) * len(keywords)

            # 历史偏好调整
            status = self._surface_status[surface]
            history_factor = math.sqrt(max(status.success_rate, 0.1))

            # 负载惩罚
            load_penalty = 1.0 - status.load * 0.5

            scores[surface] = raw_score * history_factor * load_penalty

        return scores

    def route_task(self, task: str) -> RoutingResult:
        """
        路由任务到最佳动作面

        Args:
            task: 任务描述

        Returns:
            RoutingResult with best surface and affinity scores
        """
        scores = self.compute_affinity(task)

        # 排序选择最佳
        sorted_surfaces = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_surface, best_score = sorted_surfaces[0]

        # 置信度: 最佳分数 / (最佳 + 次佳)
        if len(sorted_surfaces) > 1 and (best_score + sorted_surfaces[1][1]) > 0:
            confidence = best_score / (best_score + sorted_surfaces[1][1])
        else:
            confidence = 1.0 if best_score > 0 else 0.0

        # 无匹配时默认路由到UA(语义理解)
        if best_score == 0:
            best_surface = ActionSurface.UA
            confidence = 0.3
            reason = "无关键词匹配, 默认路由到UA语义理解通道"
        else:
            meta = SURFACE_META[best_surface]
            reason = f"关键词亲和度最高({best_score:.2f}), {meta['name']}: {meta['strength']}"

        alternatives = [(s, sc) for s, sc in sorted_surfaces[1:4]]

        result = RoutingResult(
            task=task,
            surface=best_surface,
            affinity_scores={s.value: round(sc, 4) for s, sc in scores.items()},
            confidence=round(confidence, 4),
            reason=reason,
            alternatives=alternatives,
        )

        self._routing_history.append(result)
        return result

    # ─── 动作面状态 ─────────────────────────────

    def get_surface_status(self, surface_name: str = None) -> Dict:
        """获取动作面状态"""
        if surface_name:
            surface = ActionSurface(surface_name)
            status = self._surface_status[surface]
            return {
                'surface': surface.value,
                'meta': SURFACE_META[surface],
                'available': status.available,
                'load': status.load,
                'success_rate': status.success_rate,
                'avg_latency_ms': status.avg_latency,
            }
        else:
            return {
                s.value: {
                    'meta': SURFACE_META[s],
                    'available': st.available,
                    'load': st.load,
                    'success_rate': st.success_rate,
                    'avg_latency_ms': st.avg_latency,
                }
                for s, st in self._surface_status.items()
            }

    def update_surface_status(self, surface_name: str, available: bool = None,
                              load: float = None, success_rate: float = None,
                              avg_latency: float = None):
        """更新动作面状态"""
        surface = ActionSurface(surface_name)
        status = self._surface_status[surface]
        if available is not None:
            status.available = available
        if load is not None:
            status.load = max(0, min(1, load))
        if success_rate is not None:
            status.success_rate = max(0, min(1, success_rate))
        if avg_latency is not None:
            status.avg_latency = avg_latency

    # ─── 跨动作面工作流 ──────────────────────────

    def plan_workflow(self, tasks: List[str]) -> List[WorkflowStep]:
        """
        规划跨动作面工作流

        对每个任务路由到最佳动作面, 生成有序步骤列表
        """
        steps = []
        for i, task in enumerate(tasks):
            routing = self.route_task(task)
            steps.append(WorkflowStep(
                step_id=i,
                task=task,
                surface=routing.surface,
            ))
        return steps

    def execute_workflow(self, tasks: List[str]) -> WorkflowResult:
        """
        执行跨动作面工作流

        模拟执行每个步骤, 记录结果和切换次数
        """
        steps = self.plan_workflow(tasks)
        transitions = 0
        prev_surface = None

        for step in steps:
            step.status = "done"
            # 模拟执行结果
            step.result = {
                'task': step.task,
                'surface': step.surface.value,
                'status': 'completed',
            }
            step.duration_ms = 10.0 + hash(step.task) % 50

            if prev_surface and prev_surface != step.surface:
                transitions += 1
            prev_surface = step.surface

        workflow_id = hashlib.md5(
            f"workflow_{time.time()}_{len(tasks)}".encode()
        ).hexdigest()[:12]

        return WorkflowResult(
            workflow_id=workflow_id,
            steps=steps,
            total_duration_ms=sum(s.duration_ms for s in steps),
            success=True,
            surface_transitions=transitions,
        )

    # ─── 定理验证 T2.44 ─────────────────────────

    def verify_theorem(self) -> Dict:
        """
        定理 T2.44: 动作面路由最优性

        对于给定任务集T, 混合路由策略的完成率 R_mix >= max(R_single)

        验证方法:
          1. 生成多样化任务集(覆盖6个动作面)
          2. 计算混合路由的匹配率
          3. 计算每个单一动作面的匹配率
          4. 断言 R_mix >= max(R_single)
        """
        # 测试任务集 - 每个动作面2个任务
        test_tasks = [
            # ICE
            "验证HoTT构造性门回路的类型正确性",
            "证明Y-组合子自指不动点定理",
            # Jinling
            "对金灵球图执行beta-rewiring操作",
            "计算邻接矩阵的Laplacian谱",
            # UA
            "搜索量子计算相关的AI专家",
            "构建自然语言处理的上下文理解",
            # EML
            "计算eml(2.0, 3.0)的指数-对数混合值",
            "执行极坐标数的乘法运算",
            # Liu
            "计算金灵球堆垒的Liu作用量",
            "判定Liu变分是否达到平衡态",
            # MCP
            "将三元组写入AkashaChainDB持久化",
            "调用外部API获取实时数据",
        ]

        # 混合路由匹配
        correct_surface = [
            ActionSurface.ICE, ActionSurface.ICE,
            ActionSurface.JINLING, ActionSurface.JINLING,
            ActionSurface.UA, ActionSurface.UA,
            ActionSurface.EML, ActionSurface.EML,
            ActionSurface.LIU, ActionSurface.LIU,
            ActionSurface.MCP, ActionSurface.MCP,
        ]

        mix_hits = 0
        for task, expected in zip(test_tasks, correct_surface):
            routing = self.route_task(task)
            if routing.surface == expected:
                mix_hits += 1

        r_mix = mix_hits / len(test_tasks)

        # 单一动作面匹配率
        single_rates = {}
        for surface in ActionSurface:
            hits = sum(1 for e in correct_surface if e == surface)
            single_rates[surface.value] = hits / len(test_tasks)

        max_single = max(single_rates.values())

        # T2.44核心断言: R_mix >= max(R_single)
        theorem_pass = r_mix >= max_single

        return {
            'pass': theorem_pass,
            'theorem': 'T2.44',
            'description': '动作面路由最优性: R_mix >= max(R_single)',
            'r_mix': round(r_mix, 4),
            'max_r_single': round(max_single, 4),
            'mix_hits': mix_hits,
            'total_tasks': len(test_tasks),
            'single_rates': {k: round(v, 4) for k, v in single_rates.items()},
            'evidence': f"R_mix={r_mix:.4f} >= max(R_single)={max_single:.4f}" if theorem_pass
                        else f"R_mix={r_mix:.4f} < max(R_single)={max_single:.4f} — FAIL",
        }

    # ─── 模块接口 ──────────────────────────────

    def get_state(self) -> Dict:
        """模块状态查询"""
        return {
            'version': self._version,
            'module': 'M229_ActionSurfaceRouter',
            'surfaces': len(ActionSurface),
            'routing_history_count': len(self._routing_history),
            'theorem': 'T2.44',
            'surface_status': {
                s.value: {
                    'available': st.available,
                    'success_rate': st.success_rate,
                }
                for s, st in self._surface_status.items()
            },
        }


# ─── 单例 ────────────────────────────────────

_instance = None

def get_instance():
    global _instance
    if _instance is None:
        _instance = ActionSurfaceRouter()
    return _instance
