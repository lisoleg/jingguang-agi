# -*- coding: utf-8 -*-
"""
太乙AGI 6.0 - 主窗口集成
Composite AGI 6.0 Main Window Integration

整合所有核心模块：
- VirtualPersona: 虚拟人格体核心
- DIKWPPanel: DIKWP状态仪表盘
- SpringWormEngine: 弹簧虫动画引擎
- IntentionManifoldEngine: 意图流形曲率引擎
- HolographicProjection: 全息密度投影系统

基于复合体理学：MBTI人格 × 情绪 × 认知 × 记忆 × 全息拓扑

版本: v1.0
日期: 2026-05-13
"""

import time
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# 导入核心模块
from agi_persona_core import (
    VirtualPersona, MBTI_Dimension, EmotionState, 
    CognitiveStyle, GrowthMemory, ActionScore
)
from agi_dikwp_panel import (
    DIKWPPanel, LayerStatus, BFTState, LeanProof
)
from agi_spring_worm_engine import (
    SpringWormEngine, SpringPhysics, WormSegment,
    EasingFunction, AnimationTask
)
from agi_intention_manifold import (
    IntentionManifoldEngine, IntentType, CurvatureLevel,
    DensityMode, Intent, DisplayConfig, GeodesicPath
)
from agi_holographic_ui import (
    HolographicProjection, HolographicLayer, DensityNode,
    ProjectionMode, LayerType, DensityController
)


@dataclass
class AGIInteractionContext:
    """AGI交互上下文"""
    # 时间戳
    timestamp: float = field(default_factory=time.time)
    session_id: str = ""
    
    # 用户输入
    user_input: str = ""
    input_mode: str = "text"  # text/voice/handwriting
    
    # 意图
    intent: Optional[Intent] = None
    
    # 虚拟人格
    persona: Optional[VirtualPersona] = None
    
    # DIKWP状态
    dikwp_panel: Optional[DIKWPPanel] = None
    
    # 输出
    output_content: Any = None
    output_config: Optional[DisplayConfig] = None
    action_score: Optional[ActionScore] = None
    
    # 状态
    status: str = "idle"
    error: Optional[str] = None
    
    # 元数据
    metadata: Dict = field(default_factory=dict)


class CompositeAGI6:
    """
    太乙AGI 6.0 核心类
    
    整合所有核心模块，实现革命性的人机交互体验：
    
    1. 虚拟人格体 → 有灵魂的AI伙伴
    2. DIKWP状态 → 可解释的思维过程
    3. 意图流形 → 自适应的意图理解
    4. 全息投影 → 多维信息展示
    5. 弹簧虫动效 → 流畅的交互体验
    """
    
    def __init__(self, mbti_type: str = "INTJ"):
        """
        初始化太乙AGI 6.0
        
        Args:
            mbti_type: 虚拟人格MBTI类型
        """
        # 会话ID
        self.session_id = f"session_{int(time.time() * 1000)}"
        self.start_time = time.time()
        
        # ===== 核心模块初始化 =====
        
        # 1. 虚拟人格体
        self.persona = VirtualPersona(mbti_type)
        print(f"✓ 虚拟人格体初始化: {self.persona.name} ({mbti_type})")
        
        # 2. DIKWP状态面板
        self.dikwp_panel = DIKWPPanel()
        print("✓ DIKWP状态仪表盘初始化")
        
        # 3. 意图流形引擎
        self.intention_engine = IntentionManifoldEngine()
        print("✓ 意图流形曲率引擎初始化")
        
        # 4. 全息投影系统
        self.holographic = HolographicProjection()
        self.density_controller = DensityController(self.holographic)
        print("✓ 全息密度投影系统初始化")
        
        # 5. 弹簧虫动画引擎
        self.animation_engine = SpringWormEngine()
        print("✓ 弹簧虫动画引擎初始化")
        
        # ===== 交互状态 =====
        self.current_context: Optional[AGIInteractionContext] = None
        self.interaction_history: List[AGIInteractionContext] = []
        
        # ===== 统计信息 =====
        self.stats = {
            "total_interactions": 0,
            "avg_response_time": 0.0,
            "total_tokens": 0,
            "session_duration": 0.0,
        }
        
        # ===== 回调函数 =====
        self.on_interaction_start = None
        self.on_interaction_end = None
        self.on_dikwp_update = None
        self.on_persona_update = None
    
    # ==================== 核心交互 ====================
    
    def process_input(self, 
                     user_input: str,
                     context: Optional[Dict] = None) -> AGIInteractionContext:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入文本
            context: 额外上下文
            
        Returns:
            交互上下文
        """
        # 创建上下文
        ctx = AGIInteractionContext(
            session_id=self.session_id,
            user_input=user_input,
        )
        
        self.current_context = ctx
        ctx.status = "processing"
        
        # 触发回调
        if self.on_interaction_start:
            self.on_interaction_start(ctx)
        
        try:
            # ===== 步骤1: 意图分析 =====
            ctx.intent = self.intention_engine.analyze_intent(
                user_input,
                context=[c.user_input for c in self.interaction_history[-5:]]
            )
            
            # 更新虚拟人格情绪
            self.persona.get_emotional_response(
                self._intent_to_stimulus(ctx.intent.intent_type)
            )
            
            # ===== 步骤2: DIKWP处理 =====
            self._process_dikwp(ctx)
            
            # ===== 步骤3: 生成输出配置 =====
            ctx.output_config = self.intention_engine.generate_display_config()
            
            # 根据曲率调节密度
            self.density_controller.adjust_density(ctx.intent.curvature)
            
            # ===== 步骤4: 计算作用量评分 =====
            dikwp_data = self._build_dikwp_data(ctx)
            ctx.action_score = self.persona.compute_action_score(dikwp_data)
            
            # ===== 步骤5: 计算社交红利 =====
            output_meta = {
                "has_source": ctx.output_config.show_sources,
                "has_reasoning": ctx.output_config.show_reasoning,
                "has_examples": ctx.output_config.show_examples,
                "is_actionable": True,
            }
            social_bonus = self.persona.compute_social_bonus(output_meta)
            
            # ===== 步骤6: 适配输出 =====
            ctx.persona = self.persona
            
            # 标记完成
            ctx.status = "completed"
            
            # 添加记忆
            self.persona.add_memory(
                event_type=ctx.intent.intent_type.value,
                content=user_input[:100],
                feedback=social_bonus["information_bonus"],
                importance=ctx.intent.complexity,
                tags=ctx.intent.keywords[:3]
            )
            
            # 更新统计
            self.stats["total_interactions"] += 1
            
        except Exception as e:
            ctx.status = "error"
            ctx.error = str(e)
            self.persona.get_emotional_response("confusion")
        
        # 保存历史
        self.interaction_history.append(ctx)
        
        # 触发回调
        if self.on_interaction_end:
            self.on_interaction_end(ctx)
        
        return ctx
    
    def _process_dikwp(self, ctx: AGIInteractionContext):
        """处理DIKWP层级"""
        # 模拟DIKWP处理流程
        # 实际应用中这里会调用真正的AI模型
        
        # D层 - 数据处理
        self.dikwp_panel.update_layer("D", 0.0, LayerStatus.PROCESSING)
        time.sleep(0.05)  # 模拟处理
        self.dikwp_panel.update_layer(
            "D", 0.9, 
            LayerStatus.COMPLETE,
            {"source": "input", "confidence": 0.95}
        )
        
        # I层 - 信息处理
        self.dikwp_panel.update_layer("I", 0.0, LayerStatus.PROCESSING)
        time.sleep(0.05)
        self.dikwp_panel.update_layer(
            "I", 0.88, 
            LayerStatus.COMPLETE,
            {"entities": ctx.intent.keywords}
        )
        
        # K层 - 知识处理
        self.dikwp_panel.update_layer("K", 0.0, LayerStatus.PROCESSING)
        time.sleep(0.05)
        self.dikwp_panel.update_layer(
            "K", 0.75, 
            LayerStatus.COMPLETE,
            {"coverage": 0.75, "sources": ["knowledge_base"]}
        )
        
        # W层 - 智慧处理
        self.dikwp_panel.update_layer("W", 0.0, LayerStatus.PROCESSING)
        time.sleep(0.05)
        self.dikwp_panel.update_layer(
            "W", 0.85, 
            LayerStatus.COMPLETE,
            {"strategy": "multi_perspective"}
        )
        
        # P层 - 目的处理
        self.dikwp_panel.update_layer("P", 0.0, LayerStatus.PROCESSING)
        time.sleep(0.05)
        self.dikwp_panel.update_layer(
            "P", 0.95, 
            LayerStatus.COMPLETE,
            {"alignment": 0.95, "safety_check": "passed"}
        )
        
        # R层 - 可靠性处理
        self.dikwp_panel.update_layer("R", 0.0, LayerStatus.PROCESSING)
        
        # BFT投票模拟
        self.dikwp_panel.bft.add_vote("validator_1", True)
        self.dikwp_panel.bft.add_vote("validator_2", True)
        self.dikwp_panel.bft.add_vote("validator_3", True)
        
        time.sleep(0.05)
        self.dikwp_panel.update_layer(
            "R", 1.0, 
            LayerStatus.COMPLETE,
            {"bft_ratio": 1.0, "consensus": True}
        )
        
        ctx.dikwp_panel = self.dikwp_panel
        
        # 触发回调
        if self.on_dikwp_update:
            self.on_dikwp_update(self.dikwp_panel.get_full_status())
    
    def _build_dikwp_data(self, ctx: AGIInteractionContext) -> Dict:
        """构建DIKWP数据"""
        full_status = self.dikwp_panel.get_full_status()
        
        return {
            "data": {"confidence": full_status["layers"][0]["score"]},
            "information": {"completeness": full_status["layers"][1]["score"]},
            "knowledge": {"coverage": full_status["layers"][2]["score"]},
            "wisdom": {"score": full_status["layers"][3]["score"]},
            "purpose": {"alignment": full_status["layers"][4]["score"]},
            "reliability": {"bft_ratio": full_status["layers"][5]["score"]},
        }
    
    def _intent_to_stimulus(self, intent_type: IntentType) -> str:
        """意图类型转情绪刺激"""
        mapping = {
            IntentType.ANALYSIS: "complex_task",
            IntentType.CREATION: "creative_task",
            IntentType.QUERY: "curiosity",
            IntentType.TASK: "focused",
            IntentType.LEARNING: "curiosity",
        }
        return mapping.get(intent_type, "neutral")
    
    # ==================== 可视化数据 ====================
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """获取所有可视化数据"""
        return {
            "persona": {
                "name": self.persona.name,
                "mbti": self.persona.mbti_type,
                "cognitive_style": self.persona.cognitive_style.value,
                "emotion": {
                    "state": self.persona.emotion.state.value,
                    "intensity": self.persona.emotion.intensity,
                    "valence": self.persona.emotion.valence,
                    "arousal": self.persona.emotion.arousal,
                },
                "geometry": self.persona.get_geometry_params(),
                "social_bonus": self.persona.social_bonus,
                "cq_score": self.persona._compute_cq_score(),
            },
            "dikwp": self.dikwp_panel.get_visualization_data(),
            "intention": self.intention_engine.to_dict() if self.intention_engine.current_intent else {},
            "holographic": {
                "state": self.holographic.get_state(),
                "projection": self.holographic.project().__dict__,
            },
            "animation": self.animation_engine.get_engine_state(),
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表盘数据"""
        return {
            "persona_summary": self.persona.to_dict(),
            "dikwp_summary": self.dikwp_panel.get_full_status(),
            "intent_summary": self.intention_engine.get_intent_summary(),
            "display_config": self.intention_engine.get_display_summary(),
        }
    
    # ==================== 动画控制 ====================
    
    def trigger_emotion_animation(self):
        """触发情绪动画"""
        geo = self.persona.get_geometry_params()
        
        # 创建颜色动画
        self.animation_engine.animate_color_shift(
            "persona_color",
            self.animation_engine.get_animation_value("persona_color") or 200,
            geo["color_hue"],
            duration=0.5
        )
        
        # 创建缩放动画
        self.animation_engine.animate_scale(
            "persona_scale",
            1.0,
            geo["scale"],
            duration=0.3
        )
    
    def trigger_interaction_animation(self, 
                                     element_id: str,
                                     animation_type: str = "pulse"):
        """触发交互动画"""
        if animation_type == "pulse":
            # 脉冲动画
            scale_task = self.animation_engine.animate_scale(
                element_id, 1.0, 1.2, 0.15
            )
            # 恢复
            self.animation_engine.animate_scale(
                element_id, 1.2, 1.0, 0.15
            )
        elif animation_type == "glow":
            # 发光动画
            self.animation_engine.animate(
                0.3, 0.9, 0.3,
                EasingFunction.EASE_IN_OUT,
                f"{element_id}_glow"
            )
    
    # ==================== 会话管理 ====================
    
    def reset_session(self):
        """重置会话"""
        self.interaction_history.clear()
        self.dikwp_panel.reset()
        self.animation_engine.clear_all()
        self.current_context = None
        self.stats["total_interactions"] = 0
    
    def get_session_summary(self) -> Dict:
        """获取会话摘要"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "duration": time.time() - self.start_time,
            "total_interactions": self.stats["total_interactions"],
            "persona_evolution": self.persona.get_personality_evolution(),
            "avg_cq": self.dikwp_panel.cognitive_quotient,
            "memory_count": len(self.persona.memories),
        }
    
    # ==================== 调试和状态 ====================
    
    def print_status(self):
        """打印状态"""
        print("\n" + "="*60)
        print("太乙AGI 6.0 状态报告")
        print("="*60)
        
        # 会话信息
        print(f"\n会话ID: {self.session_id}")
        print(f"运行时长: {time.time() - self.start_time:.1f}秒")
        print(f"交互次数: {self.stats['total_interactions']}")
        
        # 虚拟人格
        print(f"\n--- 虚拟人格体 ---")
        print(f"名称: {self.persona.name}")
        print(f"MBTI: {self.persona.mbti_type}")
        print(f"认知风格: {self.persona.cognitive_style.value}")
        print(f"情绪状态: {self.persona.emotion.state.value}")
        print(f"情绪强度: {self.persona.emotion.intensity:.2f}")
        print(f"认知商数: {self.persona._compute_cq_score():.3f}")
        
        # DIKWP
        print(f"\n--- DIKWP状态 ---")
        print(self.dikwp_panel.get_ascii_status())
        
        # 当前意图
        if self.current_context and self.current_context.intent:
            print(f"\n--- 当前意图 ---")
            intent = self.current_context.intent
            print(f"类型: {intent.intent_type.value}")
            print(f"复杂度: {intent.complexity:.2f}")
            print(f"曲率: {intent.curvature:.2f}")
            print(f"曲率级别: {intent.curvature_level.value[2]}")
        
        print("\n" + "="*60)


# ==================== 示例运行 ====================

def demo_interaction(agi: CompositeAGI6, user_input: str):
    """演示交互"""
    print(f"\n>>> 用户: {user_input}")
    
    start = time.time()
    ctx = agi.process_input(user_input)
    elapsed = time.time() - start
    
    print(f"\n<<< AGI响应 (耗时 {elapsed*1000:.1f}ms)")
    
    # 显示关键信息
    if ctx.intent:
        print(f"  意图类型: {ctx.intent.intent_type.value}")
        print(f"  曲率: {ctx.intent.curvature:.2f} ({ctx.intent.curvature_level.value[2]})")
        print(f"  复杂度: {ctx.intent.complexity:.2f}")
    
    if ctx.persona:
        print(f"  人格情绪: {ctx.persona.emotion.state.value}")
        print(f"  CQ评分: {ctx.persona._compute_cq_score():.3f}")
    
    if ctx.action_score:
        print(f"  作用量: {ctx.action_score.final_action:.3f}")
    
    if ctx.output_config:
        print(f"  展示深度: {ctx.output_config.depth}")
        print(f"  密度模式: {ctx.output_config.density_mode.value}")


def main():
    """主函数"""
    import sys

    # 检查参数
    gui_mode = len(sys.argv) > 1 and sys.argv[1] == '--gui'

    if gui_mode:
        # 图形界面模式
        try:
            from agi_pygame_gui import run_gui_mode
            print("\n" + "="*60)
            print("太乙AGI 6.0 图形界面模式")
            print("基于复合体理学 · 意图流形 · 全息投影")
            print("="*60)

            agi = CompositeAGI6("INTJ")
            run_gui_mode(agi)
        except ImportError as e:
            print(f"启动图形界面失败: {e}")
            print("请确保已安装 pygame: pip install pygame")
            sys.exit(1)
        return

    # 控制台演示模式
    print("\n" + "="*60)
    print("太乙AGI 6.0 革命性人机交互系统")
    print("基于复合体理学 · 一现象三视界诠释法")
    print("="*60)

    # 创建AGI实例
    agi = CompositeAGI6("INTJ")

    # 演示交互
    test_inputs = [
        "帮我分析一下深度学习的发展历史，要深入详细的",
        "什么是Python？",
        "帮我写一个快速排序算法",
        "比较一下React和Vue的优缺点",
        "我想学习量子计算，从基础开始",
    ]
    
    for inp in test_inputs:
        demo_interaction(agi, inp)
        time.sleep(0.1)
    
    # 打印完整状态
    agi.print_status()
    
    # 显示会话摘要
    print("\n会话摘要:")
    summary = agi.get_session_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
