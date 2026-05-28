# -*- coding: utf-8 -*-
"""
太乙AGI modules 包

包含所有M系列模块(M56-M206)和辅助模块。

M系列模块通过 from modules.M###_XXX import ... 方式导入，例如：
    from modules.M189_PowerLawEngine import PowerLawEngine
    from modules.M190_AkashaChainDB import AkashaChainDB

辅助模块（v5.0）：
1. ftel_purpose_module - Ftel目的约束模块
2. holographic_projection_module - 全息投影压缩模块
3. lean_formalization_module - Lean形式化验证接口
4. bft_tolerance_module - BFT拜占庭容错执行层
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

__version__ = "5.0.0"
__author__ = "太乙AGI研究团队"
