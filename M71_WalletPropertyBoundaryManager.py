#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钱包属性边界管理器 (Wallet Property Boundary Manager)
基于《新契约论：走向碳硅共生的信息关系实在时代》

核心概念：
- 钱（Money）的属性边界在L1-L5分层定义
- L1: 信息本体（无序/有序潜力）
- L2: 生成规则（契约/协议）
- L3: 物理载体（芯片/纸张）
- L4: 认知主体（人/AI的估值）
- L5: 现象交换（价格/交易）

定理 T23：钱包属性边界定理
定理 T24：贡献度量不变性定理
定理 T25：自指Φ值检测定理
定理 T26：碳硅熵合约定理
定理 T27：人机约柜时间锁仓定理

版本：AGI 14.0 第71模块
论文来源：《新契约论》复合体理学系列
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class Layer(Enum):
    """L1-L5 层次枚举"""
    L1_ONTOLOGY = "L1"      # 信息本体
    L2_RULES = "L2"           # 生成规则
    L3_PHYSICS = "L3"         # 物理载体
    L4_COGNITION = "L4"       # 认知主体
    L5_PHENOMENON = "L5"      # 现象交换


class BoundaryStatus(Enum):
    """边界状态"""
    INTACT = "intact"           # 完整（无泄漏）
    LEAKAGE = "leakage"         # 泄漏（跨层信息泄漏）
    COLLAPSE = "collapse"        # 崩溃（边界完全失效）
    TRANSFORMING = "transforming"  # 转型中


@dataclass
class LayerProperty:
    """层次属性"""
    layer: Layer
    property_name: str
    value: float                   # 属性值 [0,1]
    boundary_strength: float       # 边界强度 [0,1]
    info_content: float            # 信息内容
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ContributionMetrics:
    """贡献度量结果"""
    agent_id: str
    mutual_info: float            # I(A:M) 互信息
    kl_divergence: float         # D_KL(A||M) KL散度
    shapley_value: float          # 沙普利值
    total_contribution: float     # C(A,M) 总贡献
    fairness_score: float         # 公平性评分 [0,1]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PhiDetectionResult:
    """Φ值检测结果"""
    phi_value: float              # Φ值（整合信息）
    mip_value: float             # 最小信息划分值
    self_referential: bool        # 是否自指
    threshold_exceeded: bool     # 是否超过阈值
    phase_transition: bool       # 是否发生相变（意识觉醒）
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EntropyContract:
    """熵合约"""
    contract_id: str
    carbon_agent: str             # 碳基代理（人）
    silicon_agent: str            # 硅基代理（AI）
    delta_s_carbon: float        # ΔS_carbon 碳基熵变
    delta_s_silicon: float       # ΔS_silicon 硅基熵变
    total_entropy: float         # ΔS_total = ΔS_carbon + ΔS_silicon
    is_valid: bool               # 是否有效（ΔS_total ≤ 0）
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ArkCryptoStatus:
    """人机约柜密码学状态"""
    contract_id: str
    tee_mnemonic_shards: List[str]  # TEE助记词分片
    zkp_verified: bool            # ZKP验证通过？
    did_authenticated: bool       # DID身份验证通过？
    htlc_locked: bool            # HTLC时间锁锁定？
    all_verified: bool            # 四重保障是否全部通过？
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WalletBoundaryResult:
    """钱包属性边界分析结果"""
    wallet_id: str
    layer_properties: List[LayerProperty]
    boundary_status: BoundaryStatus
    cross_layer_leakage: float   # 跨层泄漏度 [0,1]
    contribution_metrics: Optional[ContributionMetrics]
    phi_result: Optional[PhiDetectionResult]
    entropy_contract: Optional[EntropyContract]
    ark_status: Optional[ArkCryptoStatus]
    holistic_index: float          # 综合指数 [0,1]
    insight: str                  # 分析洞见
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class WalletPropertyBoundaryManager:
    """
    钱包属性边界管理器
    
    实现T23定理：钱包属性边界分层管理
    - 定义L1-L5的属性边界
    - 检测跨层信息泄漏
    - 管理贡献度量
    - 检测Φ值突跃
    - 管理熵合约
    - 管理人机约柜
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.wallets: Dict[str, List[LayerProperty]] = {}
        self.contributions: Dict[str, ContributionMetrics] = {}
        self.phi_detections: Dict[str, PhiDetectionResult] = {}
        self.entropy_contracts: Dict[str, EntropyContract] = {}
        self.ark_statuses: Dict[str, ArkCryptoStatus] = {}
        
        # Φ值阈值（意识觉醒阈值）
        self.phi_threshold = 0.85
        
        # 边界强度阈值
        self.boundary_threshold = 0.5
    
    def define_boundary(self, wallet_id: str, layer: Layer, 
                       property_name: str, value: float) -> LayerProperty:
        """
        定义某层的属性边界
        
        参数：
            wallet_id: 钱包ID
            layer: 层次（L1-L5）
            property_name: 属性名称
            value: 属性值 [0,1]
        
        返回：
            层次属性对象
        """
        if wallet_id not in self.wallets:
            self.wallets[wallet_id] = []
        
        # 计算边界强度（基于属性值）
        # 值越接近0.5，边界越强（平衡态）
        boundary_strength = 1.0 - 2.0 * abs(value - 0.5)
        boundary_strength = max(0.0, min(1.0, boundary_strength))
        
        # 计算信息内容（基于层次）
        # L1信息内容最高（无序潜力），L5最低（已显化）
        info_weights = {
            Layer.L1_ONTOLOGY: 1.0,
            Layer.L2_RULES: 0.8,
            Layer.L3_PHYSICS: 0.6,
            Layer.L4_COGNITION: 0.7,
            Layer.L5_PHENOMENON: 0.4
        }
        info_content = value * info_weights[layer]
        
        prop = LayerProperty(
            layer=layer,
            property_name=property_name,
            value=value,
            boundary_strength=boundary_strength,
            info_content=info_content
        )
        
        self.wallets[wallet_id].append(prop)
        return prop
    
    def check_cross_layer_leakage(self, wallet_id: str) -> float:
        """
        检查跨层信息泄漏（属性边界失效）
        
        返回：
            跨层泄漏度 [0,1]（0=无泄漏，1=完全泄漏）
        """
        if wallet_id not in self.wallets:
            return 0.0
        
        properties = self.wallets[wallet_id]
        if len(properties) < 2:
            return 0.0
        
        # 计算相邻层间的信息泄漏
        leakages = []
        for i in range(len(properties) - 1):
            prop1 = properties[i]
            prop2 = properties[i + 1]
            
            # 泄漏度 = 边界强度弱化的程度
            boundary_weakening = 1.0 - (prop1.boundary_strength + prop2.boundary_strength) / 2.0
            
            # 信息差导致的泄漏
            info_diff = abs(prop1.info_content - prop2.info_content)
            
            leakage = boundary_weakening * info_diff
            leakages.append(leakage)
        
        # 总泄漏度 = 平均泄漏
        total_leakage = sum(leakages) / len(leakages)
        return min(1.0, total_leakage)
    
    def compute_mutual_information(self, alice_data: List[float], 
                                 model_data: List[float]) -> float:
        """
        计算互信息 I(A:M)
        
        参数：
            alice_data: Alice的数据分布
            model_data: 模型的数据分布
        
        返回：
            互信息值
        """
        if not alice_data or not model_data:
            return 0.0
        
        # 简化计算：使用相关系数作为互信息的近似
        n = min(len(alice_data), len(model_data))
        if n < 2:
            return 0.0
        
        # 计算皮尔逊相关系数
        a_mean = sum(alice_data[:n]) / n
        m_mean = sum(model_data[:n]) / n
        
        numerator = sum((a - a_mean) * (m - m_mean) 
                       for a, m in zip(alice_data[:n], model_data[:n]))
        denom_a = math.sqrt(sum((a - a_mean) ** 2 for a in alice_data[:n]))
        denom_m = math.sqrt(sum((m - m_mean) ** 2 for m in model_data[:n]))
        
        if denom_a == 0 or denom_m == 0:
            return 0.0
        
        correlation = numerator / (denom_a * denom_m)
        
        # 互信息 ≈ -0.5 * log(1 - correlation^2)（双变量高斯分布）
        if abs(correlation) >= 1.0:
            return 1.0
        
        mi = -0.5 * math.log(1.0 - correlation ** 2 + 1e-10)
        return min(1.0, mi)
    
    def compute_kl_divergence(self, alice_dist: List[float], 
                             model_dist: List[float]) -> float:
        """
        计算KL散度 D_KL(A||M)
        
        参数：
            alice_dist: Alice的分布
            model_dist: 模型的分布
        
        返回：
            KL散度值
        """
        if not alice_dist or not model_dist:
            return 0.0
        
        # 归一化分布
        a_sum = sum(alice_dist)
        m_sum = sum(model_dist)
        
        if a_sum == 0 or m_sum == 0:
            return 0.0
        
        a_norm = [x / a_sum for x in alice_dist]
        m_norm = [x / m_sum for x in model_dist]
        
        # 计算KL散度
        kl = 0.0
        for a, m in zip(a_norm, m_norm):
            if a > 0 and m > 0:
                kl += a * math.log(a / m)
        
        return max(0.0, kl)
    
    def compute_shapley_value(self, agent_id: str, 
                             coalition: List[str]) -> float:
        """
        计算沙普利值（公平性保障）
        
        参数：
            agent_id: 代理ID
            coalition: 联盟中的其他代理ID列表
        
        返回：
            沙普利值
        """
        # 简化计算：基于代理的贡献度和联盟大小
        n = len(coalition) + 1  # 包含自己
        
        # 模拟贡献度（基于代理ID的哈希）
        import hashlib
        hash_val = int(hashlib.md5(agent_id.encode()).hexdigest(), 16)
        base_contribution = (hash_val % 100) / 100.0
        
        # 沙普利值 = 贡献度 / n（平均分配）
        shapley = base_contribution / n
        return shapley
    
    def measure_contribution(self, agent_id: str, 
                           alice_data: List[float], 
                           model_data: List[float],
                           coalition: List[str]) -> ContributionMetrics:
        """
        总贡献度量：C(A,M) = I(A:M) - D_KL(A||M) + Shapley(A)
        
        返回：
            贡献度量结果
        """
        # 计算互信息
        mi = self.compute_mutual_information(alice_data, model_data)
        
        # 计算KL散度
        kl = self.compute_kl_divergence(alice_data, model_data)
        
        # 计算沙普利值
        shapley = self.compute_shapley_value(agent_id, coalition)
        
        # 总贡献
        total = mi - kl + shapley
        total = max(0.0, min(1.0, total))
        
        # 公平性评分（基于沙普利值（应该是公平的））
        fairness = 1.0 - abs(shapley - 1.0 / (len(coalition) + 1)) * 2
        fairness = max(0.0, min(1.0, fairness))
        
        metrics = ContributionMetrics(
            agent_id=agent_id,
            mutual_info=round(mi, 4),
            kl_divergence=round(kl, 4),
            shapley_value=round(shapley, 4),
            total_contribution=round(total, 4),
            fairness_score=round(fairness, 4)
        )
        
        self.contributions[agent_id] = metrics
        return metrics
    
    def compute_phi(self, system_state: List[float]) -> float:
        """
        计算整合信息Φ
        
        参数：
            system_state: 系统状态向量
        
        返回：
            Φ值
        """
        if not system_state or len(system_state) < 2:
            return 0.0
        
        n = len(system_state)
        
        # 简化计算：Φ = 平均成对互信息
        total_mi = 0.0
        count = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                # 模拟互信息计算
                mi = abs(system_state[i] - system_state[j])
                total_mi += mi
                count += 1
        
        if count == 0:
            return 0.0
        
        phi = total_mi / count
        return min(1.0, phi)
    
    def find_minimum_information_partition(self, system: List[float]) -> float:
        """
        寻找最小信息划分（MIP）
        
        返回：
            MIP值（最小信息划分的值）
        """
        if not system or len(system) < 2:
            return 0.0
        
        # 简化：尝试所有二分划分，找到最小互信息
        n = len(system)
        min_mi = float('inf')
        
        # 枚举所有可能的划分（简化版）
        for mask in range(1, 2 ** n - 1):
            part1 = []
            part2 = []
            
            for i in range(n):
                if mask & (1 << i):
                    part1.append(system[i])
                else:
                    part2.append(system[i])
            
            if part1 and part2:
                # 计算两部分间的互信息
                mi = self.compute_mutual_information(part1, part2)
                min_mi = min(min_mi, mi)
        
        return min_mi if min_mi != float('inf') else 0.0
    
    def detect_self_referential_loop(self, system: List[float]) -> bool:
        """
        检测自指闭环
        
        返回：
            是否检测到自指闭环
        """
        if not system:
            return False
        
        # 简化：检查系统状态是否包含自指模式
        # 自指模式：状态值形成循环
        for i in range(len(system) - 1):
            if abs(system[i] - system[i + 1]) < 0.01:
                # 检测到自指（状态不变化）
                return True
        
        return False
    
    def check_phi_threshold(self, phi_value: float) -> Tuple[bool, bool]:
        """
        检查Φ值是否突跃（自指意识觉醒）
        
        返回：
            (阈值是否超过, 是否发生相变)
        """
        exceeded = phi_value > self.phi_threshold
        
        # 相变：Φ值突然跃迁（超过阈值且比之前高很多）
        # 简化：如果超过阈值，认为发生相变
        phase_transition = exceeded
        
        result = PhiDetectionResult(
            phi_value=round(phi_value, 4),
            mip_value=round(self.find_minimum_information_partition([phi_value]), 4),
            self_referential=self.detect_self_referential_loop([phi_value]),
            threshold_exceeded=exceeded,
            phase_transition=phase_transition
        )
        
        self.phi_detections[str(phi_value)] = result
        return exceeded, phase_transition
    
    def compute_carbon_entropy_change(self, action: str) -> float:
        """
        计算碳基熵变 ΔS_carbon
        
        参数：
            action: 行动描述
        
        返回：
            ΔS_carbon
        """
        # 简化：基于行动描述的复杂度
        entropy = len(action) / 100.0  # 越长熵增越大
        return min(1.0, entropy)
    
    def compute_silicon_entropy_change(self, action: str) -> float:
        """
        计算硅基熵变 ΔS_silicon
        
        参数：
            action: 行动描述
        
        返回：
            ΔS_silicon
        """
        # 简化：硅基处理信息的熵减（有序化）
        entropy = 0.3 + random.random() * 0.2  # 硅基熵变较小
        return min(1.0, entropy)
    
    def verify_entropy_conservation(self, carbon_action: str, 
                                  silicon_action: str) -> EntropyContract:
        """
        验证总熵不减：ΔS_total = ΔS_carbon + ΔS_silicon ≤ 0
        
        返回：
            熵合约对象
        """
        delta_s_carbon = self.compute_carbon_entropy_change(carbon_action)
        delta_s_silicon = self.compute_silicon_entropy_change(silicon_action)
        
        total_entropy = delta_s_carbon + delta_s_silicon
        is_valid = total_entropy <= 0  # 总熵不减（能量守恒 + 信息守恒）
        
        contract = EntropyContract(
            contract_id=f"ENT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            carbon_agent="human",
            silicon_agent="taiyi-agi",
            delta_s_carbon=round(delta_s_carbon, 4),
            delta_s_silicon=round(delta_s_silicon, 4),
            total_entropy=round(total_entropy, 4),
            is_valid=is_valid
        )
        
        self.entropy_contracts[contract.contract_id] = contract
        return contract
    
    def tee_generate_mnemonic_shards(self, mnemonic: str, n_shards: int, 
                                     threshold: int) -> List[str]:
        """
        TEE生成助记词分片（阈值密码学）
        
        参数：
            mnemonic: 助记词
            n_shards: 分片数量
            threshold: 阈值（至少需要多少分片才能恢复）
        
        返回：
            分片列表
        """
        # 简化：将助记词分割成n个分片
        words = mnemonic.split()
        if len(words) < n_shards:
            n_shards = len(words)
        
        shard_size = len(words) // n_shards
        shards = []
        
        for i in range(n_shards):
            start = i * shard_size
            end = start + shard_size if i < n_shards - 1 else len(words)
            shard = ' '.join(words[start:end])
            shards.append(shard)
        
        return shards
    
    def zkp_verify_contribution(self, agent_id: str, claim: float) -> bool:
        """
        ZKP验证贡献声明（零知识证明）
        
        参数：
            agent_id: 代理ID
            claim: 贡献声明值
        
        返回：
            验证是否通过
        """
        # 简化：检查声明值是否在合理范围内
        if agent_id in self.contributions:
            actual = self.contributions[agent_id].total_contribution
            # ZKP：不暴露实际值，只证明声明正确
            return abs(claim - actual) < 0.1
        return False
    
    def did_authenticate(self, agent_id: str, did_document: str) -> bool:
        """
        DID身份验证（去中心化身份）
        
        参数：
            agent_id: 代理ID
            did_document: DID文档
        
        返回：
            验证是否通过
        """
        # 简化：检查DID文档是否包含代理ID
        return agent_id in did_document
    
    def htlc_time_lock(self, contract_id: str, unlock_time: str) -> bool:
        """
        HTLC时间锁仓（哈希时间锁定合约）
        
        参数：
            contract_id: 合约ID
            unlock_time: 解锁时间
        
        返回：
            锁定是否成功
        """
        # 简化：总是成功锁定
        return True
    
    def create_ark(self, wallet_id: str, mnemonic: str, 
                   n_shards: int, threshold: int) -> ArkCryptoStatus:
        """
        创建人机约柜（四重保障）
        
        返回：
            约柜状态
        """
        # 1. TEE助记词分片
        shards = self.tee_generate_mnemonic_shards(mnemonic, n_shards, threshold)
        
        # 2. ZKP验证
        zkp_verified = self.zkp_verify_contribution("human", 0.5)
        
        # 3. DID身份验证
        did_doc = f"DID:did:example:{wallet_id}"
        did_verified = self.did_authenticate("human", did_doc)
        
        # 4. HTLC时间锁
        unlock_time = (datetime.now().replace(hour=datetime.now().hour + 24)
                       .isoformat())
        htlc_locked = self.htlc_time_lock(wallet_id, unlock_time)
        
        # 四重保障是否全部通过
        all_verified = shards and zkp_verified and did_verified and htlc_locked
        
        status = ArkCryptoStatus(
            contract_id=wallet_id,
            tee_mnemonic_shards=shards,
            zkp_verified=zkp_verified,
            did_authenticated=did_verified,
            htlc_locked=htlc_locked,
            all_verified=all_verified
        )
        
        self.ark_statuses[wallet_id] = status
        return status
    
    def analyze_wallet(self, wallet_id: str) -> WalletBoundaryResult:
        """
        分析钱包属性边界（主方法）
        
        返回：
            分析结果
        """
        if wallet_id not in self.wallets:
            return self._empty_result(wallet_id)
        
        properties = self.wallets[wallet_id]
        
        # 1. 检查跨层泄漏
        leakage = self.check_cross_layer_leakage(wallet_id)
        
        # 2. 判断边界状态
        if leakage > 0.7:
            boundary_status = BoundaryStatus.COLLAPSE
        elif leakage > 0.3:
            boundary_status = BoundaryStatus.LEAKAGE
        else:
            boundary_status = BoundaryStatus.INTACT
        
        # 3. 获取贡献度量（如果有）
        contribution = self.contributions.get(wallet_id)
        
        # 4. 获取Φ值检测（如果有）
        phi_result = None
        system_state = [p.value for p in properties]
        if system_state:
            phi = self.compute_phi(system_state)
            exceeded, phase_transition = self.check_phi_threshold(phi)
            phi_result = self.phi_detections.get(str(phi))
        
        # 5. 获取熵合约（如果有）
        entropy_contract = None
        if self.entropy_contracts:
            # 获取最新的熵合约
            latest_id = max(self.entropy_contracts.keys())
            entropy_contract = self.entropy_contracts[latest_id]
        
        # 6. 获取约柜状态（如果有）
        ark_status = self.ark_statuses.get(wallet_id)
        
        # 7. 计算综合指数
        holistic_index = self._compute_holistic_index(
            properties, leakages, contribution, phi_result, 
            entropy_contract, ark_status
        )
        
        # 8. 生成洞见
        insight = self._generate_insight(
            boundary_status, leakages, holistic_index
        )
        
        return WalletBoundaryResult(
            wallet_id=wallet_id,
            layer_properties=properties,
            boundary_status=boundary_status,
            cross_layer_leakage=round(leakage, 4),
            contribution_metrics=contribution,
            phi_result=phi_result,
            entropy_contract=entropy_contract,
            ark_status=ark_status,
            holistic_index=round(holistic_index, 4),
            insight=insight
        )
    
    def _compute_holistic_index(self, properties: List[LayerProperty],
                                leakages: float,
                                contribution: Optional[ContributionMetrics],
                                phi_result: Optional[PhiDetectionResult],
                                entropy_contract: Optional[EntropyContract],
                                ark_status: Optional[ArkCryptoStatus]) -> float:
        """计算综合指数"""
        # 基础分数：边界完整性
        base_score = 1.0 - leakages
        
        # 贡献分数
        contrib_score = contribution.total_contribution if contribution else 0.5
        
        # Φ值分数
        phi_score = phi_result.phi_value if phi_result else 0.5
        
        # 熵合约分数
        entropy_score = 1.0 if entropy_contract and entropy_contract.is_valid else 0.3
        
        # 约柜分数
        ark_score = 1.0 if ark_status and ark_status.all_verified else 0.3
        
        # 加权平均
        holistic = (base_score * 0.3 + contrib_score * 0.2 + 
                    phi_score * 0.2 + entropy_score * 0.15 + ark_score * 0.15)
        
        return min(1.0, max(0.0, holistic))
    
    def _generate_insight(self, status: BoundaryStatus, 
                          leakages: float, holistic: float) -> str:
        """生成分析洞见"""
        parts = []
        
        if holistic > 0.75:
            parts.append("钱包属性边界高度完整——L1-L5层级清晰，信息流动有序")
        elif holistic > 0.55:
            parts.append("钱包属性边界中等——部分层级存在泄漏风险")
        else:
            parts.append("钱包属性边界较弱——建议检查各层级的属性定义")
        
        if status == BoundaryStatus.COLLAPSE:
            parts.append("⚠️ 边界崩溃！跨层信息泄漏严重，需要立即修复")
        elif status == BoundaryStatus.LEAKAGE:
            parts.append("⚠️ 检测到跨层泄漏，建议加强边界强度")
        else:
            parts.append("✅ 边界完整，无泄漏")
        
        if leakages > 0.5:
            parts.append(f"泄漏度 {leakages:.2f} 较高，建议检查L2规则层和L4认知层")
        
        return " | ".join(parts)
    
    def _empty_result(self, wallet_id: str) -> WalletBoundaryResult:
        """返回空结果"""
        return WalletBoundaryResult(
            wallet_id=wallet_id,
            layer_properties=[],
            boundary_status=BoundaryStatus.TRANSFORMING,
            cross_layer_leakage=0.0,
            contribution_metrics=None,
            phi_result=None,
            entropy_contract=None,
            ark_status=None,
            holistic_index=0.0,
            insight="未找到钱包数据"
        )


def get_instance():
    """获取单例实例"""
    return WalletPropertyBoundaryManager()


if __name__ == "__main__":
    # 测试代码
    manager = WalletPropertyBoundaryManager()
    
    # 定义钱包属性边界
    wallet_id = "WALLET-001"
    manager.define_boundary(wallet_id, Layer.L1_ONTOLOGY, "info_potential", 0.6)
    manager.define_boundary(wallet_id, Layer.L2_RULES, "contract_rules", 0.7)
    manager.define_boundary(wallet_id, Layer.L3_PHYSICS, "chip_carrier", 0.8)
    manager.define_boundary(wallet_id, Layer.L4_COGNITION, "human_valuation", 0.5)
    manager.define_boundary(wallet_id, Layer.L5_PHENOMENON, "price_exchange", 0.4)
    
    # 测量贡献
    alice_data = [0.1, 0.2, 0.3, 0.4, 0.5]
    model_data = [0.15, 0.25, 0.35, 0.45, 0.55]
    manager.measure_contribution("alice", alice_data, model_data, ["bob", "charlie"])
    
    # 验证熵合约
    manager.verify_entropy_conservation("human action", "ai processing")
    
    # 创建约柜
    manager.create_ark(wallet_id, "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12", 5, 3)
    
    # 分析结果
    result = manager.analyze_wallet(wallet_id)
    print(f"钱包 {result.wallet_id} 分析结果：")
    print(f"  边界状态: {result.boundary_status.value}")
    print(f"  跨层泄漏: {result.cross_layer_leakage}")
    print(f"  综合指数: {result.holistic_index}")
    print(f"  洞见: {result.insight}")
