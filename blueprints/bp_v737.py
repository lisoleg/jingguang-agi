# -*- coding: utf-8 -*-
"""
Blueprint: v737 (22+ routes)
M250 -- StableWorldModel Engine
  World Model State Transition Prediction (f_θ: (s_t, a_t) -> s_{t+1})
  CEM Cross-Entropy Method Planner
  MPC Model-Predictive Control Controller
  OOD Out-of-Distribution Generalization Evaluator
  Composite Physics Prior Integration (Liu + EML)
  Standardized Environment Suite (PushT/DMControl/OGBench/Two-Room/etc.)
  Theorems T2.90-T2.95, Predictions P23-P24
URL prefix: /api/v737
Version: v7.37 stable-worldmodel integration
"""

import math
import random
import shared_state
from flask import Blueprint, request, jsonify

bp = Blueprint('v737', __name__, url_prefix='/api/v737')


# ====================================================
# M250 StableWorldModel Engine
# ====================================================

@bp.route('/m250/state', methods=['GET'])
def api_v737_m250_state():
    """Get M250 stable world model engine state"""
    try:
        from modules.M250_StableWorldModelEngine import get_state
        return jsonify(get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/verify_theorem', methods=['GET', 'POST'])
def api_v737_m250_verify_theorem():
    """Verify M250 theorems (T2.90-T2.95). GET=all, POST=specific theorem_id"""
    try:
        from modules.M250_StableWorldModelEngine import (
            verify_theorem_t290, verify_theorem_t291, verify_theorem_t292,
            verify_theorem_t293, verify_theorem_t294, verify_theorem_t295
        )
        theorem_id = None
        if request.method == 'POST':
            data = request.get_json(force=True) or {}
            theorem_id = data.get('theorem_id', None)
        if theorem_id:
            verifiers = {
                'T2.90': verify_theorem_t290,
                'T2.91': verify_theorem_t291,
                'T2.92': verify_theorem_t292,
                'T2.93': verify_theorem_t293,
                'T2.94': verify_theorem_t294,
                'T2.95': verify_theorem_t295,
            }
            fn = verifiers.get(theorem_id)
            if fn is None:
                return jsonify({'error': f'Unknown theorem: {theorem_id}', 'theorem': theorem_id, 'proved': False}), 400
            result = fn()
            result['theorem'] = theorem_id
            return jsonify(result)
        else:
            t290 = verify_theorem_t290()
            t291 = verify_theorem_t291()
            t292 = verify_theorem_t292()
            t293 = verify_theorem_t293()
            t294 = verify_theorem_t294()
            t295 = verify_theorem_t295()
            theorems = [t290, t291, t292, t293, t294, t295]
            return jsonify({
                'module': 'M250',
                'theorems': theorems,
                'all_proved': all(t.get('proved', False) for t in theorems)
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/verify_prediction', methods=['GET', 'POST'])
def api_v737_m250_verify_prediction():
    """Verify M250 predictions (P23, P24). GET=all, POST=specific prediction_id"""
    try:
        from modules.M250_StableWorldModelEngine import (
            verify_prediction_p23, verify_prediction_p24
        )
        prediction_id = None
        if request.method == 'POST':
            data = request.get_json(force=True) or {}
            prediction_id = data.get('prediction_id', None)
        if prediction_id:
            verifiers = {
                'P23': verify_prediction_p23,
                'P24': verify_prediction_p24,
            }
            fn = verifiers.get(prediction_id)
            if fn is None:
                return jsonify({'error': f'Unknown prediction: {prediction_id}', 'prediction': prediction_id, 'passed': False}), 400
            result = fn()
            result['prediction'] = prediction_id
            return jsonify(result)
        else:
            p23 = verify_prediction_p23()
            p24 = verify_prediction_p24()
            return jsonify({
                'module': 'M250',
                'predictions': [p23, p24],
                'all_passed': all(p.get('passed', False) for p in [p23, p24])
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/predict', methods=['POST'])
def api_v737_m250_predict():
    """Predict next state using world model"""
    try:
        from modules.M250_StableWorldModelEngine import (
            WorldModelTransition, WorldState, Action
        )
        import numpy as np
        data = request.get_json(force=True) or {}
        state = data.get('state', [0.0, 0.0, 0.0, 0.0])
        action = data.get('action', [0.0, 0.0])
        use_composite = bool(data.get('use_composite_prior', True))

        model = WorldModelTransition(
            state_dim=len(state), action_dim=len(action),
            use_composite_prior=use_composite
        )
        s = WorldState(state_vector=state)
        a = Action(action_vector=action)
        s_next = model.predict(s, a)
        return jsonify({
            'input_state': state,
            'input_action': action,
            'predicted_next_state': s_next.state_vector.tolist(),
            'use_composite_prior': use_composite
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/create_model', methods=['POST'])
def api_v737_m250_create_model():
    """Create a new world model instance"""
    try:
        from modules.M250_StableWorldModelEngine import StableWorldModelEngine
        data = request.get_json(force=True) or {}
        model_id = data.get('model_id', 'default')
        state_dim = int(data.get('state_dim', 4))
        action_dim = int(data.get('action_dim', 2))
        use_composite = bool(data.get('use_composite_prior', False))
        engine = StableWorldModelEngine.get_instance()
        model = engine.create_world_model(model_id, state_dim, action_dim, use_composite)
        return jsonify({
            'model_id': model_id,
            'state_dim': state_dim,
            'action_dim': action_dim,
            'use_composite_prior': use_composite,
            'status': 'created'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/create_planner', methods=['POST'])
def api_v737_m250_create_planner():
    """Create a CEM planner instance"""
    try:
        from modules.M250_StableWorldModelEngine import StableWorldModelEngine
        data = request.get_json(force=True) or {}
        planner_id = data.get('planner_id', 'default')
        action_dim = int(data.get('action_dim', 2))
        horizon = int(data.get('horizon', 10))
        engine = StableWorldModelEngine.get_instance()
        planner = engine.create_planner(planner_id, action_dim, horizon)
        return jsonify({
            'planner_id': planner_id,
            'action_dim': action_dim,
            'horizon': horizon,
            'status': 'created'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ====================================================
# CEM Planner Routes
# ====================================================

@bp.route('/m250/cem_state', methods=['GET'])
def api_v737_m250_cem_state():
    """Get CEM planner state"""
    try:
        from modules.M250_StableWorldModelEngine import StableWorldModelEngine
        engine = StableWorldModelEngine.get_instance()
        state = engine.get_state()
        return jsonify({
            'module': 'M250',
            'component': 'CEMPlanner',
            'planners': state.get('planners', {}),
            'status': 'ready'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/cem_plan', methods=['POST'])
def api_v737_m250_cem_plan():
    """Run CEM planning to find optimal action sequence"""
    try:
        from modules.M250_StableWorldModelEngine import (
            CEMPlanner, WorldModelTransition, WorldState
        )
        import numpy as np
        data = request.get_json(force=True) or {}
        state_dim = int(data.get('state_dim', 4))
        action_dim = int(data.get('action_dim', 2))
        horizon = int(data.get('horizon', 5))
        n_iterations = int(data.get('n_iterations', 5))
        target = data.get('target', [0.0] * state_dim)
        initial = data.get('initial', [1.0] * state_dim)
        use_composite = bool(data.get('use_composite_prior', True))

        model = WorldModelTransition(
            state_dim=state_dim, action_dim=action_dim,
            use_composite_prior=use_composite
        )
        planner = CEMPlanner(
            action_dim=action_dim, horizon=horizon,
            n_iterations=n_iterations
        )
        target_arr = np.array(target, dtype=np.float32)
        init_state = WorldState(state_vector=initial)

        def cost_fn(s, a):
            return float(np.sum((s.state_vector - target_arr) ** 2))

        planned = planner.plan(init_state, model, cost_fn)
        return jsonify({
            'planned_actions': planned.astype(float).tolist(),
            'horizon': horizon,
            'action_dim': action_dim,
            'n_iterations': n_iterations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ====================================================
# MPC Controller Routes
# ====================================================

@bp.route('/m250/mpc_state', methods=['GET'])
def api_v737_m250_mpc_state():
    """Get MPC controller state"""
    try:
        from modules.M250_StableWorldModelEngine import StableWorldModelEngine
        engine = StableWorldModelEngine.get_instance()
        state = engine.get_state()
        return jsonify({
            'module': 'M250',
            'component': 'MPCController',
            'controllers': state.get('controllers', {}),
            'status': 'ready'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/mpc_control', methods=['POST'])
def api_v737_m250_mpc_control():
    """Run MPC control episode"""
    try:
        from modules.M250_StableWorldModelEngine import (
            WorldModelTransition, CEMPlanner, MPCController, WorldState
        )
        import numpy as np
        data = request.get_json(force=True) or {}
        state_dim = int(data.get('state_dim', 4))
        action_dim = int(data.get('action_dim', 2))
        n_steps = int(data.get('n_steps', 20))
        target = data.get('target', [0.0] * state_dim)
        initial = data.get('initial', [1.0] * state_dim)
        use_composite = bool(data.get('use_composite_prior', True))

        model = WorldModelTransition(
            state_dim=state_dim, action_dim=action_dim,
            use_composite_prior=use_composite
        )
        planner = CEMPlanner(action_dim=action_dim, horizon=5, n_iterations=3)
        controller = MPCController(world_model=model, planner=planner)

        init_state = WorldState(state_vector=initial)
        target_arr = np.array(target, dtype=np.float64)
        trajectory = controller.run_episode(init_state, target_arr, n_steps=n_steps)

        final_state = trajectory.transitions[-1].next_state.state_vector
        final_dist = float(np.linalg.norm(final_state - target_arr))
        return jsonify({
            'n_steps': n_steps,
            'total_reward': float(trajectory.total_reward),
            'final_state': final_state.tolist(),
            'target_state': target,
            'final_distance': final_dist
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/mpc_episode', methods=['POST'])
def api_v737_m250_mpc_episode():
    """Run MPC control episode (alias for mpc_control, used by frontend)"""
    return api_v737_m250_mpc_control()


# ====================================================
# OOD Evaluator Routes
# ====================================================

@bp.route('/m250/ood_state', methods=['GET'])
def api_v737_m250_ood_state():
    """Get OOD evaluator state"""
    try:
        from modules.M250_StableWorldModelEngine import StableWorldModelEngine
        engine = StableWorldModelEngine.get_instance()
        state = engine.get_state()
        return jsonify({
            'module': 'M250',
            'component': 'OODEvaluator',
            'evaluators': state.get('evaluators', {}),
            'status': 'ready'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/ood_evaluate', methods=['POST'])
def api_v737_m250_ood_evaluate():
    """Evaluate OOD generalization of a world model"""
    try:
        from modules.M250_StableWorldModelEngine import (
            WorldModelTransition, OODEvaluator, verify_theorem_t293
        )
        data = request.get_json(force=True) or {}
        state_dim = int(data.get('state_dim', 4))
        action_dim = int(data.get('action_dim', 2))

        # Use verify_theorem_t293 which handles dataset generation internally
        result = verify_theorem_t293()
        return jsonify({
            'module': 'M250',
            'ood_evaluation': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ====================================================
# Environment & Physics Prior Routes
# ====================================================

@bp.route('/m250/env_state', methods=['GET'])
def api_v737_m250_env_state():
    """Get environment suite state"""
    try:
        from modules.M250_StableWorldModelEngine import StableWorldModelEngine
        engine = StableWorldModelEngine.get_instance()
        state = engine.get_state()
        return jsonify({
            'module': 'M250',
            'component': 'EnvironmentSuite',
            'environments': state.get('environments', []),
            'status': 'ready'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/list_environments', methods=['GET'])
def api_v737_m250_list_environments():
    """List supported standardized environments (alias used by frontend)"""
    return api_v737_m250_environments()


@bp.route('/m250/environments', methods=['GET'])
def api_v737_m250_environments():
    """List supported standardized environments"""
    envs = [
        {'id': 'pusht', 'name': 'PushT', 'description': 'Push-T shape manipulation task'},
        {'id': 'dmcontrol', 'name': 'DeepMind Control Suite', 'description': 'Continuous control locomotion'},
        {'id': 'ogbench', 'name': 'OGBench', 'description': 'Offline goal-conditioned benchmark'},
        {'id': 'tworoom', 'name': 'Two-Room', 'description': 'Navigation in two-room grid world'},
        {'id': 'gymrobotics', 'name': 'Gymnasium Robotics', 'description': 'Robotic manipulation tasks'},
        {'id': 'craftax', 'name': 'Craftax', 'description': 'Procedural crafting survival'},
        {'id': 'ale', 'name': 'ALE (Atari)', 'description': 'Atari Learning Environment'},
    ]
    return jsonify({
        'environments': envs,
        'count': len(envs),
        'source': 'stable-worldmodel'
    })


# ====================================================
# Individual Theorem/Prediction Routes (URL-param style)
# ====================================================

@bp.route('/m250/theorem/<theorem_id>', methods=['GET'])
def api_v737_m250_theorem(theorem_id):
    """Verify a specific M250 theorem by ID (T2.90-T2.95)"""
    try:
        from modules.M250_StableWorldModelEngine import StableWorldModelEngine
        engine = StableWorldModelEngine.get_instance()
        result = engine.verify_theorem(theorem_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/prediction/<prediction_id>', methods=['GET'])
def api_v737_m250_prediction(prediction_id):
    """Verify a specific M250 prediction by ID (P23, P24)"""
    try:
        from modules.M250_StableWorldModelEngine import StableWorldModelEngine
        engine = StableWorldModelEngine.get_instance()
        result = engine.verify_prediction(prediction_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ====================================================
# Utility API Routes
# ====================================================

@bp.route('/m250/prediction_error', methods=['POST'])
def api_v737_m250_prediction_error():
    """Compute prediction error between predicted and true next states"""
    try:
        from modules.M250_StableWorldModelEngine import compute_prediction_error
        import numpy as np
        data = request.get_json(force=True) or {}
        pred = data.get('predicted', [0.0, 0.0, 0.0, 0.0])
        true = data.get('true', [0.0, 0.0, 0.0, 0.0])
        metric = data.get('metric', 'mse')
        error = compute_prediction_error(np.array(pred), np.array(true), metric)
        return jsonify({
            'predicted': pred,
            'true': true,
            'metric': metric,
            'error': error
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/information_capacity', methods=['POST'])
def api_v737_m250_information_capacity():
    """Compute information-theoretic world model capacity bound"""
    try:
        from modules.M250_StableWorldModelEngine import compute_information_capacity
        data = request.get_json(force=True) or {}
        state_dim = int(data.get('state_dim', 4))
        action_dim = int(data.get('action_dim', 2))
        n_parameters = int(data.get('n_parameters', 1000))
        capacity = compute_information_capacity(state_dim, action_dim, 64, n_parameters)
        import math
        lower_bound = math.log2(max(1, n_parameters))
        return jsonify({
            'state_dim': state_dim,
            'action_dim': action_dim,
            'n_parameters': n_parameters,
            'capacity_bits': capacity,
            'lower_bound_bits': lower_bound,
            'bound_satisfied': capacity >= lower_bound
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/m250/wasserstein', methods=['POST'])
def api_v737_m250_wasserstein():
    """Compute approximate Wasserstein distance between two distributions"""
    try:
        from modules.M250_StableWorldModelEngine import compute_wasserstein_distance
        import numpy as np
        data = request.get_json(force=True) or {}
        samples_p = data.get('samples_p', [[0.0, 0.0], [1.0, 1.0]])
        samples_q = data.get('samples_q', [[0.5, 0.5], [1.5, 1.5]])
        p_order = int(data.get('p', 2))
        w_dist = compute_wasserstein_distance(
            np.array(samples_p), np.array(samples_q), p=p_order
        )
        return jsonify({
            'wasserstein_distance': w_dist,
            'order': p_order
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ====================================================
# v737 Health Check
# ====================================================

@bp.route('/health', methods=['GET'])
def api_v737_health():
    """v7.37 health check - M250 module"""
    import importlib
    results = {}
    try:
        importlib.import_module('modules.M250_StableWorldModelEngine')
        results['M250'] = 'OK'
    except Exception as ex:
        results['M250'] = f'ERROR: {ex}'
    all_ok = all(v == 'OK' for v in results.values())
    return jsonify({
        'version': 'v7.37',
        'status': 'healthy' if all_ok else 'degraded',
        'modules': results,
        'integration': 'stable-worldmodel'
    }), 200 if all_ok else 207
