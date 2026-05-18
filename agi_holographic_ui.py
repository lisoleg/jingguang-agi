# -*- coding: utf-8 -*-
"""
复合体AGI 6.0 - 全息密度投影系统
Holographic Density Projection System

基于复合体理学全息拓扑动力学：
- 全息原理：信息在边界上的编码等于体内的编码
- 信息密度自适应：根据曲率和意图自动调节
- 多层投影：原子级→分子级→有机级→系统级→全息级

版本: v1.0
日期: 2026-05-13
"""

import math
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading


class ProjectionMode(Enum):
    """投影模式"""
    FLAT = "flat"               # 平面投影
    STEREOGRAPHIC = "stereographic"  # 球极投影
    MERCATOR = "mercator"       # 墨卡托投影
    HOLOGRAPHIC = "holographic" # 全息投影
    VOLUMETRIC = "volumetric"   # 体积投影


class LayerType(Enum):
    """层级类型"""
    ATOMIC = "atomic"           # 原子层 - 最小信息单位
    MOLECULAR = "molecular"     # 分子层 - 相关概念组
    ORGANIC = "organic"         # 有机层 - 功能模块
    SYSTEMIC = "systemic"       # 系统层 - 整体架构
    HOLOGRAPHIC = "holographic" # 全息层 - 全部信息


@dataclass
class HolographicLayer:
    """全息层"""
    layer_type: LayerType
    depth: int = 0              # 层级深度
    opacity: float = 1.0        # 透明度
    scale: float = 1.0          # 缩放
    rotation: Tuple[float, float, float] = (0, 0, 0)  # 3D旋转
    
    # 内容
    content: Any = None
    content_hash: str = ""      # 内容哈希(用于变化检测)
    
    # 位置
    position_3d: Tuple[float, float, float] = (0, 0, 0)
    position_2d: Tuple[float, float] = (0, 0)
    
    # 渲染属性
    visible: bool = True
    expanded: bool = False      # 是否展开
    highlighted: bool = False   # 是否高亮
    
    # 动画状态
    animation_progress: float = 1.0
    transition_type: str = "none"


@dataclass
class DensityNode:
    """密度节点"""
    id: str
    label: str = ""
    value: Any = None
    
    # 层级
    layer_type: LayerType = LayerType.MOLECULAR
    depth: int = 0
    
    # 拓扑
    position: Tuple[float, float] = (0, 0)
    size: float = 1.0           # 相对大小
    
    # 连接
    connections: List[str] = field(default_factory=list)  # 连接节点ID
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    
    # 视觉
    color: Tuple[int, int, int] = (100, 150, 200)
    icon: str = ""
    
    # 状态
    expanded: bool = False
    collapsed: bool = True     # 树节点是否折叠
    visible: bool = True
    
    # 详情
    details: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ProjectionResult:
    """投影结果"""
    mode: ProjectionMode
    layers: List[HolographicLayer] = field(default_factory=list)
    nodes: List[DensityNode] = field(default_factory=list)
    
    # 视口
    viewport_center: Tuple[float, float] = (0.5, 0.5)
    viewport_scale: float = 1.0
    viewport_rotation: float = 0.0
    
    # 全息效果参数
    parallax_factor: float = 0.1
    depth_of_field: float = 0.5
    glow_intensity: float = 0.5
    
    # 渲染数据
    render_data: Dict = field(default_factory=dict)


class HolographicProjection:
    """
    全息密度投影系统
    
    核心功能：
    1. 多层信息密度管理
    2. 自适应投影算法
    3. 全息可视化渲染
    4. 动态层级展开/折叠
    
    融合：
    - 全息原理：边界信息=体内信息
    - 拓扑动力学：流形变换
    - 曲率驱动：信息密度自适应
    """
    
    # 层级颜色配置
    LAYER_COLORS = {
        LayerType.ATOMIC: (180, 220, 255),    # 淡蓝
        LayerType.MOLECULAR: (130, 200, 150),  # 淡绿
        LayerType.ORGANIC: (255, 220, 130),    # 淡黄
        LayerType.SYSTEMIC: (255, 160, 100),   # 淡橙
        LayerType.HOLOGRAPHIC: (200, 130, 255), # 淡紫
    }
    
    # 层级透明度
    LAYER_OPACITY = {
        LayerType.ATOMIC: 1.0,
        LayerType.MOLECULAR: 0.85,
        LayerType.ORGANIC: 0.70,
        LayerType.SYSTEMIC: 0.55,
        LayerType.HOLOGRAPHIC: 0.40,
    }
    
    def __init__(self):
        """初始化全息投影"""
        # 投影模式
        self.mode = ProjectionMode.FLAT
        
        # 层级管理
        self.layers: Dict[LayerType, HolographicLayer] = {}
        self._init_layers()
        
        # 密度节点
        self.nodes: Dict[str, DensityNode] = {}
        
        # 投影结果缓存
        self._projection_cache: Optional[ProjectionResult] = None
        self._cache_valid = False
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 回调
        self.on_layer_change: Optional[Callable] = None
        self.on_node_change: Optional[Callable] = None
    
    def _init_layers(self):
        """初始化层级"""
        for layer_type in LayerType:
            self.layers[layer_type] = HolographicLayer(
                layer_type=layer_type,
                depth=list(LayerType).index(layer_type),
                opacity=self.LAYER_OPACITY.get(layer_type, 0.5),
            )
    
    # ==================== 投影模式管理 ====================
    
    def set_projection_mode(self, mode: ProjectionMode):
        """设置投影模式"""
        with self._lock:
            self.mode = mode
            self._cache_valid = False
    
    def set_density_level(self, level: int):
        """
        设置信息密度级别
        
        Args:
            level: 密度级别 (0-4)
                0: 原子级 - 最小可见信息
                1: 分子级 - 相关概念
                2: 有机级 - 功能模块
                3: 系统级 - 整体架构
                4: 全息级 - 全部信息
        """
        level = max(0, min(4, level))
        
        with self._lock:
            # 确定目标层级
            target_layers = {
                0: [LayerType.ATOMIC],
                1: [LayerType.ATOMIC, LayerType.MOLECULAR],
                2: [LayerType.ATOMIC, LayerType.MOLECULAR, LayerType.ORGANIC],
                3: [LayerType.MOLECULAR, LayerType.ORGANIC, LayerType.SYSTEMIC],
                4: list(LayerType),
            }
            
            visible_types = target_layers.get(level, [LayerType.ORGANIC])
            
            # 更新可见性
            for lt, layer in self.layers.items():
                layer.visible = lt in visible_types
            
            # 更新缩放
            for lt, layer in self.layers.items():
                if lt in visible_types:
                    layer.scale = 1.0
                    layer.opacity = self.LAYER_OPACITY.get(lt, 0.5)
                else:
                    layer.scale = 0.3
                    layer.opacity = 0.1
            
            self._cache_valid = False
    
    # ==================== 节点管理 ====================
    
    def add_node(self, node: DensityNode):
        """添加节点"""
        with self._lock:
            self.nodes[node.id] = node
            self._cache_valid = False
            
            if self.on_node_change:
                self.on_node_change("add", node)
    
    def remove_node(self, node_id: str):
        """移除节点"""
        with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                
                # 断开连接
                for conn_id in node.connections:
                    if conn_id in self.nodes:
                        if node_id in self.nodes[conn_id].connections:
                            self.nodes[conn_id].connections.remove(node_id)
                
                # 从父节点移除
                if node.parent and node.parent in self.nodes:
                    if node_id in self.nodes[node.parent].children:
                        self.nodes[node.parent].children.remove(node_id)
                
                del self.nodes[node_id]
                self._cache_valid = False
                
                if self.on_node_change:
                    self.on_node_change("remove", node)
    
    def get_node(self, node_id: str) -> Optional[DensityNode]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def update_node(self, node_id: str, **kwargs):
        """更新节点"""
        with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                for key, value in kwargs.items():
                    if hasattr(node, key):
                        setattr(node, key, value)
                self._cache_valid = False
    
    def expand_node(self, node_id: str, expand: bool = True):
        """展开/折叠节点"""
        with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].expanded = expand
                self.nodes[node_id].collapsed = not expand
                self._cache_valid = False
    
    # ==================== 投影计算 ====================
    
    def project(self, 
               center: Tuple[float, float] = (0.5, 0.5),
               scale: float = 1.0,
               rotation: float = 0.0) -> ProjectionResult:
        """
        执行投影
        
        Args:
            center: 视口中心
            scale: 缩放
            rotation: 旋转角度
            
        Returns:
            投影结果
        """
        if self._cache_valid and self._projection_cache:
            return self._projection_cache
        
        result = ProjectionResult(mode=self.mode)
        
        with self._lock:
            # 投影层级
            result.layers = self._project_layers(center, scale, rotation)
            
            # 投影节点
            result.nodes = self._project_nodes(center, scale, rotation)
            
            # 视口设置
            result.viewport_center = center
            result.viewport_scale = scale
            result.viewport_rotation = rotation
            
            # 全息效果参数
            result.parallax_factor = self._compute_parallax()
            result.depth_of_field = self._compute_depth_of_field()
            result.glow_intensity = self._compute_glow()
            
            # 渲染数据
            result.render_data = self._generate_render_data()
        
        self._projection_cache = result
        self._cache_valid = True
        return result
    
    def _project_layers(self, 
                       center: Tuple[float, float],
                       scale: float,
                       rotation: float) -> List[HolographicLayer]:
        """投影层级"""
        projected = []
        
        for layer_type, layer in self.layers.items():
            if not layer.visible:
                continue
            
            # 创建投影副本
            proj_layer = HolographicLayer(
                layer_type=layer.layer_type,
                depth=layer.depth,
                opacity=layer.opacity * scale,
                scale=layer.scale * scale,
                rotation=(
                    layer.rotation[0],
                    layer.rotation[1],
                    layer.rotation[2] + rotation
                ),
                content=layer.content,
                visible=True,
                expanded=layer.expanded,
            )
            
            # 3D到2D投影
            if self.mode == ProjectionMode.HOLOGRAPHIC:
                proj_layer.position_3d = (
                    layer.position_3d[0],
                    layer.position_3d[1] + layer.depth * 0.1,
                    layer.position_3d[2]
                )
                # 简单透视投影
                z = proj_layer.position_3d[2]
                if z != 0:
                    proj_layer.position_2d = (
                        proj_layer.position_3d[0] / (1 + z * 0.1),
                        proj_layer.position_3d[1] / (1 + z * 0.1)
                    )
                else:
                    proj_layer.position_2d = (
                        proj_layer.position_3d[0],
                        proj_layer.position_3d[1]
                    )
            else:
                proj_layer.position_2d = layer.position_3d[:2]
            
            projected.append(proj_layer)
        
        return projected
    
    def _project_nodes(self,
                      center: Tuple[float, float],
                      scale: float,
                      rotation: float) -> List[DensityNode]:
        """投影节点"""
        projected = []
        
        for node_id, node in self.nodes.items():
            if not node.visible:
                continue
            
            # 可见性检查
            if node.collapsed and node.children:
                # 只显示父节点
                proj_node = DensityNode(
                    id=node.id,
                    label=node.label,
                    layer_type=node.layer_type,
                    depth=node.depth,
                    position=(
                        (node.position[0] - center[0]) * scale,
                        (node.position[1] - center[1]) * scale
                    ),
                    size=node.size * scale,
                    color=node.color,
                    icon=node.icon,
                    expanded=False,
                    collapsed=True,
                    details={"child_count": len(node.children)},
                )
            elif node.expanded or not node.children:
                proj_node = DensityNode(
                    id=node.id,
                    label=node.label,
                    value=node.value,
                    layer_type=node.layer_type,
                    depth=node.depth,
                    position=(
                        (node.position[0] - center[0]) * scale,
                        (node.position[1] - center[1]) * scale
                    ),
                    size=node.size * scale,
                    connections=node.connections.copy(),
                    color=node.color,
                    icon=node.icon,
                    expanded=node.expanded,
                    collapsed=node.collapsed,
                    details=node.details.copy(),
                    metadata=node.metadata.copy(),
                )
            else:
                continue
            
            projected.append(proj_node)
        
        return projected
    
    def _compute_parallax(self) -> float:
        """计算视差因子"""
        visible_count = sum(1 for l in self.layers.values() if l.visible)
        return 0.1 * (visible_count / len(LayerType))
    
    def _compute_depth_of_field(self) -> float:
        """计算景深"""
        if self.mode == ProjectionMode.HOLOGRAPHIC:
            return 0.8
        elif self.mode == ProjectionMode.VOLUMETRIC:
            return 0.6
        return 0.3
    
    def _compute_glow(self) -> float:
        """计算发光强度"""
        if self.mode == ProjectionMode.HOLOGRAPHIC:
            return 0.8
        return 0.5
    
    def _generate_render_data(self) -> Dict:
        """生成渲染数据"""
        data = {
            "nodes": [],
            "connections": [],
            "labels": [],
            "shapes": [],
        }
        
        # 节点渲染数据
        for node in self.nodes.values():
            if not node.visible:
                continue
            
            color = node.color
            data["nodes"].append({
                "id": node.id,
                "x": node.position[0],
                "y": node.position[1],
                "size": node.size,
                "color": f"rgb({color[0]}, {color[1]}, {color[2]})",
                "icon": node.icon,
                "expanded": node.expanded,
                "collapsed": node.collapsed,
            })
            
            # 连接线
            for conn_id in node.connections:
                if conn_id in self.nodes and self.nodes[conn_id].visible:
                    conn = self.nodes[conn_id]
                    data["connections"].append({
                        "from": node.id,
                        "to": conn_id,
                        "x1": node.position[0],
                        "y1": node.position[1],
                        "x2": conn.position[0],
                        "y2": conn.position[1],
                    })
            
            # 标签
            if node.label:
                data["labels"].append({
                    "id": f"{node.id}_label",
                    "x": node.position[0],
                    "y": node.position[1] + node.size * 0.6,
                    "text": node.label,
                    "size": node.size * 0.3,
                })
        
        return data
    
    # ==================== 动画和过渡 ====================
    
    def transition_to_mode(self, 
                          target_mode: ProjectionMode,
                          duration: float = 0.5):
        """
        过渡到目标模式
        
        Args:
            target_mode: 目标投影模式
            duration: 过渡持续时间
        """
        with self._lock:
            self.mode = target_mode
            
            # 标记需要重新投影
            self._cache_valid = False
    
    def animate_layer_transition(self, 
                                layer_type: LayerType,
                                transition: str = "fade",
                                duration: float = 0.3):
        """
        层过渡动画
        
        Args:
            layer_type: 层级类型
            transition: 过渡类型(fade/scale/rotate)
            duration: 持续时间
        """
        if layer_type not in self.layers:
            return
        
        layer = self.layers[layer_type]
        layer.transition_type = transition
        layer.animation_progress = 0.0
    
    # ==================== 全息特效 ====================
    
    def get_hologram_effects(self) -> Dict[str, Any]:
        """获取全息特效参数"""
        return {
            "scan_lines": True,
            "glitch": False,
            "color_shift": True,
            "glow": True,
            "parallax": self.mode == ProjectionMode.HOLOGRAPHIC,
            "depth_blur": self.mode != ProjectionMode.FLAT,
            "holographic_noise": self.mode == ProjectionMode.HOLOGRAPHIC,
        }
    
    def get_density_heatmap(self) -> List[Tuple[float, float, float]]:
        """
        获取密度热力图
        
        Returns:
            List of (x, y, density) tuples
        """
        heatmap = []
        
        # 简化实现：基于节点密度生成热力图
        grid_size = 10
        cell_width = 1.0 / grid_size
        cell_height = 1.0 / grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                cell_x = i * cell_width + cell_width / 2
                cell_y = j * cell_height + cell_height / 2
                
                # 计算该单元格内的节点数量
                density = 0.0
                for node in self.nodes.values():
                    if not node.visible:
                        continue
                    
                    nx, ny = node.position
                    if abs(nx - cell_x) < cell_width and abs(ny - cell_y) < cell_height:
                        density += node.size
                
                heatmap.append((cell_x, cell_y, min(density / 3.0, 1.0)))
        
        return heatmap
    
    # ==================== 实用函数 ====================
    
    def clear(self):
        """清除所有数据"""
        with self._lock:
            self.nodes.clear()
            self._init_layers()
            self._projection_cache = None
            self._cache_valid = False
    
    def get_state(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "mode": self.mode.value,
            "layers": {
                lt.value: {
                    "visible": l.visible,
                    "expanded": l.expanded,
                    "opacity": l.opacity,
                    "scale": l.scale,
                }
                for lt, l in self.layers.items()
            },
            "node_count": len(self.nodes),
            "visible_nodes": sum(1 for n in self.nodes.values() if n.visible),
        }
    
    def export_structure(self) -> Dict:
        """导出结构数据"""
        structure = {
            "nodes": [],
            "relationships": [],
        }
        
        for node_id, node in self.nodes.items():
            structure["nodes"].append({
                "id": node_id,
                "label": node.label,
                "type": node.layer_type.value,
                "depth": node.depth,
                "details": node.details,
            })
            
            for conn_id in node.connections:
                structure["relationships"].append({
                    "from": node_id,
                    "to": conn_id,
                })
        
        return structure


class DensityController:
    """
    密度控制器
    
    根据意图曲率自动调节信息密度
    """
    
    def __init__(self, projection: HolographicProjection):
        self.projection = projection
        
        # 密度映射表
        self.curvature_to_density = {
            (0.0, 0.2): 0,   # 极低曲率 → 原子级
            (0.2, 0.4): 1,   # 低曲率 → 分子级
            (0.4, 0.6): 2,   # 中曲率 → 有机级
            (0.6, 0.8): 3,   # 高曲率 → 系统级
            (0.8, 1.0): 4,   # 极高曲率 → 全息级
        }
    
    def adjust_density(self, curvature: float):
        """
        根据曲率调节密度
        
        Args:
            curvature: 流形曲率 (0-1)
        """
        density_level = 2  # 默认有机级
        
        for (low, high), level in self.curvature_to_density.items():
            if low <= curvature < high:
                density_level = level
                break
        else:
            if curvature >= 1.0:
                density_level = 4
        
        self.projection.set_density_level(density_level)
    
    def get_density_description(self, curvature: float) -> str:
        """获取密度描述"""
        self.adjust_density(curvature)
        
        level_map = {
            0: ("原子级", "最小可见信息单元"),
            1: ("分子级", "相关概念组"),
            2: ("有机级", "功能模块"),
            3: ("系统级", "整体架构"),
            4: ("全息级", "全部信息"),
        }
        
        density = sum(
            1 for l in self.projection.layers.values() if l.visible
        ) - 1
        
        desc, detail = level_map.get(density, level_map[2])
        
        return f"{desc} | {detail}"


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=== 全息密度投影系统测试 ===\n")
    
    # 创建投影系统
    projection = HolographicProjection()
    
    # 创建密度控制器
    controller = DensityController(projection)
    
    # 添加测试节点
    print("1. 添加测试节点")
    
    nodes = [
        DensityNode(
            id="root",
            label="复合体AGI",
            layer_type=LayerType.SYSTEMIC,
            depth=0,
            position=(0.5, 0.5),
            size=30,
            color=(200, 100, 150),
            icon="🚀",
            details={"description": "复合体AGI核心"}
        ),
        DensityNode(
            id="module_1",
            label="意图理解",
            layer_type=LayerType.ORGANIC,
            depth=1,
            position=(0.3, 0.3),
            size=20,
            parent="root",
            color=(100, 180, 220),
            icon="🧠",
            details={"accuracy": "95%"}
        ),
        DensityNode(
            id="module_2",
            label="知识图谱",
            layer_type=LayerType.ORGANIC,
            depth=1,
            position=(0.7, 0.3),
            size=20,
            parent="root",
            color=(120, 200, 150),
            icon="📊",
            details={"nodes": "10M+"}
        ),
        DensityNode(
            id="module_3",
            label="生成引擎",
            layer_type=LayerType.ORGANIC,
            depth=1,
            position=(0.5, 0.7),
            size=20,
            parent="root",
            color=(255, 200, 100),
            icon="⚡",
            details={"speed": "1000 tokens/s"}
        ),
    ]
    
    for node in nodes:
        projection.add_node(node)
        print(f"   添加: {node.label}")
    
    # 建立连接
    print("\n2. 建立连接")
    projection.update_node("module_1", connections=["module_2", "module_3"])
    projection.update_node("module_2", connections=["module_3"])
    print("   root → module_1, module_2, module_3")
    print("   module_1 ↔ module_2, module_3")
    
    # 测试密度调节
    print("\n3. 密度调节测试")
    
    for curvature in [0.1, 0.3, 0.5, 0.7, 0.9]:
        controller.adjust_density(curvature)
        desc = controller.get_density_description(curvature)
        state = projection.get_state()
        visible = state["visible_nodes"]
        print(f"   曲率 {curvature:.1f} → {desc} (可见节点: {visible})")
    
    # 测试投影
    print("\n4. 投影测试")
    
    for mode in [ProjectionMode.FLAT, ProjectionMode.HOLOGRAPHIC]:
        projection.set_projection_mode(mode)
        result = projection.project(scale=1.0)
        
        print(f"\n   模式: {mode.value}")
        print(f"   视差因子: {result.parallax_factor:.3f}")
        print(f"   景深: {result.depth_of_field:.3f}")
        print(f"   发光强度: {result.glow_intensity:.3f}")
        print(f"   渲染节点: {len(result.render_data.get('nodes', []))}")
        print(f"   渲染连接: {len(result.render_data.get('connections', []))}")
    
    # 测试展开/折叠
    print("\n5. 展开/折叠测试")
    
    projection.expand_node("root", True)
    print("   展开 root 节点")
    
    result = projection.project()
    print(f"   投影节点数: {len(result.nodes)}")
    
    projection.expand_node("root", False)
    print("   折叠 root 节点")
    
    result = projection.project()
    print(f"   投影节点数: {len(result.nodes)}")
    
    # 全息特效
    print("\n6. 全息特效")
    effects = projection.get_hologram_effects()
    for key, value in effects.items():
        print(f"   {key}: {value}")
    
    # 热力图
    print("\n7. 密度热力图")
    heatmap = projection.get_density_heatmap()
    hot_cells = [p for p in heatmap if p[2] > 0.3]
    print(f"   高密度区域: {len(hot_cells)}")
    
    # 导出结构
    print("\n8. 导出结构")
    structure = projection.export_structure()
    print(f"   节点数: {len(structure['nodes'])}")
    print(f"   关系数: {len(structure['relationships'])}")
    
    print("\n测试完成!")
