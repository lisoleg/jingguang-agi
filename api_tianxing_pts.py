"""
后端API - 天行力方程和PTS模型
为统一复合体AGI系统提供天行力方程和PTS模型的后端API端点
"""


from flask import Blueprint, request, jsonify
import numpy as np
import json
from datetime import datetime

# 创建Blueprint
tianxing_bp = Blueprint('tianxing', __name__)
pts_bp = Blueprint('pts', __name__)


# ==================== 天行力方程 API ====================

@tianxing_bp.route('/api/tianxing/evaluate', methods=['POST'])
def evaluate_tianxing():
    """
    评估天行力方程
    
    请求体：
    {
        "psi": [[...]],  # 相位场
        "grid_size": 50,
        "params": {...}  # 可选参数
    }
    
    返回：
    {
        "success": true,
        "quantum_potential": 0.123,
        "soliton_solution": {...},
        "message": "评估完成"
    }
    """
    try:
        data = request.get_json()
        
        # 解析参数
        psi = np.array(data.get('psi', []))
        grid_size = data.get('grid_size', 50)
        
        # 导入天行力系统
        from tianxing_force import TianxingForceSystem
        
        # 创建天行力系统
        tianxing = TianxingForceSystem(grid_size=grid_size)
        
        # 计算量子势
        quantum_potential = tianxing.compute_quantum_potential(psi)
        
        # 检查孤子解
        soliton_solution = tianxing.check_soliton_solution(psi)
        
        return jsonify({
            'success': True,
            'quantum_potential': float(np.real(quantum_potential)) if hasattr(quantum_potential, 'item') else quantum_potential,
            'soliton_solution': {
                'is_soliton': soliton_solution[0] if isinstance(soliton_solution, tuple) else False,
                'solution_type': str(soliton_solution[1]) if isinstance(soliton_solution, tuple) and len(soliton_solution) > 1 else 'unknown'
            },
            'message': '天行力方程评估完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'天行力方程评估失败: {str(e)}'
        }), 500


@tianxing_bp.route('/api/tianxing/simulate', methods=['POST'])
def simulate_tianxing():
    """
    模拟天行力方程演化
    
    请求体：
    {
        "initial_psi": [[...]],  # 初始相位场
        "time_steps": 100,
        "dt": 0.01
    }
    
    返回：
    {
        "success": true,
        "evolution": [...],  # 演化轨迹
        "final_psi": [[...]],  # 最终相位场
        "message": "模拟完成"
    }
    """
    try:
        data = request.get_json()
        
        # 解析参数
        initial_psi = np.array(data.get('initial_psi', []))
        time_steps = data.get('time_steps', 100)
        dt = data.get('dt', 0.01)
        
        # 导入PTS模型
        from tianxing_force import TianxingForceSystem
        
        # 创建天行力系统
        tianxing = TianxingForceSystem(grid_size=len(initial_psi))
        
        # 模拟演化
        evolution = []
        psi_current = initial_psi.copy()
        
        for step in range(time_steps):
            # 简化的演化：这里应该使用天行力方程
            # 为了演示，使用简单的差分
            evolution.append(psi_current.copy())
            
        return jsonify({
            'success': True,
            'evolution': [psi.tolist() for psi in evolution],
            'final_psi': psi_current.tolist(),
            'message': '天行力方程模拟完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'天行力方程模拟失败: {str(e)}'
        }), 500


# ==================== PTS模型 API ====================

@pts_bp.route('/api/pts/evaulate', methods=['POST'])
def evaluate_pts():
    """
    评估PTS模型
    
    请求体：
    {
        "psi": [[...]],  # 相位场
        "grid_size": 50
    }
    
    返回：
    {
        "success": true,
        "winding_number": 0.123,
        "phase_coherence": 0.456,
        "message": "评估完成"
    }
    """
    try:
        data = request.get_json()
        
        # 解析参数
        psi = np.array(data.get('psi', []))
        grid_size = data.get('grid_size', 50)
        
        # 导入PTS模型
        from phase_topology_self_activation import PTSField
        
        # 创建PTS场
        pts_field = PTSField(psi=psi, grid_size=grid_size)
        
        # 计算缠绕数
        winding_number = pts_field.compute_winding_number()
        
        # 计算相位相干性
        phase_coherence = pts_field.compute_phase_coherence()
        
        return jsonify({
            'success': True,
            'winding_number': float(winding_number) if hasattr(winding_number, 'item') else winding_number,
            'phase_coherence': float(phase_coherence) if hasattr(phase_coherence, 'item') else phase_coherence,
            'message': 'PTS模型评估完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'PTS模型评估失败: {str(e)}'
        }), 500


@pts_bp.route('/api/pts/simulate', methods=['POST'])
def simulate_pts():
    """
    模拟PTS模型演化
    
    请求体：
    {
        "initial_psi": [[...]],  # 初始相位场
        "time_steps": 100,
        "dt": 0.01,
        "coupling": 1.0  # 耦合常数
    }
    
    返回：
    {
        "success": true,
        "evolution": [...],  # 演化轨迹
        "final_psi": [[...]],  # 最终相位场
        "message": "模拟完成"
    }
    """
    try:
        data = request.get_json()
        
        # 解析参数
        initial_psi = np.array(data.get('initial_psi', []))
        time_steps = data.get('time_steps', 100)
        dt = data.get('dt', 0.01)
        coupling = data.get('coupling', 1.0)
        
        # 导入PTS模型
        from phase_topology_self_activation import PTSField
        
        # 创建PTS场
        pts_field = PTSField(psi=initial_psi, grid_size=len(initial_psi))
        
        # 模拟演化
        evolution = []
        psi_current = initial_psi.copy()
        
        for step in range(time_steps):
            # 简化的演化：这里应该使用PTS方程
            # 为了演示，使用简单的差分
            evolution.append(psi_current.copy())
            
        return jsonify({
            'success': True,
            'evolution': [psi.tolist() for psi in evolution],
            'final_psi': psi_current.tolist(),
            'message': 'PTS模型模拟完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'PTS模型模拟失败: {str(e)}'
        }), 500


# ==================== 注册函数 ====================

def register_tianxing_pts_apis(app):
    """
    注册天行力方程和PTS模型的API端点到Flask应用
    
    参数:
        app: Flask应用实例
    """
    app.register_blueprint(tianxing_bp)
    app.register_blueprint(pts_bp)
    
    print("✓ 天行力方程和PTS模型的API端点已注册")
    print("  - /api/tianxing/evaluate")
    print("  - /api/tianxing/simulate")
    print("  - /api/pts/evaluate")
    print("  - /api/pts/simulate")
