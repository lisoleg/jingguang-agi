# -*- coding: utf-8 -*-
"""
Blueprint: v738 (50+ routes)
M251 -- NAU 结合子引擎 (Non-associative Unity Associator)
  Octonion algebra, Jacobiator, NAU forward, Causal triple rate, Bypass check
  Theorems T2.96-T2.97, Prediction P25
M252 -- JSN 记忆引擎 (Joint Semantic Network)
  Hypergraph memory: nodes, edges, hedges, TDHNN, deep-well, SAT check, coverage
  Theorems T2.98-T2.99
M252b -- Gamma 超图谱引擎 (Gamma HyperGrapher)
  Hypergraph spectral clustering, GNN message passing, gamma functional
  Theorem T2.73, Predictions P20-P21
M253 -- Epiplexity 引擎 (Epiplexity = Entropy + KL + Complexity)
  Shannon entropy, KL divergence, Model complexity, Information bottleneck
  Theorem T2.74, Prediction P21
M254 -- QITE 虚时引擎 (Quantum Imaginary-Time Evolution)
  Wick rotation, QITE evolution, Ground state, Quaternion/Octonion algebra
  Theorems T2.101-T2.102, Prediction P26
M255 -- LSNC 协方差引擎 (Log-Scale Neural Covariance Regulation)
  Covariance matrix, Log-scale regulation, Adaptive alpha, Neural dynamics, Steady state
  Theorem T2.76, Prediction P23
URL prefix: /api/v738
Version: v7.38 五引擎 + Gamma超图谱整合
"""

import math
import random
import shared_state
from flask import Blueprint, request, jsonify

bp = Blueprint('v738', __name__, url_prefix='/api/v738')


# ════════════════════════════════════════════════════
# M251 NAU Associator Engine — NAU结合子引擎
# ════════════════════════════════════════════════════

@bp.route('/nau/octonion_multiply', methods=['POST'])
def api_v738_nau_octonion_multiply():
    """
    八元数乘法 a * b

    POST body:
      a: List[float]  八元数a (8元素)
      b: List[float]  八元数b (8元素)
    """
    try:
        from modules.M251_NAUAssociatorEngine import NAUAssociatorEngine
        data = request.get_json(force=True) or {}
        a = [float(x) for x in data.get('a', [1, 0, 0, 0, 0, 0, 0, 0])]
        b = [float(x) for x in data.get('b', [0, 1, 0, 0, 0, 0, 0, 0])]
        engine = NAUAssociatorEngine.get_instance()
        result = engine.octonion_multiply(a, b)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nau/jacobiator', methods=['POST'])
def api_v738_nau_jacobiator():
    """
    八元数Jacobiator: J(a,b,c) = [a,b,c] + [b,c,a] + [c,a,b]

    POST body:
      a, b, c: List[float]  各8元素八元数
    """
    try:
        from modules.M251_NAUAssociatorEngine import NAUAssociatorEngine
        data = request.get_json(force=True) or {}
        a = [float(x) for x in data.get('a', [1, 0, 0, 0, 0, 0, 0, 0])]
        b = [float(x) for x in data.get('b', [0, 1, 0, 0, 0, 0, 0, 0])]
        c = [float(x) for x in data.get('c', [0, 0, 1, 0, 0, 0, 0, 0])]
        engine = NAUAssociatorEngine.get_instance()
        result = engine.jacobiator(a, b, c)
        return jsonify({'jacobiator': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nau/nau_forward', methods=['POST'])
def api_v738_nau_forward():
    """
    NAU前向计算: NAU(x, w, s)

    POST body:
      x: List[float]       输入向量 (8元素)
      weight: List[float]   权重向量 (8元素)
      scale: List[float]    缩放向量 (可选, 8元素)
    """
    try:
        from modules.M251_NAUAssociatorEngine import NAUAssociatorEngine
        data = request.get_json(force=True) or {}
        x = [float(v) for v in data.get('x', [1] * 8)]
        w = [float(v) for v in data.get('weight', [0.5] * 8)]
        scale = data.get('scale', None)
        if scale is not None:
            scale = [float(v) for v in scale]
        engine = NAUAssociatorEngine.get_instance()
        result = engine.nau_forward(x, w, scale=scale)
        return jsonify({'output': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nau/causal_triple_rate', methods=['POST'])
def api_v738_nau_causal_triple_rate():
    """
    因果三元率: 衡量结合子的非结合程度

    POST body:
      n_samples: int   采样数 (default 100)
      seed: int        随机种子 (default 42)
    """
    try:
        from modules.M251_NAUAssociatorEngine import NAUAssociatorEngine
        data = request.get_json(force=True) or {}
        n_samples = int(data.get('n_samples', 100))
        seed = int(data.get('seed', 42))
        engine = NAUAssociatorEngine.get_instance()
        import random as _rng
        _rng.seed(seed)
        samples = []
        for _ in range(n_samples):
            a = [_rng.gauss(0, 1) for _ in range(8)]
            b = [_rng.gauss(0, 1) for _ in range(8)]
            c = [_rng.gauss(0, 1) for _ in range(8)]
            samples.append((a, b, c))
        rate = engine.causal_triple_rate(samples)
        return jsonify({'causal_triple_rate': rate, 'n_samples': n_samples})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nau/bypass_check', methods=['POST'])
def api_v738_nau_bypass_check():
    """
    Bypass检验: 检查三元组(a,b,c)是否满足bypass条件

    POST body:
      a, b, c: List[float]  各8元素
    """
    try:
        from modules.M251_NAUAssociatorEngine import NAUAssociatorEngine
        data = request.get_json(force=True) or {}
        a = [float(x) for x in data.get('a', [1, 0, 0, 0, 0, 0, 0, 0])]
        b = [float(x) for x in data.get('b', [0, 1, 0, 0, 0, 0, 0, 0])]
        c = [float(x) for x in data.get('c', [0, 0, 1, 0, 0, 0, 0, 0])]
        engine = NAUAssociatorEngine.get_instance()
        result = engine.bypass_check(a, b, c)
        return jsonify({'bypass_satisfied': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nau/verify_theorem_t296', methods=['GET'])
def api_v738_nau_verify_t296():
    """定理T2.96验证: NAU结合子零化定理"""
    try:
        from modules.M251_NAUAssociatorEngine import verify_theorem_t296
        return jsonify(verify_theorem_t296())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nau/verify_theorem_t297', methods=['GET'])
def api_v738_nau_verify_t297():
    """定理T2.97验证: NAU因果三元率下界定理"""
    try:
        from modules.M251_NAUAssociatorEngine import verify_theorem_t297
        return jsonify(verify_theorem_t297())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nau/verify_prediction_p25', methods=['GET'])
def api_v738_nau_verify_p25():
    """预测P25验证: NAU因果三元率预测"""
    try:
        from modules.M251_NAUAssociatorEngine import verify_prediction_p25
        return jsonify(verify_prediction_p25())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/nau/state', methods=['GET'])
def api_v738_nau_state():
    """获取M251引擎状态"""
    try:
        from modules.M251_NAUAssociatorEngine import NAUAssociatorEngine
        engine = NAUAssociatorEngine.get_instance()
        return jsonify(engine.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════
# M252 JSN Memory Engine — JSN记忆引擎
# ════════════════════════════════════════════════════

@bp.route('/jsn/add_node', methods=['POST'])
def api_v738_jsn_add_node():
    """
    添加语义节点

    POST body:
      label: str              节点标签
      embedding: List[float]  节点嵌入 (可选)
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        label = str(data.get('label', 'node'))
        embedding = data.get('embedding', None)
        if embedding is not None:
            embedding = [float(x) for x in embedding]
        engine = JSNMemoryEngine.get_instance()
        node_id = engine.add_node(label=label, embedding=embedding)
        return jsonify({'node_id': node_id, 'label': label})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/add_edge', methods=['POST'])
def api_v738_jsn_add_edge():
    """
    添加语义边

    POST body:
      src: int        源节点ID
      dst: int        目标节点ID
      rel_type: str   关系类型
      weight: float    权重 (default 1.0)
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        src = int(data.get('src', 0))
        dst = int(data.get('dst', 1))
        rel_type = str(data.get('rel_type', 'related'))
        weight = float(data.get('weight', 1.0))
        engine = JSNMemoryEngine.get_instance()
        edge_id = engine.add_edge(src=src, dst=dst, rel_type=rel_type, weight=weight)
        return jsonify({'edge_id': edge_id, 'src': src, 'dst': dst, 'rel_type': rel_type})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/add_hedge', methods=['POST'])
def api_v738_jsn_add_hedge():
    """
    添加超边

    POST body:
      nodes: List[int]  节点ID列表
      rel_type: str      关系类型
      weight: float       权重 (default 1.0)
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        nodes = [int(x) for x in data.get('nodes', [0, 1, 2])]
        rel_type = str(data.get('rel_type', 'hyper'))
        weight = float(data.get('weight', 1.0))
        engine = JSNMemoryEngine.get_instance()
        hedge_id = engine.add_hedge(nodes=nodes, rel_type=rel_type, weight=weight)
        return jsonify({'hedge_id': hedge_id, 'nodes': nodes, 'rel_type': rel_type})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/query_triple', methods=['POST'])
def api_v738_jsn_query_triple():
    """
    三元组查询

    POST body:
      a, b, c: int  节点ID
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        a = int(data.get('a', 0))
        b = int(data.get('b', 1))
        c = int(data.get('c', 2))
        engine = JSNMemoryEngine.get_instance()
        result = engine.query_triple(a, b, c)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/tdhnn_step', methods=['POST'])
def api_v738_jsn_tdhnn_step():
    """执行一步TDHNN动力学更新"""
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        engine = JSNMemoryEngine.get_instance()
        result = engine.tdhnn_step()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/deepwell_add', methods=['POST'])
def api_v738_jsn_deepwell_add():
    """
    添加深井记忆条目

    POST body:
      content: str  记忆内容
      depth: int     深度 (default 1)
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        content = str(data.get('content', 'memory'))
        depth = int(data.get('depth', 1))
        engine = JSNMemoryEngine.get_instance()
        entry_id = engine.deepwell_add(content=content, depth=depth)
        return jsonify({'entry_id': entry_id, 'content': content, 'depth': depth})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/deepwell_access', methods=['POST'])
def api_v738_jsn_deepwell_access():
    """
    访问深井记忆条目

    POST body:
      entry_id: int  条目ID
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        entry_id = int(data.get('entry_id', 0))
        engine = JSNMemoryEngine.get_instance()
        entry = engine.deepwell_access(entry_id=entry_id)
        if entry is None:
            return jsonify({'found': False, 'entry_id': entry_id})
        return jsonify({'found': True, 'entry_id': entry_id, 'content': entry.content, 'depth': entry.depth})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/deepwell_prune', methods=['POST'])
def api_v738_jsn_deepwell_prune():
    """
    深井记忆修剪

    POST body:
      threshold_access: int  访问次数阈值 (default 2)
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        threshold = int(data.get('threshold_access', 2))
        engine = JSNMemoryEngine.get_instance()
        pruned = engine.deepwell_prune(threshold_access=threshold)
        return jsonify({'pruned_count': pruned})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/compute_coverage', methods=['GET'])
def api_v738_jsn_coverage():
    """计算记忆覆盖率"""
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        engine = JSNMemoryEngine.get_instance()
        coverage = engine.compute_coverage()
        return jsonify({'coverage': coverage})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/compute_relational_action', methods=['GET'])
def api_v738_jsn_relational_action():
    """计算关系作用量"""
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        engine = JSNMemoryEngine.get_instance()
        action = engine.compute_relational_action()
        return jsonify({'relational_action': action})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/sat_check', methods=['POST'])
def api_v738_jsn_sat_check():
    """
    SAT可满足性检查

    POST body:
      max_arity: int  最大元数 (default 10)
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        max_arity = int(data.get('max_arity', 10))
        engine = JSNMemoryEngine.get_instance()
        result = engine.sat_check(max_arity=max_arity)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/prune_edges', methods=['POST'])
def api_v738_jsn_prune_edges():
    """
    修剪弱边

    POST body:
      threshold: float  权重阈值 (default 0.1)
    """
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        data = request.get_json(force=True) or {}
        threshold = float(data.get('threshold', 0.1))
        engine = JSNMemoryEngine.get_instance()
        pruned = engine.prune_edges(threshold=threshold)
        return jsonify({'pruned_edges': pruned})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/verify_theorem_t298', methods=['GET'])
def api_v738_jsn_verify_t298():
    """定理T2.98验证: JSN记忆一致性定理"""
    try:
        from modules.M252_JSNMemoryEngine import verify_theorem_t298
        return jsonify(verify_theorem_t298())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/verify_theorem_t299', methods=['GET'])
def api_v738_jsn_verify_t299():
    """定理T2.99验证: JSN记忆可满足性定理"""
    try:
        from modules.M252_JSNMemoryEngine import verify_theorem_t299
        return jsonify(verify_theorem_t299())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jsn/state', methods=['GET'])
def api_v738_jsn_state():
    """获取M252 JSN引擎状态"""
    try:
        from modules.M252_JSNMemoryEngine import JSNMemoryEngine
        engine = JSNMemoryEngine.get_instance()
        return jsonify(engine.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════
# M252b Gamma HyperGrapher Engine — Gamma超图谱引擎
# ════════════════════════════════════════════════════

@bp.route('/gamma/add_vertex', methods=['POST'])
def api_v738_gamma_add_vertex():
    """
    添加超图顶点

    POST body:
      v: int  顶点ID
    """
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        data = request.get_json(force=True) or {}
        v = int(data.get('v', 0))
        engine = GammaHyperGrapherEngine.get_instance()
        engine.add_vertex(v)
        return jsonify({'vertex_added': v})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/gamma/add_hyperedge', methods=['POST'])
def api_v738_gamma_add_hyperedge():
    """
    添加超边

    POST body:
      vertices: List[int]  顶点列表
      weight: float         权重 (default 1.0)
    """
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        data = request.get_json(force=True) or {}
        vertices = [int(x) for x in data.get('vertices', [0, 1, 2])]
        weight = float(data.get('weight', 1.0))
        engine = GammaHyperGrapherEngine.get_instance()
        edge_id = engine.add_hyperedge(vertices=vertices, weight=weight)
        return jsonify({'edge_id': edge_id, 'vertices': vertices, 'weight': weight})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/gamma/spectral_cluster', methods=['POST'])
def api_v738_gamma_spectral_cluster():
    """
    超图谱聚类

    POST body:
      num_clusters: int  聚类数 (default 2)
      n_vertices: int     顶点数 (default 20, 自动生成随机超图)
      seed: int           随机种子 (default 42)
    """
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        import random as _rng
        data = request.get_json(force=True) or {}
        num_clusters = int(data.get('num_clusters', 2))
        n_vertices = int(data.get('n_vertices', 20))
        seed = int(data.get('seed', 42))
        engine = GammaHyperGrapherEngine.get_instance()
        engine.reset()
        _rng.seed(seed)
        # Add vertices
        for v in range(n_vertices):
            engine.add_vertex(v)
        # Add random hyperedges
        for _ in range(n_vertices * 2):
            size = _rng.randint(2, min(5, n_vertices))
            vertices = _rng.sample(range(n_vertices), size)
            engine.add_hyperedge(vertices=vertices, weight=_rng.uniform(0.5, 2.0))
        result = engine.hypergraph_spectral_cluster(num_clusters=num_clusters)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/gamma/message_pass', methods=['POST'])
def api_v738_gamma_message_pass():
    """
    超图GNN消息传递

    POST body:
      num_layers: int  传递层数 (default 3)
      n_vertices: int   顶点数 (default 10)
      feature_dim: int   特征维度 (default 4)
    """
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        import random as _rng
        data = request.get_json(force=True) or {}
        num_layers = int(data.get('num_layers', 3))
        n_vertices = int(data.get('n_vertices', 10))
        feature_dim = int(data.get('feature_dim', 4))
        engine = GammaHyperGrapherEngine.get_instance()
        engine.reset()
        for v in range(n_vertices):
            engine.add_vertex(v)
        for _ in range(n_vertices):
            size = _rng.randint(2, min(4, n_vertices))
            vertices = _rng.sample(range(n_vertices), size)
            engine.add_hyperedge(vertices=vertices)
        H = [[_rng.gauss(0, 1) for _ in range(feature_dim)] for _ in range(n_vertices)]
        result = engine.hypergnn_message_pass(H, num_layers=num_layers)
        return jsonify({'output_shape': [len(result), len(result[0]) if result else 0], 'output': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/gamma/gamma_functional', methods=['POST'])
def api_v738_gamma_functional():
    """
    Gamma泛函计算: gamma(f) = sum_k gamma_k * f^{(k)}

    POST body:
      f: List[float]        输入函数值列表
      coeffs: List[float]   Gamma系数 (可选)
    """
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        data = request.get_json(force=True) or {}
        f = [float(x) for x in data.get('f', [1.0, 2.0, 3.0])]
        coeffs = data.get('coeffs', None)
        if coeffs is not None:
            coeffs = [float(x) for x in coeffs]
        engine = GammaHyperGrapherEngine.get_instance()
        result = engine.gamma_functional(f, coeffs=coeffs)
        return jsonify({'gamma_functional': result, 'input_size': len(f)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/gamma/verify_theorem_t273', methods=['GET'])
def api_v738_gamma_verify_t273():
    """定理T2.73验证: 超图谱聚类收敛性"""
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        engine = GammaHyperGrapherEngine.get_instance()
        return jsonify(engine.verify_theorem_t273())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/gamma/verify_prediction_p20', methods=['GET'])
def api_v738_gamma_verify_p20():
    """预测P20验证: 社区检测准确率 >= 80%"""
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        engine = GammaHyperGrapherEngine.get_instance()
        return jsonify(engine.verify_prediction_p20())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/gamma/verify_prediction_p21', methods=['GET'])
def api_v738_gamma_verify_p21():
    """预测P21验证: 消息传递收敛性"""
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        engine = GammaHyperGrapherEngine.get_instance()
        return jsonify(engine.verify_prediction_p21())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/gamma/state', methods=['GET'])
def api_v738_gamma_state():
    """获取M252 Gamma引擎状态"""
    try:
        from modules.M252_GammaHyperGrapherEngine import GammaHyperGrapherEngine
        engine = GammaHyperGrapherEngine.get_instance()
        return jsonify(engine.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════
# M253 Epiplexity Engine — Epiplexity引擎
# ════════════════════════════════════════════════════

@bp.route('/epiplexity/entropy', methods=['POST'])
def api_v738_epiplexity_entropy():
    """
    Shannon信息熵 H(p) = -sum p_i log p_i

    POST body:
      prob_dist: List[float]  概率分布
    """
    try:
        from modules.M253_EpiplexityEngine import EpiplexityEngine
        data = request.get_json(force=True) or {}
        prob_dist = [float(x) for x in data.get('prob_dist', [0.25, 0.25, 0.25, 0.25])]
        engine = EpiplexityEngine.get_instance()
        result = engine.compute_entropy(prob_dist)
        return jsonify({'entropy': result, 'input_size': len(prob_dist)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/epiplexity/distance', methods=['POST'])
def api_v738_epiplexity_distance():
    """
    KL散度 D_KL(p||q) = sum p_i log(p_i/q_i)

    POST body:
      p: List[float]      分布p
      prior: List[float]   先验分布q
    """
    try:
        from modules.M253_EpiplexityEngine import EpiplexityEngine
        data = request.get_json(force=True) or {}
        p = [float(x) for x in data.get('p', [0.5, 0.5])]
        prior = [float(x) for x in data.get('prior', [0.5, 0.5])]
        engine = EpiplexityEngine.get_instance()
        result = engine.compute_distance(p, prior)
        return jsonify({'kl_divergence': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/epiplexity/complexity', methods=['POST'])
def api_v738_epiplexity_complexity():
    """
    模型复杂度 C(params) = (1-s) * log(1 + n/n_ref)

    POST body:
      model_params: List[float]  模型参数列表
    """
    try:
        from modules.M253_EpiplexityEngine import EpiplexityEngine
        data = request.get_json(force=True) or {}
        params = [float(x) for x in data.get('model_params', [0.1, 0.2, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0])]
        engine = EpiplexityEngine.get_instance()
        result = engine.compute_complexity(params)
        return jsonify({'complexity': result, 'n_params': len(params)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/epiplexity/score', methods=['POST'])
def api_v738_epiplexity_score():
    """
    Epiplexity总分 E(p) = H(p) + D(p) + C(p)

    POST body:
      p: List[float]        分布p
      prior: List[float]     先验分布
      params: List[float]    模型参数
    """
    try:
        from modules.M253_EpiplexityEngine import EpiplexityEngine
        data = request.get_json(force=True) or {}
        p = [float(x) for x in data.get('p', [0.5, 0.5])]
        prior = [float(x) for x in data.get('prior', [0.5, 0.5])]
        params = [float(x) for x in data.get('params', [0.1, 0.2])]
        engine = EpiplexityEngine.get_instance()
        result = engine.epiplexity_score(p, prior, params)
        return jsonify({'epiplexity_score': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/epiplexity/information_bottleneck', methods=['POST'])
def api_v738_epiplexity_ib():
    """
    信息瓶颈权衡 L = I(X;Z) - beta * I(Z;Y)

    POST body:
      I_XZ: float  I(X;Z)
      I_ZY: float  I(Z;Y)
      beta: float   权衡参数
    """
    try:
        from modules.M253_EpiplexityEngine import EpiplexityEngine
        data = request.get_json(force=True) or {}
        I_XZ = float(data.get('I_XZ', 1.0))
        I_ZY = float(data.get('I_ZY', 0.8))
        beta = float(data.get('beta', 1.0))
        engine = EpiplexityEngine.get_instance()
        result = engine.information_bottleneck(I_XZ, I_ZY, beta)
        return jsonify({'ib_score': result, 'I_XZ': I_XZ, 'I_ZY': I_ZY, 'beta': beta})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/epiplexity/verify_theorem_t274', methods=['GET'])
def api_v738_epiplexity_verify_t274():
    """定理T2.74验证: E(p) >= H(p) + D(p) >= H(p)"""
    try:
        from modules.M253_EpiplexityEngine import verify_theorem_t274
        return jsonify(verify_theorem_t274())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/epiplexity/verify_prediction_p21', methods=['GET'])
def api_v738_epiplexity_verify_p21():
    """预测P21验证: 认知负载预测误差 < 15%"""
    try:
        from modules.M253_EpiplexityEngine import verify_prediction_p21
        return jsonify(verify_prediction_p21())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/epiplexity/state', methods=['GET'])
def api_v738_epiplexity_state():
    """获取M253引擎状态"""
    try:
        from modules.M253_EpiplexityEngine import EpiplexityEngine
        engine = EpiplexityEngine.get_instance()
        return jsonify(engine.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════
# M254 QITE Virtual Time Engine — QITE虚时引擎
# ════════════════════════════════════════════════════

@bp.route('/qite/wick_rotate', methods=['POST'])
def api_v738_qite_wick_rotate():
    """
    Wick旋转: t -> -i*tau (Minkowski -> Euclidean)

    POST body:
      tau: float  虚时间参数
    """
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        data = request.get_json(force=True) or {}
        tau = float(data.get('tau', 1.0))
        result = QITEVirtualTimeEngine.wick_rotate(tau)
        return jsonify({'tau': tau, 't_real': result.real if isinstance(result, complex) else result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/inverse_wick_rotate', methods=['POST'])
def api_v738_qite_inv_wick():
    """
    逆Wick旋转: -i*tau -> t (Euclidean -> Minkowski)

    POST body:
      t_real: float  实时间
    """
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        data = request.get_json(force=True) or {}
        t_real = float(data.get('t_real', 1.0))
        result = QITEVirtualTimeEngine.inverse_wick_rotate(t_real)
        return jsonify({'t_real': t_real, 'tau': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/evolve', methods=['POST'])
def api_v738_qite_evolve():
    """
    QITE虚时演化

    POST body:
      initial_state: List[float]       初始量子态
      hamiltonian: List[List[float]]   哈密顿量矩阵
      n_steps: int                      演化步数 (default 10)
    """
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        data = request.get_json(force=True) or {}
        n_steps = int(data.get('n_steps', 10))
        dim = int(data.get('dim', 4))
        # Default: simple 4x4 identity-like Hamiltonian
        initial_state = data.get('initial_state', None)
        hamiltonian = data.get('hamiltonian', None)
        if initial_state is None:
            initial_state = [1.0 / dim] * dim
        else:
            initial_state = [float(x) for x in initial_state]
        if hamiltonian is None:
            # Diagonal Hamiltonian with decreasing eigenvalues
            import random as _rng
            _rng.seed(42)
            hamiltonian = [[0.0] * dim for _ in range(dim)]
            for i in range(dim):
                hamiltonian[i][i] = (dim - i) * 0.5
        else:
            hamiltonian = [[float(x) for x in row] for row in hamiltonian]
        engine = QITEVirtualTimeEngine.get_instance(dim=dim)
        result = engine.qite_evolve(initial_state, hamiltonian, n_steps)
        return jsonify({'final_state': result, 'n_steps': n_steps, 'dim': dim})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/find_ground_state', methods=['POST'])
def api_v738_qite_ground_state():
    """
    寻找基态 (最低能量本征态)

    POST body:
      dim: int                          维度 (default 4)
      hamiltonian: List[List[float]]     哈密顿量矩阵 (可选, 自动生成)
    """
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        data = request.get_json(force=True) or {}
        dim = int(data.get('dim', 4))
        hamiltonian = data.get('hamiltonian', None)
        if hamiltonian is None:
            import random as _rng
            _rng.seed(42)
            hamiltonian = [[0.0] * dim for _ in range(dim)]
            for i in range(dim):
                hamiltonian[i][i] = (dim - i) * 0.5
        else:
            hamiltonian = [[float(x) for x in row] for row in hamiltonian]
        engine = QITEVirtualTimeEngine.get_instance(dim=dim)
        ground_state, energy = engine.find_ground_state(hamiltonian)
        return jsonify({'ground_state': ground_state, 'ground_energy': energy, 'dim': dim})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/quaternion_multiply', methods=['POST'])
def api_v738_qite_quat_mult():
    """
    四元数乘法

    POST body:
      q1: [w,x,y,z]  四元数1
      q2: [w,x,y,z]  四元数2
    """
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        data = request.get_json(force=True) or {}
        q1 = tuple(float(x) for x in data.get('q1', [1, 0, 0, 0]))
        q2 = tuple(float(x) for x in data.get('q2', [0, 1, 0, 0]))
        result = QITEVirtualTimeEngine.quaternion_multiply(q1, q2)
        return jsonify({'result': list(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/octonion_multiply', methods=['POST'])
def api_v738_qite_oct_mult():
    """
    八元数乘法

    POST body:
      a: Tuple[8 floats]  八元数a
      b: Tuple[8 floats]  八元数b
    """
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        data = request.get_json(force=True) or {}
        a = tuple(float(x) for x in data.get('a', [1, 0, 0, 0, 0, 0, 0, 0]))
        b = tuple(float(x) for x in data.get('b', [0, 1, 0, 0, 0, 0, 0, 0]))
        result = QITEVirtualTimeEngine.octonion_multiply(a, b)
        return jsonify({'result': list(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/octonion_jacobiator', methods=['POST'])
def api_v738_qite_oct_jacobiator():
    """
    八元数Jacobiator

    POST body:
      a, b, c: Tuple[8 floats]
    """
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        data = request.get_json(force=True) or {}
        a = tuple(float(x) for x in data.get('a', [1, 0, 0, 0, 0, 0, 0, 0]))
        b = tuple(float(x) for x in data.get('b', [0, 1, 0, 0, 0, 0, 0, 0]))
        c = tuple(float(x) for x in data.get('c', [0, 0, 1, 0, 0, 0, 0, 0]))
        engine = QITEVirtualTimeEngine.get_instance()
        result = engine.octonion_jacobiator(a, b, c)
        return jsonify({'jacobiator': list(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/octonion_reasoning', methods=['POST'])
def api_v738_qite_oct_reasoning():
    """
    八元数推理

    POST body:
      a, b, c: Tuple[8 floats]
    """
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        data = request.get_json(force=True) or {}
        a = tuple(float(x) for x in data.get('a', [1, 0, 0, 0, 0, 0, 0, 0]))
        b = tuple(float(x) for x in data.get('b', [0, 1, 0, 0, 0, 0, 0, 0]))
        c = tuple(float(x) for x in data.get('c', [0, 0, 1, 0, 0, 0, 0, 0]))
        engine = QITEVirtualTimeEngine.get_instance()
        result = engine.octonion_reasoning(a, b, c)
        return jsonify({'reasoning_result': list(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/verify_theorem_t2101', methods=['GET'])
def api_v738_qite_verify_t2101():
    """定理T2.101验证: QITE收敛性定理"""
    try:
        from modules.M254_QITEVirtualTimeEngine import verify_theorem_t2101
        return jsonify({'theorem': 'T2.101', 'proved': verify_theorem_t2101()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/verify_theorem_t2102', methods=['GET'])
def api_v738_qite_verify_t2102():
    """定理T2.102验证: QITE基态存在性定理"""
    try:
        from modules.M254_QITEVirtualTimeEngine import verify_theorem_t2102
        return jsonify({'theorem': 'T2.102', 'proved': verify_theorem_t2102()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/verify_prediction_p26', methods=['GET'])
def api_v738_qite_verify_p26():
    """预测P26验证: QITE基态精度预测"""
    try:
        from modules.M254_QITEVirtualTimeEngine import verify_prediction_p26
        return jsonify({'prediction': 'P26', 'passed': verify_prediction_p26()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/qite/state', methods=['GET'])
def api_v738_qite_state():
    """获取M254引擎状态"""
    try:
        from modules.M254_QITEVirtualTimeEngine import QITEVirtualTimeEngine
        engine = QITEVirtualTimeEngine.get_instance()
        return jsonify(engine.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════
# M255 LSNC Regulation Engine — LSNC协方差引擎
# ════════════════════════════════════════════════════

@bp.route('/lsnc/covariance', methods=['POST'])
def api_v738_lsnc_covariance():
    """
    计算样本协方差矩阵

    POST body:
      X: List[List[float]]  样本矩阵 (n_samples x n_features)
    """
    try:
        from modules.M255_LSNCREngine import LSNCREngine
        data = request.get_json(force=True) or {}
        X = data.get('X', None)
        if X is None:
            # Default: 5x5 identity-like
            import random as _rng
            _rng.seed(42)
            X = [[_rng.gauss(0, 1) for _ in range(5)] for _ in range(10)]
        else:
            X = [[float(x) for x in row] for row in X]
        engine = LSNCREngine.get_instance()
        result = engine.compute_covariance(X)
        return jsonify({'covariance': result, 'shape': [len(result), len(result[0]) if result else 0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lsnc/log_scale_regulate', methods=['POST'])
def api_v738_lsnc_log_scale():
    """
    对数尺度调节 C_log = log(I + alpha * C)

    POST body:
      C: List[List[float]]  协方差矩阵
      alpha: float            调节参数 (default 0.1)
    """
    try:
        from modules.M255_LSNCREngine import LSNCREngine
        data = request.get_json(force=True) or {}
        alpha = float(data.get('alpha', 0.1))
        C = data.get('C', None)
        if C is None:
            # Default: 3x3 identity
            C = [[1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]
        else:
            C = [[float(x) for x in row] for row in C]
        engine = LSNCREngine.get_instance()
        result = engine.log_scale_regulate(C, alpha)
        return jsonify({'C_log': result, 'alpha': alpha, 'shape': [len(result), len(result[0]) if result else 0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lsnc/adaptive_alpha', methods=['POST'])
def api_v738_lsnc_adaptive_alpha():
    """
    自适应alpha: alpha = eta / (||C||_F + eps)

    POST body:
      C: List[List[float]]  协方差矩阵
      eta: float              学习率 (可选)
      eps: float              稳定常数 (可选)
    """
    try:
        from modules.M255_LSNCREngine import LSNCREngine
        data = request.get_json(force=True) or {}
        C = data.get('C', [[1.0, 0.5], [0.5, 2.0]])
        C = [[float(x) for x in row] for row in C]
        eta = data.get('eta', None)
        eps = data.get('eps', None)
        engine = LSNCREngine.get_instance()
        alpha = engine.adaptive_alpha(C, eta=eta, eps=eps)
        return jsonify({'adaptive_alpha': alpha})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lsnc/neural_dynamics', methods=['POST'])
def api_v738_lsnc_neural_dynamics():
    """
    神经动力学 ODE积分 (Euler-Maruyama)

    POST body:
      W: List[List[float]]  权重矩阵
      x0: List[float]       初始状态
      tau: float              时间常数 (default 1.0)
      T: float                总时间 (default 5.0)
      dt: float               时间步长 (default 0.01)
      noise_std: float        噪声标准差 (default 0.01)
    """
    try:
        from modules.M255_LSNCREngine import LSNCREngine
        data = request.get_json(force=True) or {}
        dim = int(data.get('dim', 3))
        tau = float(data.get('tau', 1.0))
        T = float(data.get('T', 5.0))
        dt = float(data.get('dt', 0.01))
        noise_std = float(data.get('noise_std', 0.01))
        W = data.get('W', None)
        if W is None:
            import random as _rng
            _rng.seed(42)
            W = [[_rng.gauss(0, 0.3) for _ in range(dim)] for _ in range(dim)]
            # Make diagonals negative for stability
            for i in range(dim):
                W[i][i] = -1.0
        else:
            W = [[float(x) for x in row] for row in W]
        x0 = data.get('x0', None)
        if x0 is None:
            x0 = [1.0 / dim] * dim
        else:
            x0 = [float(x) for x in x0]
        engine = LSNCREngine.get_instance()
        # Default activation: identity
        f = lambda x: x
        trajectory, times = engine.neural_dynamics(W, f, x0, tau, T, dt=dt, noise_std=noise_std, seed=42)
        return jsonify({
            'trajectory_length': len(trajectory),
            'times_length': len(times),
            'final_state': trajectory[-1] if trajectory else [],
            'T': T,
            'dt': dt,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lsnc/covariance_steady_state', methods=['POST'])
def api_v738_lsnc_steady_state():
    """
    协方差平稳状态检测

    POST body:
      dim: int    维度 (default 3)
      tau: float    时间常数 (default 1.0)
      T_max: float  最大模拟时间 (default 20.0)
    """
    try:
        from modules.M255_LSNCREngine import LSNCREngine
        data = request.get_json(force=True) or {}
        dim = int(data.get('dim', 3))
        tau = float(data.get('tau', 1.0))
        T_max = float(data.get('T_max', 20.0))
        import random as _rng
        _rng.seed(42)
        W = [[_rng.gauss(0, 0.3) for _ in range(dim)] for _ in range(dim)]
        for i in range(dim):
            W[i][i] = -1.0
        f = lambda x: x
        engine = LSNCREngine.get_instance()
        result = engine.covariance_steady_state(W, f, tau, T_max, seed=42)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lsnc/verify_theorem_t276', methods=['GET'])
def api_v738_lsnc_verify_t276():
    """定理T2.76验证: 协方差调节收敛性"""
    try:
        from modules.M255_LSNCREngine import LSNCREngine
        engine = LSNCREngine.get_instance()
        return jsonify(engine.verify_theorem_t276())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lsnc/verify_prediction_p23', methods=['GET'])
def api_v738_lsnc_verify_p23():
    """预测P23验证: 平稳状态检测准确率 >= 80%"""
    try:
        from modules.M255_LSNCREngine import LSNCREngine
        engine = LSNCREngine.get_instance()
        return jsonify(engine.verify_prediction_p23())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/lsnc/state', methods=['GET'])
def api_v738_lsnc_state():
    """获取M255引擎状态"""
    try:
        from modules.M255_LSNCREngine import LSNCREngine
        engine = LSNCREngine.get_instance()
        return jsonify(engine.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════
# v738 Health Check
# ════════════════════════════════════════════════════

@bp.route('/health', methods=['GET'])
def api_v738_health():
    """v7.38 health check - all 6 modules"""
    import importlib
    results = {}
    module_map = {
        'M251_NAUAssociatorEngine': 'M251',
        'M252_JSNMemoryEngine': 'M252',
        'M252_GammaHyperGrapherEngine': 'M252b',
        'M253_EpiplexityEngine': 'M253',
        'M254_QITEVirtualTimeEngine': 'M254',
        'M255_LSNCREngine': 'M255',
    }
    for mod_path, short in module_map.items():
        try:
            importlib.import_module(f'modules.{mod_path}')
            results[short] = 'OK'
        except Exception as ex:
            results[short] = f'ERROR: {ex}'
    all_ok = all(v == 'OK' for v in results.values())
    return jsonify({
        'version': 'v7.38',
        'status': 'healthy' if all_ok else 'degraded',
        'modules': results,
        'integration': 'nau-jsn-gamma-epiplexity-qite-lsnc'
    }), 200 if all_ok else 207
