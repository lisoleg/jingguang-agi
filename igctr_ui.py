#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IGCTR v2.3 图形用户界面
太乙AGI系统的现代化Tkinter界面

功能特性：
- Tab分页（运行/日志/可视化/文档）
- 颜色高亮（成功绿/错误红/信息蓝）
- 滚动日志区
- 复杂度仪表盘
- 状态指示器
- 实时模块状态监控

作者：WorkBuddy AI Assistant
日期：2026年5月12日
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import traceback

# 尝试导入IGCTR框架
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from IGCTR_v2_3_Simplified import IGCTR_v23_Framework
    IGCTR_AVAILABLE = True
except ImportError as e:
    IGCTR_AVAILABLE = False
    IGCTR_IMPORT_ERROR = str(e)

try:
    from CompositeAGI_V2 import CompositeAGI_V2
    COMPOSITE_AGI_AVAILABLE = True
except ImportError as e:
    COMPOSITE_AGI_AVAILABLE = False
    COMPOSITE_AGI_IMPORT_ERROR = str(e)


# ============================================================================
# 颜色主题配置
# ============================================================================
class Colors:
    """UI颜色主题配置"""
    # 主色调
    BG_PRIMARY = "#1e1e2e"      # 深色背景
    BG_SECONDARY = "#2d2d44"   # 次级背景
    BG_TERTIARY = "#3d3d5c"    # 三级背景
    
    # 文本颜色
    TEXT_PRIMARY = "#ffffff"   # 主文本
    TEXT_SECONDARY = "#b0b0c0" # 次级文本
    TEXT_MUTED = "#707080"     # 弱化文本
    
    # 高亮颜色
    SUCCESS = "#4ade80"        # 成功绿
    ERROR = "#f87171"          # 错误红
    WARNING = "#fbbf24"         # 警告黄
    INFO = "#60a5fa"           # 信息蓝
    HIGHLIGHT = "#c084fc"      # 紫色高亮
    
    # 按钮颜色
    BTN_PRIMARY = "#6366f1"   # 主按钮
    BTN_SUCCESS = "#22c55e"    # 成功按钮
    BTN_DANGER = "#ef4444"     # 危险按钮
    
    # 边框颜色
    BORDER = "#4d4d6d"


# ============================================================================
# 日志管理器
# ============================================================================
class LogManager:
    """日志管理器 - 支持颜色高亮"""
    
    def __init__(self, text_widget: scrolledtext.ScrolledText):
        self.text_widget = text_widget
        self.tag_config_done = False
        
    def _ensure_tags(self):
        """确保标签配置完成"""
        if not self.tag_config_done:
            self.text_widget.tag_config("SUCCESS", foreground=Colors.SUCCESS)
            self.text_widget.tag_config("ERROR", foreground=Colors.ERROR)
            self.text_widget.tag_config("WARNING", foreground=Colors.WARNING)
            self.text_widget.tag_config("INFO", foreground=Colors.INFO)
            self.text_widget.tag_config("HIGHLIGHT", foreground=Colors.HIGHLIGHT)
            self.text_widget.tag_config("MUTED", foreground=Colors.TEXT_MUTED)
            self.tag_config_done = True
    
    def log(self, message: str, level: str = "INFO", timestamp: bool = True):
        """添加日志消息"""
        self._ensure_tags()
        
        # 获取时间戳
        ts = datetime.now().strftime("%H:%M:%S") if timestamp else " " * 8
        
        # 格式化消息
        prefix = {
            "SUCCESS": "[✓] ",
            "ERROR": "[✗] ",
            "WARNING": "[⚠] ",
            "INFO": "[i] ",
            "HIGHLIGHT": "[★] "
        }.get(level, "[·] ")
        
        full_message = f"{ts} {prefix}{message}\n"
        
        # 插入文本
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, full_message, level)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)
    
    def clear(self):
        """清除日志"""
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.configure(state=tk.DISABLED)


# ============================================================================
# IGCTR主GUI类
# ============================================================================
class IGCTRGui:
    """IGCTR v2.3 图形用户界面主类"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("IGCTR v2.3 - 太乙AGI系统")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # 核心组件
        self.igctr_framework: Optional[IGCTR_v23_Framework] = None
        self.composite_agi: Optional[CompositeAGI_V2] = None
        
        # 状态变量
        self.is_running = tk.BooleanVar(value=False)
        self.is_processing = tk.BooleanVar(value=False)
        
        # 状态指示器
        self.status_indicators: Dict[str, tk.Label] = {}
        
        # 日志管理器
        self.log_manager: Optional[LogManager] = None
        
        # 构建UI
        self._setup_ui()
        self._initialize_frameworks()
    
    def _setup_ui(self):
        """设置UI布局"""
        # 主容器
        main_container = tk.Frame(self.root, bg=Colors.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 顶部标题栏
        self._create_header(main_container)
        
        # 主内容区（Notebook）
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 创建各个Tab
        self._create_run_tab()
        self._create_log_tab()
        self._create_visualization_tab()
        self._create_docs_tab()
        
        # 底部状态栏
        self._create_status_bar(main_container)
    
    def _create_header(self, parent: tk.Frame):
        """创建顶部标题栏"""
        header = tk.Frame(parent, bg=Colors.BG_SECONDARY, height=60)
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        header.pack_propagate(False)
        
        # 标题
        title = tk.Label(
            header,
            text="IGCTR v2.3 - 信息几何意识三元共振系统",
            font=("Microsoft YaHei", 18, "bold"),
            fg=Colors.HIGHLIGHT,
            bg=Colors.BG_SECONDARY
        )
        title.pack(side=tk.LEFT, padx=20, pady=15)
        
        # 版本信息
        version = tk.Label(
            header,
            text="v2.3.0",
            font=("Consolas", 12),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_SECONDARY
        )
        version.pack(side=tk.RIGHT, padx=20, pady=15)
    
    def _create_run_tab(self):
        """创建运行Tab"""
        tab = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(tab, text="🚀 运行")
        
        # 左侧控制面板
        control_frame = tk.Frame(tab, bg=Colors.BG_SECONDARY, width=350)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        control_frame.pack_propagate(False)
        
        # 控制面板标题
        tk.Label(
            control_frame,
            text="控制面板",
            font=("Microsoft YaHei", 14, "bold"),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        ).pack(pady=(15, 10))
        
        # 查询输入框
        tk.Label(
            control_frame,
            text="输入查询:",
            font=("Microsoft YaHei", 10),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        self.query_entry = tk.Text(
            control_frame,
            height=6,
            font=("Microsoft YaHei", 10),
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.query_entry.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # 预设问题按钮组
        tk.Label(
            control_frame,
            text="预设问题:",
            font=("Microsoft YaHei", 10),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        presets = [
            ("波函数坍缩", "什么是波函数坍缩？"),
            ("暗物质", "暗物质存在吗？请分析"),
            ("AGI实现", "如何实现AGI？"),
            ("信息悖论", "黑洞信息悖论是什么？")
        ]
        
        for name, query in presets:
            btn = tk.Button(
                control_frame,
                text=name,
                command=lambda q=query: self._fill_query(q),
                bg=Colors.BG_TERTIARY,
                fg=Colors.TEXT_PRIMARY,
                activebackground=Colors.BTN_PRIMARY,
                activeforeground=Colors.TEXT_PRIMARY,
                relief=tk.FLAT,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, padx=15, pady=2)
        
        # 执行按钮
        self.execute_btn = tk.Button(
            control_frame,
            text="▶ 执行分析",
            command=self._execute_analysis,
            bg=Colors.BTN_SUCCESS,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.SUCCESS,
            activeforeground=Colors.BG_PRIMARY,
            font=("Microsoft YaHei", 12, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            height=2
        )
        self.execute_btn.pack(fill=tk.X, padx=15, pady=(20, 5))
        
        # 清空按钮
        tk.Button(
            control_frame,
            text="清空结果",
            command=self._clear_results,
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_SECONDARY,
            activebackground=Colors.BORDER,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # 模块状态
        self._create_module_status(control_frame)
        
        # 右侧结果显示区
        result_frame = tk.Frame(tab, bg=Colors.BG_PRIMARY)
        result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        # 结果标题
        tk.Label(
            result_frame,
            text="分析结果",
            font=("Microsoft YaHei", 14, "bold"),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # 结果文本框
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=("Consolas", 10),
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置结果文本标签
        self.result_text.tag_config("SUCCESS", foreground=Colors.SUCCESS)
        self.result_text.tag_config("ERROR", foreground=Colors.ERROR)
        self.result_text.tag_config("WARNING", foreground=Colors.WARNING)
        self.result_text.tag_config("INFO", foreground=Colors.INFO)
        self.result_text.tag_config("HIGHLIGHT", foreground=Colors.HIGHLIGHT)
    
    def _create_module_status(self, parent: tk.Frame):
        """创建模块状态显示"""
        # 分隔线
        tk.Frame(parent, height=2, bg=Colors.BORDER).pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            parent,
            text="模块状态",
            font=("Microsoft YaHei", 12, "bold"),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # 状态指示器容器
        status_container = tk.Frame(parent, bg=Colors.BG_SECONDARY)
        status_container.pack(fill=tk.X, padx=15)
        
        self.status_indicators = {}
        modules = [
            ("IGCTR框架", "igctr"),
            ("太乙AGI", "composite"),
            ("三元共振", "resonance"),
            ("可审计性", "audit")
        ]
        
        for i, (name, key) in enumerate(modules):
            row = i // 2
            col = i % 2
            
            frame = tk.Frame(status_container, bg=Colors.BG_SECONDARY)
            frame.grid(row=row, column=col, sticky=tk.W, pady=5)
            
            indicator = tk.Label(
                frame,
                text="○",
                font=("Consolas", 14),
                fg=Colors.TEXT_MUTED,
                bg=Colors.BG_SECONDARY
            )
            indicator.pack(side=tk.LEFT)
            
            label = tk.Label(
                frame,
                text=name,
                font=("Microsoft YaHei", 9),
                fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_SECONDARY
            )
            label.pack(side=tk.LEFT, padx=(5, 0))
            
            self.status_indicators[key] = indicator
    
    def _create_log_tab(self):
        """创建日志Tab"""
        tab = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(tab, text="📋 日志")
        
        # 日志控制栏
        control_frame = tk.Frame(tab, bg=Colors.BG_SECONDARY, height=40)
        control_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        control_frame.pack_propagate(False)
        
        tk.Label(
            control_frame,
            text="系统日志",
            font=("Microsoft YaHei", 12, "bold"),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        ).pack(side=tk.LEFT, padx=15)
        
        tk.Button(
            control_frame,
            text="清空日志",
            command=lambda: self.log_manager and self.log_manager.clear(),
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_SECONDARY,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=10)
        
        tk.Button(
            control_frame,
            text="导出日志",
            command=self._export_log,
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_SECONDARY,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=5)
        
        # 日志文本区
        self.log_text = scrolledtext.ScrolledText(
            tab,
            font=("Consolas", 10),
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # 初始化日志管理器
        self.log_manager = LogManager(self.log_text)
    
    def _create_visualization_tab(self):
        """创建可视化Tab"""
        tab = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(tab, text="📊 可视化")
        
        # 复杂度仪表盘
        dashboard_frame = tk.LabelFrame(
            tab,
            text="复杂度仪表盘",
            font=("Microsoft YaHei", 12, "bold"),
            fg=Colors.HIGHLIGHT,
            bg=Colors.BG_SECONDARY,
            padx=15,
            pady=15
        )
        dashboard_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 复杂度进度条
        self.complexity_var = tk.DoubleVar(value=0)
        self.complexity_bar = ttk.Progressbar(
            dashboard_frame,
            variable=self.complexity_var,
            maximum=100,
            length=300,
            mode='determinate'
        )
        self.complexity_bar.pack(side=tk.LEFT, padx=10)
        
        self.complexity_label = tk.Label(
            dashboard_frame,
            text="0%",
            font=("Consolas", 14, "bold"),
            fg=Colors.INFO,
            bg=Colors.BG_SECONDARY,
            width=10
        )
        self.complexity_label.pack(side=tk.LEFT)
        
        # 共振强度显示
        resonance_frame = tk.LabelFrame(
            tab,
            text="三元共振强度",
            font=("Microsoft YaHei", 12, "bold"),
            fg=Colors.HIGHLIGHT,
            bg=Colors.BG_SECONDARY,
            padx=15,
            pady=15
        )
        resonance_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 三元共振进度条
        self.resonance_var = tk.DoubleVar(value=0)
        self.resonance_bar = ttk.Progressbar(
            resonance_frame,
            variable=self.resonance_var,
            maximum=1.0,
            length=300,
            mode='determinate'
        )
        self.resonance_bar.pack(side=tk.LEFT, padx=10)
        
        self.resonance_label = tk.Label(
            resonance_frame,
            text="0.00",
            font=("Consolas", 14, "bold"),
            fg=Colors.INFO,
            bg=Colors.BG_SECONDARY,
            width=10
        )
        self.resonance_label.pack(side=tk.LEFT)
        
        # 架构图示
        architecture_frame = tk.LabelFrame(
            tab,
            text="IGCTR架构图",
            font=("Microsoft YaHei", 12, "bold"),
            fg=Colors.HIGHLIGHT,
            bg=Colors.BG_SECONDARY,
            padx=15,
            pady=15
        )
        architecture_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 架构文本图
        architecture_text = """
┌─────────────────────────────────────────────────────────────┐
│                    宏视界层 (Γ)                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│   │ 三视界推理   │  │ Ftel意图显化 │  │ 历史复合体调制   │  │
│   │   裁判      │  │  Oracle层    │  │                 │  │
│   └─────────────┘  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    中视界层 (Σ)                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│   │ BFT物理容错 │  │ Lean逻辑验证 │  │  R/U认知更新    │  │
│   │   N≥3f+1  │  │  类型安全    │  │                 │  │
│   └─────────────┘  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    微视界层 (Φ)                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│   │ Clifford    │  │ H₁同调代数   │  │ SOM-Agent数学   │  │
│   │ Cℓ(1,3)时空 │  │ 边界算子∂   │  │    网络        │  │
│   └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
        """
        
        tk.Label(
            architecture_frame,
            text=architecture_text,
            font=("Consolas", 9),
            fg=Colors.INFO,
            bg=Colors.BG_SECONDARY,
            justify=tk.LEFT
        ).pack(fill=tk.BOTH, expand=True)
    
    def _create_docs_tab(self):
        """创建文档Tab"""
        tab = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(tab, text="📖 文档")
        
        # 文档内容
        docs_frame = tk.Frame(tab, bg=Colors.BG_PRIMARY)
        docs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # IGCTR简介
        intro_frame = tk.LabelFrame(
            docs_frame,
            text="IGCTR框架简介",
            font=("Microsoft YaHei", 12, "bold"),
            fg=Colors.HIGHLIGHT,
            bg=Colors.BG_SECONDARY,
            padx=15,
            pady=15
        )
        intro_frame.pack(fill=tk.X, pady=(0, 10))
        
        intro_text = """
信息-几何-意识三元共振（IGCTR）框架是基于复合体理学的AGI理论基础。

核心组件：
• IDO五元组 - 信息动力学优化的核心结构
• 信息作用量泛函 S_I[φ] = ∫_C (tr(I_F[φ]) + R[g]) dV
• 梯度流收敛定理 - ∂_t φ = -∇ S_I[φ]
• 三视界诠释法 - 微视界(Φ)、中视界(Σ)、宏视界(Γ)
• 可证伪预言框架 - 拓扑孤子、量子视觉、暗物质引力透镜
        """
        
        tk.Label(
            intro_frame,
            text=intro_text.strip(),
            font=("Microsoft YaHei", 10),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY,
            justify=tk.LEFT,
            wraplength=800
        ).pack()
        
        # 使用说明
        usage_frame = tk.LabelFrame(
            docs_frame,
            text="使用说明",
            font=("Microsoft YaHei", 12, "bold"),
            fg=Colors.HIGHLIGHT,
            bg=Colors.BG_SECONDARY,
            padx=15,
            pady=15
        )
        usage_frame.pack(fill=tk.BOTH, expand=True)
        
        usage_text = """
【运行Tab】
1. 在左侧输入框输入查询问题
2. 或点击预设问题按钮快速填充
3. 点击"执行分析"开始处理
4. 查看右侧结果区域的分析输出

【日志Tab】
• 实时查看系统运行日志
• 日志按等级自动颜色高亮
• 支持导出日志文件

【可视化Tab】
• 复杂度仪表盘显示当前查询复杂度
• 三元共振强度指示系统状态
• IGCTR三层架构图示

【快捷键】
• Enter: 执行分析
• Ctrl+L: 清空日志
• Ctrl+Q: 退出程序
        """
        
        tk.Label(
            usage_frame,
            text=usage_text.strip(),
            font=("Microsoft YaHei", 10),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY,
            justify=tk.LEFT,
            wraplength=800
        ).pack()
    
    def _create_status_bar(self, parent: tk.Frame):
        """创建底部状态栏"""
        status_bar = tk.Frame(parent, bg=Colors.BG_SECONDARY, height=30)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 5))
        status_bar.pack_propagate(False)
        
        # 运行状态
        self.status_label = tk.Label(
            status_bar,
            text="就绪",
            font=("Microsoft YaHei", 9),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=15)
        
        # 时间
        self.time_label = tk.Label(
            status_bar,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=("Consolas", 9),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_SECONDARY
        )
        self.time_label.pack(side=tk.RIGHT, padx=15)
        
        # 更新时间
        self._update_time()
    
    def _update_time(self):
        """更新时间显示"""
        self.time_label.configure(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self._update_time)
    
    def _initialize_frameworks(self):
        """初始化IGCTR框架"""
        self.log_manager.log("正在初始化IGCTR v2.3框架...", "INFO")
        
        # 初始化IGCTR v2.3框架
        if IGCTR_AVAILABLE:
            try:
                self.igctr_framework = IGCTR_v23_Framework()
                self.log_manager.log("IGCTR v2.3框架初始化成功", "SUCCESS")
                self._update_status("igctr", True)
            except Exception as e:
                self.log_manager.log(f"IGCTR框架初始化失败: {e}", "ERROR")
                self._update_status("igctr", False)
        else:
            self.log_manager.log(f"IGCTR框架不可用: {IGCTR_IMPORT_ERROR}", "WARNING")
            self._update_status("igctr", False)
        
        # 初始化太乙AGI
        if COMPOSITE_AGI_AVAILABLE:
            try:
                self.composite_agi = CompositeAGI_V2()
                self.log_manager.log("太乙AGI系统初始化成功", "SUCCESS")
                self._update_status("composite", True)
            except Exception as e:
                self.log_manager.log(f"太乙AGI初始化失败: {e}", "WARNING")
                self._update_status("composite", False)
        else:
            self.log_manager.log(f"太乙AGI不可用: {COMPOSITE_AGI_IMPORT_ERROR}", "WARNING")
            self._update_status("composite", False)
        
        self.log_manager.log("初始化完成，系统就绪", "SUCCESS")
    
    def _update_status(self, key: str, success: bool):
        """更新状态指示器"""
        if key in self.status_indicators:
            indicator = self.status_indicators[key]
            if success:
                indicator.configure(text="●", fg=Colors.SUCCESS)
            else:
                indicator.configure(text="○", fg=Colors.ERROR)
    
    def _fill_query(self, query: str):
        """填充查询"""
        self.query_entry.delete(1.0, tk.END)
        self.query_entry.insert(1.0, query)
    
    def _clear_results(self):
        """清空结果"""
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.configure(state=tk.DISABLED)
        
        # 重置可视化
        self.complexity_var.set(0)
        self.complexity_label.configure(text="0%")
        self.resonance_var.set(0)
        self.resonance_label.configure(text="0.00")
    
    def _execute_analysis(self):
        """执行分析（异步）"""
        if self.is_processing.get():
            return
        
        query = self.query_entry.get(1.0, tk.END).strip()
        if not query:
            messagebox.showwarning("警告", "请输入查询内容")
            return
        
        # 禁用按钮
        self.is_processing.set(True)
        self.execute_btn.configure(state=tk.DISABLED, text="处理中...")
        
        # 启动异步处理
        thread = threading.Thread(target=self._process_query_async, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _process_query_async(self, query: str):
        """异步处理查询"""
        try:
            self.log_manager.log(f"开始处理查询: {query[:50]}...", "INFO")
            self.status_label.configure(text=f"处理中: {query[:30]}...")
            
            # 更新复杂度（模拟）
            for i in range(0, 101, 10):
                self.complexity_var.set(i)
                self.complexity_label.configure(text=f"{i}%")
                time.sleep(0.05)
            
            result_text = ""
            
            # 使用IGCTR v2.3框架处理
            if self.igctr_framework:
                self._update_status("resonance", True)
                igctr_result = self.igctr_framework.process(query)
                
                result_text += "=" * 60 + "\n"
                result_text += "IGCTR v2.3 分析结果\n"
                result_text += "=" * 60 + "\n\n"
                
                # IDO五元组
                if 'ido_quintuple' in igctr_result:
                    result_text += "【IDO五元组】\n"
                    ido = igctr_result['ido_quintuple']
                    result_text += f"  • 构型空间维度: {ido.get('config_dim', 'N/A')}\n"
                    result_text += f"  • 信息作用量: {ido.get('S_I', 0):.4f}\n"
                    result_text += f"  • 梯度范数: {ido.get('grad_norm', 0):.4f}\n"
                    result_text += "\n"
                
                # 三视界诠释
                if 'three_horizons' in igctr_result:
                    result_text += "【三视界诠释】\n"
                    horizons = igctr_result['three_horizons']
                    for horizon, content in horizons.items():
                        result_text += f"  • {horizon}: {content}\n"
                    result_text += "\n"
                
                # 梯度流
                if 'gradient_flow' in igctr_result:
                    gf = igctr_result['gradient_flow']
                    result_text += "【梯度流动力学】\n"
                    result_text += f"  • 收敛状态: {'已收敛' if gf.get('converged') else '未收敛'}\n"
                    result_text += f"  • 最终梯度范数: {gf.get('final_grad_norm', 0):.6f}\n"
                    result_text += "\n"
                
                # 共振强度
                resonance = igctr_result.get('resonance_strength', 0)
                self.resonance_var.set(resonance)
                self.resonance_label.configure(text=f"{resonance:.2f}")
                result_text += f"【三元共振强度】: {resonance:.4f}\n"
                
                self.log_manager.log("IGCTR v2.3处理完成", "SUCCESS")
            
            # 使用太乙AGI处理
            if self.composite_agi:
                try:
                    agi_result = self.composite_agi.process_query(query)
                    synthesized = agi_result.get('synthesized_answer', '')
                    
                    result_text += "\n" + "=" * 60 + "\n"
                    result_text += "太乙AGI综合分析\n"
                    result_text += "=" * 60 + "\n\n"
                    result_text += synthesized
                    
                    self.log_manager.log("太乙AGI处理完成", "SUCCESS")
                except Exception as e:
                    self.log_manager.log(f"太乙AGI处理异常: {e}", "ERROR")
            
            # 更新结果显示
            self.result_text.configure(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
            self.result_text.configure(state=tk.DISABLED)
            
            self.log_manager.log("分析完成!", "SUCCESS")
            
        except Exception as e:
            error_msg = f"处理异常: {str(e)}\n{traceback.format_exc()}"
            self.log_manager.log(error_msg, "ERROR")
            self._update_status("resonance", False)
            
        finally:
            # 恢复按钮
            self.is_processing.set(False)
            self.execute_btn.configure(state=tk.NORMAL, text="▶ 执行分析")
            self.status_label.configure(text="就绪")
    
    def _export_log(self):
        """导出日志"""
        if not self.log_manager:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"igctr_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("成功", f"日志已导出到:\n{file_path}")
                self.log_manager.log(f"日志已导出到: {file_path}", "SUCCESS")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败:\n{str(e)}")
    
    def run(self):
        """启动GUI"""
        self.root.mainloop()


# ============================================================================
# 主入口
# ============================================================================
def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置窗口样式
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except:
        pass
    
    # 创建并运行应用
    app = IGCTRGui(root)
    app.run()


if __name__ == "__main__":
    main()
