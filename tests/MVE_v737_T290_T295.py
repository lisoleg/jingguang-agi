#!/usr/bin/env python3
"""
MVE_v737_T290_T295.py -- v7.37 Minimum Viable Experiment
Tests T2.90-T2.95 for M250 StableWorldModelEngine
(World Model State Transition Prediction, CEM Planner, MPC Controller,
 OOD Generalization, Standardized Environments)
"""
import sys, os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def test_m250_engine():
    """Test M250 StableWorldModelEngine singleton and get_state."""
    from modules.M250_StableWorldModelEngine import StableWorldModelEngine
    engine = StableWorldModelEngine.get_instance()
    assert type(engine).__name__ == "StableWorldModelEngine"
    state = engine.get_state()
    assert state['engine'] == 'StableWorldModelEngine'
    assert state['version'] == 'v7.37'
    print(f"  M250 Engine: {state['engine']} v{state['version']}, status={state['status']}")
    return True


def test_m250_world_model():
    """Test WorldModelTransition predict functionality."""
    from modules.M250_StableWorldModelEngine import WorldModelTransition, WorldState, Action
    import numpy as np
    model = WorldModelTransition(state_dim=4, action_dim=2, use_composite_prior=True)
    s = WorldState(state_vector=np.array([0.1, 0.2, 0.3, 0.4]))
    a = Action(action_vector=np.array([0.5, -0.3]))
    s_next = model.predict(s, a)
    assert s_next.state_vector.shape == (4,), f"Expected shape (4,), got {s_next.state_vector.shape}"
    assert np.all(np.isfinite(s_next.state_vector)), "Predicted state contains NaN/Inf"
    print(f"  WorldModel: s={s.state_vector} + a={a.action_vector} -> s'={s_next.state_vector}")
    return True


def test_m250_cem_planner():
    """Test CEMPlanner planning functionality."""
    from modules.M250_StableWorldModelEngine import CEMPlanner, WorldModelTransition, WorldState, Action
    import numpy as np
    planner = CEMPlanner(action_dim=2, horizon=5, n_iterations=3)
    model = WorldModelTransition(state_dim=4, action_dim=2, use_composite_prior=False)
    s = WorldState(state_vector=np.array([0.1, 0.2, 0.3, 0.4]))
    cost_fn = lambda s, a: float(np.sum((s.state_vector - np.zeros(4)) ** 2))
    planned = planner.plan(s, model, cost_fn, verbose=False)
    assert planned.shape == (5, 2), f"Expected shape (5,2), got {planned.shape}"
    assert np.all(np.isfinite(planned)), "Planned actions contain NaN/Inf"
    print(f"  CEMPlanner: planned {planned.shape} action sequence")
    return True


def test_m250_mpc_controller():
    """Test MPCController episode execution."""
    from modules.M250_StableWorldModelEngine import (
        MPCController, WorldModelTransition, CEMPlanner, WorldState
    )
    import numpy as np
    model = WorldModelTransition(state_dim=4, action_dim=2, use_composite_prior=False)
    planner = CEMPlanner(action_dim=2, horizon=3, n_iterations=2)
    controller = MPCController(world_model=model, planner=planner)
    s = WorldState(state_vector=np.array([0.5, 0.5, 0.5, 0.5]))
    trajectory = controller.run_episode(
        initial_state=s,
        target_state=np.array([1.0, 0.0, 0.0, 0.0]),
        n_steps=5
    )
    assert len(trajectory.transitions) == 5, f"Expected 5 transitions, got {len(trajectory.transitions)}"
    print(f"  MPCController: {len(trajectory.transitions)} steps, total_reward={trajectory.total_reward:.4f}")
    return True


def test_m250_ood_evaluator():
    """Test OODEvaluator distribution generalization."""
    from modules.M250_StableWorldModelEngine import (
        OODEvaluator, WorldModelTransition, WorldState, Action, Transition
    )
    import numpy as np
    model = WorldModelTransition(state_dim=4, action_dim=2, use_composite_prior=False)
    evaluator = OODEvaluator(world_model=model)
    s = WorldState(state_vector=np.array([0.1, 0.2, 0.3, 0.4]))
    a = Action(action_vector=np.array([0.5, -0.3]))
    s_next = model.predict(s, a)
    in_dist = [Transition(state=s, action=a, next_state=s_next) for _ in range(20)]
    ood = [Transition(state=s, action=a, next_state=s_next) for _ in range(20)]
    result = evaluator.evaluate(in_dist, ood)
    assert result.in_distribution_error >= 0, "In-dist error should be non-negative"
    assert result.out_of_distribution_error >= 0, "OOD error should be non-negative"
    print(f"  OODEvaluator: in_dist_err={result.in_distribution_error:.4f}, "
          f"ood_err={result.out_of_distribution_error:.4f}, "
          f"gap={result.generalization_gap:.4f}")
    return True


def test_t290():
    """T2.90: World Model Prediction Consistency — f_θ deterministic under same input."""
    from modules.M250_StableWorldModelEngine import verify_theorem_t290
    r = verify_theorem_t290()
    proved = r.get('proved', False)
    print(f"  T2.90 World Model Prediction Consistency: proved={proved}")
    return proved


def test_t291():
    """T2.91: CEM Convergence — elite set quality monotonically improves."""
    from modules.M250_StableWorldModelEngine import verify_theorem_t291
    r = verify_theorem_t291()
    proved = r.get('proved', False)
    print(f"  T2.91 CEM Convergence: proved={proved}")
    return proved


def test_t292():
    """T2.92: MPC Optimality — receding horizon cost bounded."""
    from modules.M250_StableWorldModelEngine import verify_theorem_t292
    r = verify_theorem_t292()
    proved = r.get('proved', False)
    print(f"  T2.92 MPC Optimality: proved={proved}")
    return proved


def test_t293():
    """T2.93: OOD Generalization Bound — gap bounded by W_dist."""
    from modules.M250_StableWorldModelEngine import verify_theorem_t293
    r = verify_theorem_t293()
    proved = r.get('proved', False)
    print(f"  T2.93 OOD Generalization Bound: proved={proved}")
    return proved


def test_t294():
    """T2.94: Composite Physics Prior — Liu principle + EML improve prediction."""
    from modules.M250_StableWorldModelEngine import verify_theorem_t294
    r = verify_theorem_t294()
    proved = r.get('proved', False)
    print(f"  T2.94 Composite Physics Prior: proved={proved}")
    return proved


def test_t295():
    """T2.95: Environment Transfer — world model fine-tunes across domains."""
    from modules.M250_StableWorldModelEngine import verify_theorem_t295
    r = verify_theorem_t295()
    proved = r.get('proved', False)
    print(f"  T2.95 Environment Transfer: proved={proved}")
    return proved


def test_p23():
    """P23: CEM with composite physics prior converges faster than vanilla."""
    from modules.M250_StableWorldModelEngine import verify_prediction_p23
    r = verify_prediction_p23()
    passed = r.get('passed', False)
    print(f"  P23 CEM+Prior Convergence: passed={passed}")
    return passed


def test_p24():
    """P24: World model with composite prior has lower OOD error."""
    from modules.M250_StableWorldModelEngine import verify_prediction_p24
    r = verify_prediction_p24()
    passed = r.get('passed', False)
    print(f"  P24 Composite Prior OOD: passed={passed}")
    return passed


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MVE_v737: M250 StableWorldModel Engine -- T2.90-T2.95 + P23-P24")
    print("=" * 60)

    results = {}

    # Engine & component tests
    print("\n--- Component Tests ---")
    results["M250_Engine"] = test_m250_engine()
    results["M250_WorldModel"] = test_m250_world_model()
    results["M250_CEM"] = test_m250_cem_planner()
    results["M250_MPC"] = test_m250_mpc_controller()
    results["M250_OOD"] = test_m250_ood_evaluator()

    # Theorem tests
    print("\n--- Theorem Verification ---")
    results["T2.90"] = test_t290()
    results["T2.91"] = test_t291()
    results["T2.92"] = test_t292()
    results["T2.93"] = test_t293()
    results["T2.94"] = test_t294()
    results["T2.95"] = test_t295()

    # Prediction tests
    print("\n--- Prediction Verification ---")
    results["P23"] = test_p23()
    results["P24"] = test_p24()

    # Summary
    print("\n" + "=" * 60)
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    for k, v in results.items():
        status = "PASS" if v else "FAIL"
        print(f"  {k}: {status}")
    print(f"\nResult: {passed}/{total} PASS, {failed} FAIL")
    if failed == 0:
        print("MVE_v737: ALL TESTS PASSED!")
    else:
        print("MVE_v737: SOME TESTS FAILED")
    print("=" * 60)
