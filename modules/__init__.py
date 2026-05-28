# -*- coding: utf-8 -*-
"""
太乙AGI v7.31 modules 包 — CS-TAGI Candidate

包含 291 个功能模块：
  - 164 个 M系列引擎 (M56-M206)
  - 127 个辅助模块 (DIKWP, agi_, taiyi_, TYIDO, CompositeAGI 等)

导入方式：
    from modules.M189_PowerLawEngine import PowerLawEngine
    from modules.M190_AkashaChainDB import AkashaChainDB
    from modules.expert_registry import ExpertRegistry
    from modules.CompositeAGI_V2 import CompositeAGI_V2

模块分类：
  M56-M69    叙事/单数处理
  M70-M89    EML相位/HoTT推理/自指检测
  M90-M109   语义流形/构造性AGI/类型检查
  M110-M133  KV治理/本体锻造/自指拓扑/AGI护栏
  M134-M159  金符CA/金陵格卷积/拓扑捷径
  M160-M189  太乙接口/幂律引擎/Akasha链式数据库
  M190-M206  UA万物理解/五大引擎/MVE/心理理论/可控熵

  DIKWP*     五层认知架构 (Data/Info/Knowledge/Wisdom/Purpose/Governance/Reliability)
  agi_*      AGI核心 (core, persona, evaluator, four_modes, holographic_ui等)
  taiyi_*    太乙子系统 (oracle, entropy, memory, rag, llm_enhancer等)
  TYIDO_*    TYIDO治理 (AddressableMemory, LongRangeReasoning, SelfConsistency等)
  其他        CompositeAGI_V2, FtelOperator, KnowledgeGraph, CacheManager等
"""

from .ftel_purpose_module import FtelPurposeModule, FtelConfig, create_ftel_module
from .holographic_projection_module import (
    HolographicProjectionModule, 
    HolographicConfig, 
    InvariantType,
    create_holographic_module
)
from .lean_formalization_module import (
    LeanFormalizationModule,
    LeanTheorem,
    FormalizationResult,
    ProofStatus,
    create_lean_module
)
from .bft_tolerance_module import (
    BFTToleranceModule,
    ConsensusMessage,
    ConsensusResult,
    NodeState,
    create_bft_module
)

__all__ = [
    # Ftel模块
    'FtelPurposeModule',
    'FtelConfig', 
    'create_ftel_module',
    
    # 全息投影模块
    'HolographicProjectionModule',
    'HolographicConfig',
    'InvariantType',
    'create_holographic_module',
    
    # Lean形式化模块
    'LeanFormalizationModule',
    'LeanTheorem',
    'FormalizationResult',
    'ProofStatus',
    'create_lean_module',
    
    # BFT容错模块
    'BFTToleranceModule',
    'ConsensusMessage',
    'ConsensusResult',
    'NodeState',
    'create_bft_module',
]

__version__ = "7.31.0"
__author__ = "太乙AGI研究团队"
