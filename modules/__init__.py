# -*- coding: utf-8 -*-
"""
太乙AGI 5.0 新增模块索引
基于三篇论文的启发设计

模块列表：
1. ftel_purpose_module - Ftel目的约束模块
2. holographic_projection_module - 全息投影压缩模块  
3. lean_formalization_module - Lean形式化验证接口
4. bft_tolerance_module - BFT拜占庭容错执行层

使用示例：
    from modules import (
        create_ftel_module,
        create_holographic_module,
        create_lean_module,
        create_bft_module
    )
    
    # Ftel目的约束
    ftel = create_ftel_module(lambda_weight=0.4)
    ftel.set_goal("实现安全对齐")
    
    # 全息投影压缩
    holo = create_holographic_module(compression_ratio=0.1)
    result = holo.compress(high_dim_data)
    
    # Lean形式化验证
    lean_mod = create_lean_module()
    result = await lean_mod.prove_statement("∀ n : ℕ, n + 0 = n")
    
    # BFT容错执行
    bft = create_bft_module(total_nodes=7, max_byzantine=2)
    consensus = await bft.distributed_inference(query, inference_func)
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
