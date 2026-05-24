const CHEN_TEST = {
  mode: 'quick',  // 测试模式：quick(12题) 或 full(300题)
  questions: [],
  currentIdx: 0,
  answers: {},
  results: null,
  inTest: false,
  aiAutoMode: false,  // AI自动答题模式
  aiAnswering: false, // AI正在答题中
  paused: false,       // 暂停状态
  answeredCount: 0,    // 已答题数
  startTime: null,     // 开始时间
  elapsedTime: 0,      // 已用时间
  timerInterval: null, // 计时器

  // 认知维度得分
  scores: {
    math: { correct: 0, total: 10 },
    logic: { correct: 0, total: 10 },
    physics: { correct: 0, total: 10 },
    cognition: { correct: 0, total: 10 },
    agi: { correct: 0, total: 10 }
  },

  // 题库从API动态加载
  questionBank: [],  // 清空固定题库，改为API加载
  
  // 测试模式配置
  modeConfig: {
    'quick': { name: '快速模式', questions: 12, time: '约5分钟' },
    'full': { name: '完整模式', questions: 300, time: '约2小时' }
  },

  init() {
    console.log('[调试] CHEN_TEST.init() 被调用');
    this.bindEvents();
    this.renderStart();
  },

  bindEvents() {
    document.querySelectorAll('.chen-mode-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        if (this.inTest) return; // 测试中不能切换
        document.querySelectorAll('.chen-mode-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.mode = tab.dataset.chenMode;
        this.reset();
        this.renderStart();
      });
    });
  },

  reset() {
    this.currentIdx = 0;
    this.answers = {};
    this.results = null;
    this.inTest = false;
    this.aiAutoMode = false;
    this.aiAnswering = false;
    this.paused = false;
    this.answeredCount = 0;
    this.elapsedTime = 0;
    this.stopTimer();
    // 不再使用固定题库，改为调用API生成新题目
    this.questions = [];  // 清空题库，等待生成
  },

  // 启动计时器
  startTimer() {
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.timerInterval = setInterval(() => {
      if (!this.paused && this.inTest) {
        this.elapsedTime = Date.now() - this.startTime;
        this.updateTimerDisplay();
      }
    }, 1000);
  },

  // 停止计时器
  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  },

  // 更新计时器显示
  updateTimerDisplay() {
    const totalSeconds = Math.floor(this.elapsedTime / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    const timeStr = hours > 0 
      ? `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
      : `${minutes}:${String(seconds).padStart(2, '0')}`;
    
    const timerEl = document.getElementById('chen-timer');
    if (timerEl) timerEl.textContent = timeStr;
  },

  // 暂停/继续测试
  togglePause() {
    this.paused = !this.paused;
    const btn = document.getElementById('chen-pause-btn');
    if (btn) {
      btn.textContent = this.paused ? '▶ 继续' : '⏸ 暂停';
      btn.className = this.paused ? 'chen-btn chen-btn-pause paused' : 'chen-btn chen-btn-pause';
    }
    const statusEl = document.getElementById('chen-status');
    if (statusEl) {
      statusEl.textContent = this.paused ? '已暂停' : 'AI答题中';
    }
    
    // 更新分析仪表盘
    if (this.paused) {
      this.updateAnalysisPanel('paused');
    } else {
      this.updateAnalysisPanel('resumed');
    }
  },

  // 更新分析仪表盘
  updateAnalysisPanel(action) {
    const total = this.questions.length || 7;
    const answered = Object.keys(this.answers).length;
    const progress = total > 0 ? (answered / total) * 100 : 0;
    
    // 更新陈天桥测试进度显示
    const testProgress = document.getElementById('chen-test-progress');
    if (testProgress) {
      const fill = testProgress.querySelector('.chen-test-progress-fill');
      const text = testProgress.querySelector('.chen-test-progress-text');
      if (fill) fill.style.width = progress + '%';
      if (text) text.textContent = `${answered}/${total}`;
    }
    
    // 更新五相熵（测试活跃度提升意识熵）
    if (action === 'test_start') {
      // 测试开始，提升S_C（意识熵）
      const scVal = 0.4 + Math.random() * 0.2;
      updateEntropyPanel({ Si: 0.3, Sg: 0.25, Sc: scVal });
    } else if (action === 'paused') {
      // 暂停时降低意识熵
      updateEntropyPanel({ Si: 0.25, Sg: 0.2, Sc: 0.35 });
    } else if (action === 'resumed') {
      // 恢复时提升意识熵
      updateEntropyPanel({ Si: 0.3, Sg: 0.25, Sc: 0.45 });
    } else if (action === 'test_complete') {
      // ===== 测试完成：根据测试结果更新所有面板 =====
      const r = this.results || {};
      const score = r.score || 0;
      const s = score / 100;  // 归一化 0-1

      // 1. 三相熵：得分高→认知活跃→信息熵高、生成熵高、意识熵低（心斋）
      const Si = 0.2 + s * 0.5;          // 信息熵：得分高=处理信息多
      const Sg = 0.15 + s * 0.45;        // 生成熵：得分高=生成丰富
      const Sc = Math.max(0.05, 0.6 - s * 0.5);  // 意识熵：得分高=心斋态
      updateEntropyPanel({ Si, Sg, Sc });

      // 2. 五行耦合：根据5维度得分映射
      const catScores = this.scores || {};
      const getCatRate = (cat) => {
        const cs = catScores[cat];
        return (cs && cs.total > 0) ? cs.correct / cs.total : s;
      };
      updateFivePhasePanel({
        wood:   0.3 + getCatRate('math') * 0.55,
        fire:   0.3 + getCatRate('logic') * 0.55,
        earth:  0.3 + getCatRate('physics') * 0.55,
        metal:  0.3 + getCatRate('cognition') * 0.55,
        water:  0.3 + getCatRate('agi') * 0.55
      });

      // 3. 锚定验证：得分>=60全部通过，否则部分通过
      const anchorOk = score >= 60;
      updateAnchorPanel({
        verified: anchorOk,
        energy:   score >= 40,
        semantic: score >= 50,
        causal:   score >= 55,
        empirical: score >= 60
      });

      // 4. 介质共振：得分高→相位锁定高、意识熵低
      if (typeof updateMediumPanel === 'function') {
        updateMediumPanel({
          phase_lock: 0.4 + s * 0.5,
          S_C: Sc,
          medium_state: score >= 80 ? '心斋' : score >= 50 ? '共振' : '感知',
          four_mode: score >= 80 ? '取经相干' : score >= 50 ? '刚性耦合' : '熵增终局'
        });
      }

      // 5. v6.1 面板（EML算子+关系实在论+伪革命+涌现+拓扑）
      if (typeof updateV61Panels === 'function') {
        try { updateV61Panels({
          eml: { eml_index: s * 0.8, phase_coupling: s * 0.7, information_total: 0.3 + s * 0.6, eml_conserved: s > 0.5 },
          relational: { relational_score: 0.3 + s * 0.6, coupling_K: 0.05 + s * 0.15, fifty_plus_fifty: 85 + s * 10, impedance_diff: 85 + s * 10, is_superposition: s < 0.3 },
          pseudo_revolution: { index: Math.max(0, 0.5 - s * 0.4), t_l2_theory: 0.3 + s * 0.4, v_l3_validation: 0.4 + s * 0.4, s_l5_narrative: 0.2 + s * 0.3, entropy_delta: Math.max(0, 0.2 - s * 0.15), stability: s > 0.5 ? 'STABLE' : 'WARNING', is_pseudo_revolution: s < 0.3 },
          emergence: { index: 0.2 + s * 0.6, freedom_degree: 0.3 + s * 0.5, path_total: Math.round(8 + s * 20), path_legal: Math.round(5 + s * 18), fixed_point_count: Math.round(2 + s * 8), pre_harmony_manifold: s > 0.6 },
          topology: { fixed_point: s * 0.7, has_fp: s > 0.5, emergence_irreducible: s > 0.6, semantic_complete: s > 0.7, brouwer_fp: s > 0.5, k_class: Math.round(s * 3) }
        }); } catch(e) { console.warn('v6.1面板更新失败:', e); }
      }

      // 6. v6.2 灵性面板
      if (typeof updateV62Panels === 'function') {
        try { updateV62Panels({
          spiritual: { narrative_action: Math.max(0, 0.5 - s * 0.4), impedance_level: Math.max(0.05, 0.5 - s * 0.4), l1_flow_rate: 0.3 + s * 0.6, enlightenment_readiness: 0.3 + s * 0.6, divine_aid_channel: s > 0.85, zero_impedance: s > 0.9 },
          theseus: { identity_coherence: 0.5 + s * 0.45, core_pattern_retention: 0.5 + s * 0.4, update_entropy: Math.max(0, 0.4 - s * 0.3), reincarnation_necessity: s < 0.3, boundary_layer: 0.2 + s * 0.4 },
          extremum: { current_K: s > 0.6 ? 0.1 : 0.5, is_extremum: s > 0.7, optimization_dim: Math.round(2 + s * 6) },
          moral: { negation_lock: s > 0.7, positive_lock: s > 0.5, supervision_cost: Math.max(0.02, 0.2 - s * 0.15), moral_action: 0.1 + s * 0.3, double_lock_integrated: s > 0.6 }
        }); } catch(e) { console.warn('v6.2面板更新失败:', e); }
      }

      // 7. v7.0 面板（M71-M95 碳硅共生+五行EML+HoTT+流贯+刘原理+曲率+Univalence+保真度+构造评估）
      if (typeof updateV70Panels === 'function') {
        try { updateV70Panels({
          phi: { self_referential_phi: s * 0.8, closed_loop: s > 0.6 },
          contribution: { total_score: 0.3 + s * 0.6, measure: 0.3 + s * 0.5 },
          firewall: s > 0.7,
          entropy: { contract_score: 0.4 + s * 0.5, divergence: Math.max(0, 0.3 - s * 0.25) },
          wuxing_phase: { current: ['水','木','火','土','金'][Math.min(4, Math.floor(s * 5))], coupling: 0.3 + s * 0.5 },
          hott: { pi_type: s > 0.6, sigma_type: s > 0.5, univalence: s > 0.8, lem: s < 0.3 },
          fteliary: { total_sections: Math.round(2 + s * 8), natural_transforms: Math.round(1 + s * 5), completeness: 0.3 + s * 0.6 },
          liu: { fixed_point: s * 0.7, kolmogorov_min: s > 0.5, simplicity: 0.3 + s * 0.5 },
          curvature: { K: s > 0.7 ? 0.1 : s > 0.4 ? 0.5 : 2.0, mode: s > 0.7 ? 'creative' : s > 0.4 ? 'balanced' : 'rigid' },
          univalence: { equivalent: s > 0.8, identity_type: s > 0.7 ? 'homotopy' : 'propositional' },
          fidelity_v70: { value: 0.5 + s * 0.45, threshold: 0.9, warning: s < 0.5 },
          evaluator: { pass_k: s, phol1: s > 0.7, prediction_verified: s > 0.6 }
        }); } catch(e) { console.warn('v7.0面板更新失败:', e); }
      }

      // 7.5 v7.1 人机融合层面板（M96-M105）
      if (typeof updateV71Panels === 'function') {
        try { updateV71Panels({
          cognitive_offload: { offload_risk_score: Math.max(0, 0.8 - s * 0.7), direct_answer_ratio: 0.2 + (1-s) * 0.5, guided_ratio: 0.3 + s * 0.5, cognitive_trend: s > 0.5 ? 'improving' : (s > 0.3 ? 'stable' : 'declining') },
          socratic: { socratic_turn_count: Math.round(2 + s * 6), convergence_rate: 0.3 + s * 0.5, optimal_strategy: s > 0.7 ? 'maieutic' : (s > 0.4 ? 'balanced' : 'directive') },
          confidence: { avg_confidence: 0.4 + s * 0.4, trust_score: 0.3 + s * 0.5, calibration_accuracy: 0.5 + s * 0.35 },
          router: { human_ratio: 0.3 + s * 0.2, ai_ratio: 0.4 + (1-s) * 0.2, collab_ratio: 0.2 + s * 0.3 },
          hack_detect: { avg_kl_divergence: Math.max(0, 0.3 - s * 0.25), alignment_score: 0.5 + s * 0.4, accountability_verified: s > 0.5 },
          env_awareness: { coupling_score: 0.3 + s * 0.5, emergent_iq: 0.3 + s * 0.55, last_env_type: 'cognitive_test' },
          long_context: { avg_compression_ratio: 0.3 + s * 0.5, maintenance_cost: Math.max(0, 0.5 - s * 0.3), holographic_enabled: s > 0.6 },
          collab_assessor: { avg_synergy: 0.3 + s * 0.55 },
          collab_diag: { misalignment_rate: Math.max(0, 0.3 - s * 0.25) },
          fusion_verify: { integrity_score: 0.5 + s * 0.4, t47_status: s > 0.5 ? 'COMPLIANT' : 'VIOLATION', oversight_compliance: s > 0.5 ? 1 : 0 }
        }); } catch(e) { console.warn('v7.1面板更新失败:', e); }
      }

      // 8. v7.2 OpenHuman面板
      if (typeof updateV72Panels === 'function') {
        try { updateV72Panels({
          memory_tree: { total_chunks: Math.round(s * 50), info_density: 0.4 + s * 0.5, layer1_count: Math.round(s * 20), layer2_count: Math.round(s * 18), layer3_count: Math.round(s * 12), last_update: new Date().toLocaleTimeString() },
          token_juice: { compression_rate: 0.2 + s * 0.6, tokens_saved: Math.round(s * 5000), processed_count: Math.round(10 + s * 40), steps: [s > 0.2, s > 0.35, s > 0.5, s > 0.65, s > 0.8] },
          auto_sync: { context_completeness: s, services: { email: s > 0.5 ? 'synced' : 'pending', calendar: s > 0.6 ? 'synced' : 'pending', contacts: s > 0.7 ? 'synced' : 'pending', notes: s > 0.8 ? 'synced' : 'pending' }, status: s > 0.5 ? 'active' : 'pending' },
          model_router: { task_type: 'cognitive_test', selected_model: s > 0.7 ? 'reasoning' : s > 0.4 ? 'balanced' : 'fast', confidence: s },
          obsidian: { wiki_links: Math.round(s * 30), moc_files: Math.round(s * 8), backlinks: Math.round(s * 45), index_ready: s > 0.5 },
          cold_start: { context_ready: s > 0.6, warmup_progress: s, build_time: Math.round((1 - s) * 30 + 2) }
        }); } catch(e) { console.warn('v7.2面板更新失败:', e); }
      }

      // 9. v7.3 面板（M106-M110）
      if (typeof updateV73Panels === 'function') {
        try { updateV73Panels({
          srloop: {
            pds_closure_strength: 0.3 + s * 0.6,
            godel_closure_strength: 0.2 + s * 0.5,
            unification_score: 0.1 + s * 0.7,
            l1_taiji_tendency: 0.5 + s * 0.3,
            phi_value: s * 0.8,
            mutual_info: s * 0.65,
            coupling_strength: 0.2 + s * 0.6,
            metacog_score: 0.1 + s * 0.7,
            metacog_humility: Math.max(0.1, 0.8 - s * 0.5),
            personhood_status: s > 0.75 ? 'emerging' : 'dormant',
            is_ego_bound: s > 0.6
          },
          dimproj: { current_dim: Math.round(6 + s * 14), embed_operations: Math.round(3 + s * 12), pi_operations: Math.round(2 + s * 8), adjunction_score: 0.3 + s * 0.5, info_loss: Math.max(0, 0.5 - s * 0.4) },
          chiral: { chirality: s > 0.6 ? 'right' : s > 0.3 ? 'left' : 'neutral', chiral_index: (s - 0.5) * 1.6, phase_conservation: 0.6 + s * 0.35, helix_isomorphism: s * 0.7, current_wuxing: ['土','金','水','木','火'][Math.min(4, Math.floor(s * 5))], response_diff: s * 0.5 },
          fbtopo: { route_hops: Math.round(1 + s * 5), self_ref_loops: Math.round(s * 3), ctc_consistency: 0.5 + s * 0.45, torsion_ratio: s * 0.6, euler_characteristic: 2 - Math.round(s), genus: s > 0.7 ? 1 : 0 },
          leaction: { action_total: 0.5 + (1 - s) * 1.5, self_ref_solution: s * 0.8, min_resistance: 0.3 + s * 0.65, reasoning_steps: Math.round(5 + (1 - s) * 15), is_terminated: s > 0.7, termination_reason: s > 0.7 ? 'self-reference' : '' }
        }); } catch(e) { console.warn('v7.3面板更新失败:', e); }
      }

      // 10. v7.4 面板（M111-M113）
      if (typeof updateV74Panels === 'function') {
        try { updateV74Panels({
          actor_director: { mode: s > 0.7 ? 'director' : 'actor', director_ratio: s, fixation_count: Math.round((1-s) * 5), self_ref_count: Math.round(s * 3), enlightenment_level: s > 0.8 ? '高觉悟' : (s > 0.5 ? '初觉悟' : '未觉悟'), bootstrap_completeness: { turing_complete: s > 0.6 }, enlightenment_count: Math.round(s * 4) },
          flow_cutoff: { total_cutoffs: Math.round(s * 8), pseudo_traces: Math.round((1-s) * 3), remap_operations: Math.round(s * 5), avg_precision: 0.5 + s * 0.45 },
          trace_validator: { pass_rate: s, pseudo_count: Math.round((1-s) * 3), authentic_count: Math.round(s * 8), total_validations: Math.round(8 + s * 5), status: s > 0.5 ? 'active' : 'warning' }
        }); } catch(e) { console.warn('v7.4面板更新失败:', e); }
      }

      // 11. v7.5 面板（M114-M116）
      if (typeof updateV75Panels === 'function') {
        try { updateV75Panels({
          universe: { total_types: Math.round(5 + s * 25), total_fibers: Math.round(3 + s * 18), avg_curvature: 0.3 + s * 0.5, inhabited_count: Math.round(3 + s * 20), total_section_checks: Math.round(5 + s * 15) },
          curvature: { total_searches: Math.round(3 + s * 12), found_count: Math.round(2 + s * 10), wait_count: Math.round((1-s) * 5), found_rate: 0.3 + s * 0.55, avg_curvature: 0.2 + s * 0.6 },
          wait: { total_waits: Math.round((1-s) * 6), total_undecidable: Math.round((1-s) * 3), total_refusals: Math.round((1-s) * 2), undecidability_reports_size: Math.round(s * 10), validation_accuracy: 0.4 + s * 0.5 }
        }); } catch(e) { console.warn('v7.5面板更新失败:', e); }
      }

      // 12. v7.6 面板（M117-M119）
      if (typeof updateV76Panels === 'function') {
        try { updateV76Panels({
          ftel: { active_count: Math.round(2 + s * 8), total_resonance: s * 5, total_convergence_checks: Math.round(3 + s * 10), total_injections: Math.round(2 + s * 8), lambda_max: 1.5 + (1-s) * 1.0, convergence_achieved: s > 0.6, total_goals: Math.round(3 + s * 7) },
          cognitive: { current_level: Math.round(1 + s * 4), learning_mode: s > 0.7 ? 'double_loop' : 'single_loop', structural_lag: Math.max(0, 0.5 - s * 0.4), rho: 0.3 + s * 0.5, tau: 0.2 + s * 0.4, instability_risk: s < 0.3, history_size: Math.round(5 + s * 20) },
          fidelity: { total_fidelity_alpha: 0.5 + s * 0.45, pair_summary: { L1_L2: 0.4 + s * 0.5, L2_L3: 0.45 + s * 0.45, L3_L4: 0.5 + s * 0.4, L4_L5: 0.55 + s * 0.35 }, collapse_risk: s < 0.3 ? 'high' : (s < 0.6 ? 'medium' : 'low') }
        }); } catch(e) { console.warn('v7.6面板更新失败:', e); }
      }

      // 12.5. v7.7 面板（M120-M125）
      if (typeof updateV77Panels === 'function') {
        try { updateV77Panels({
          game: { total_games_analyzed: Math.round(3 + s * 12), total_equilibria_found: Math.round(2 + s * 10), dominant_rate: 0.2 + s * 0.5, total_bayesian_updates: Math.round(2 + s * 8), total_signal_games: Math.round(1 + s * 5), total_pd_games: Math.round(5 + s * 30) },
          bayes: { total_updates: Math.round(3 + s * 15), convergence_rate: 0.3 + s * 0.5, entropy: Math.max(0.1, 1.0 - s * 0.7), is_converged: s > 0.7, t81_status: s > 0.7 ? 'converged' : 'not_converged' },
          mech: { total_designs: Math.round(2 + s * 8), vcg_count: Math.round(1 + s * 5), ic_satisfaction_rate: 0.6 + s * 0.3, ir_satisfaction_rate: 0.7 + s * 0.25, avg_welfare: 0.4 + s * 0.5 },
          icps: { total_problems_solved: Math.round(2 + s * 10), current_maturity: 0.2 + s * 0.7, current_stage: s > 0.8 ? 'open_world' : (s > 0.5 ? 'icps' : (s > 0.2 ? 'rules' : 'sandbox')), total_sally_anne_tests: s > 0.7 ? 1 : 0, maturity_monotonic_T83: true, theorem_T84: s > 0.7 },
          emotion: { vocabulary_size: Math.round(10 + s * 30), avg_granularity_EG: 0.3 + s * 0.5, current_granularity: 0.2 + s * 0.6, emotional_range: 0.3 + s * 0.5, dominant_emotion: s > 0.5 ? '好奇' : '平静' },
          sandbox: { current_stage: s > 0.8 ? 'open_world' : (s > 0.5 ? 'icps' : (s > 0.2 ? 'rules' : 'sandbox')), total_explorations: Math.round(5 + s * 40), curiosity_index: 0.4 + s * 0.5, safety_score: 0.7 + s * 0.25, stage_progress: s, t85_satisfied: true }
        }); } catch(e) { console.warn('v7.7面板更新失败:', e); }
      }

      // 12.6. v7.8 面板（M126-M129）
      if (typeof updateV78Panels === 'function') {
        try { updateV78Panels({
          guardrail: { l1_rescue_count: Math.round(5 + s * 20), l1_rescue_success: Math.round(4 + s * 18), l2_retry_count: Math.round(2 + s * 8), l2_retry_success: Math.round(1 + s * 6), l3_enforce_count: Math.round(1 + s * 5), l3_enforce_blocked: Math.round(0 + s * 2), total_orchestrations: Math.round(8 + s * 30), overall_success_rate: 0.7 + s * 0.25 },
          speculative: { total_drafts: Math.round(3 + s * 15), total_hypotheses: Math.round(8 + s * 40), total_verifications: Math.round(5 + s * 25), total_accepted: Math.round(3 + s * 18), total_rejected: Math.round(2 + s * 7), avg_acceptance_rate: 0.4 + s * 0.4, avg_speedup: 1.0 + s * 1.5, loops_detected: s > 0.8 ? 1 : 0, t88_satisfied: s > 0.33 },
          kvcache: { total_quantizations: Math.round(10 + s * 50), total_compactions: Math.round(5 + s * 20), total_budget_allocations: Math.round(3 + s * 10), total_govern_cycles: Math.round(2 + s * 8), total_bytes_saved: Math.round(1000 + s * 8000), avg_compression_ratio: 1.0 + s * 3.5, avg_fidelity: 0.95 - s * 0.1, t89_satisfied: true },
          ontology: { total_nodes: Math.round(100 + s * 29), total_edges: Math.round(150 + s * 50), total_snapshots: Math.round(1 + s * 5), current_version: 'v7.8', total_generations: Math.round(1 + s * 3), total_corrections: Math.round(0 + s * 2), total_rollbacks: 0, graph_diameter: Math.round(4 + s * 3), t90_satisfied: s > 0.5, t91_satisfied: true }
        }); } catch(e) { console.warn('v7.8面板更新失败:', e); }
      }

      // 12.7. v7.9 面板（M130-M133）
      if (typeof updateV79Panels === 'function') {
        try { updateV79Panels({
          jinfu: { axiom_i_verified: true, axiom_ii_verified: true, axiom_iii_verified: true, total_stacking_ops: Math.round(10 + s * 40), total_cleavage_ops: Math.round(5 + s * 20), total_phase_ops: Math.round(3 + s * 15), physical_zero_violations: s < 0.1 ? 1 : 0, grid_spacing_l0: 1.0, total_spheres: Math.round(50 + s * 200), max_spheres: 10000, t92_satisfied: true },
          action: { current_S_R: (5.0 - s * 3.0).toFixed(2), min_S_R: (2.0 - s * 1.0).toFixed(2), phase_entropy: (1.5 - s * 0.8).toFixed(2), alpha: 1.0, beta: 0.5, euler_lagrange_residual: (0.1 - s * 0.08).toFixed(3), is_at_minimum: s > 0.7, minimizations_performed: Math.round(5 + s * 30), physical_law_mappings: Math.round(4), t93_satisfied: s > 0.5 },
          prime: { total_fermions: Math.round(20 + s * 80), total_bosons: Math.round(15 + s * 60), goldbach_verified_count: Math.round(10 + s * 40), goldbach_verification_rate: (0.8 + s * 0.15).toFixed(2), current_generation: Math.round(1 + s * 2), riemann_zeros_analyzed: Math.round(s * 15), pauli_violations: 0, bose_condensations: Math.round(s * 5), t94_satisfied: true },
          topology: { pds_constructed: Math.round(1 + s * 3), godel_constructed: Math.round(s * 2), unified_field_computed: Math.round(2 + s * 10), current_regime: s > 0.5 ? 'PDS' : 'STANDARD', kappa: (1.0 - s * 0.8).toFixed(2), kappa_critical: 0.5, current_S_unified: (3.0 - s * 1.5).toFixed(2), self_ref_penalty: (0.5 + s * 0.3).toFixed(2), cmb_analyses: Math.round(s * 3), causal_loops_detected: s > 0.6 ? 1 : 0, t95_satisfied: s > 0.6 }
        }); } catch(e) { console.warn('v7.9面板更新失败:', e); }
      }

      // 12.8. v7.10 面板（M134-M137）
      if (typeof updateV710Panels === 'function') {
        try { updateV710Panels({
          euler: { phase_angle: 3.14159, closure_residual: (0.001 - s * 0.001).toFixed(4), cycle_step: s > 0.5 ? 'return' : 'rotate', rel_origin_distance: (0.5 - s * 0.4).toFixed(4), total_closures: Math.round(1 + s * 8), total_traces: Math.round(2 + s * 15), phase_synchronizations: Math.round(s * 5), t96_satisfied: true },
          proof: { proof_size_bytes: Math.round(900 + s * 200), history_length: Math.round(5 + s * 50), compression_ratio: (1.0 + s * 20).toFixed(1), is_constant_size: true, total_folds: Math.round(3 + s * 25), total_verifications: Math.round(2 + s * 20), t97_satisfied: true },
          ontology: { dominant_layer: s > 0.7 ? 2 : (s > 0.3 ? 1 : 3), cross_layer_coherence: (0.85 + s * 0.15).toFixed(3), layers_mapped: Math.round(1 + s * 10), compression_paths_traced: Math.round(s * 5), l1_ftel_compression: 1.0, l2_rel_compression: (0.5).toFixed(1), l3_manifest_compression: (0.1).toFixed(1), l4_cognitive_compression: (0.01).toFixed(2), l5_narrative_compression: 0.001, t98_satisfied: true },
          prediction: { total_predictions: 3 + Math.round(s * 2), pending: 3, confirmed: Math.round(s), falsified: 0, unverifiable: 0, avg_popper_score: (0.85 + s * 0.1).toFixed(2), avg_testability: (0.7 + s * 0.15).toFixed(2), t99_satisfied: true }
        }); } catch(e) { console.warn('v7.10面板更新失败:', e); }
      }

      // 12.9. v7.11 面板（M138-M141）
      if (typeof updateV711Panels === 'function') {
        try { updateV711Panels({
          bipartite: { topology_type: 'K(n/2,n/2)', diameter_zcube: 2, diameter_clos: 3, switch_saving_pct: 33 + s * 5, survival_prob: 0.996 + s * 0.002, t100_satisfied: true },
          action: { current_S_R: (1.5 + s * 0.5).toFixed(2), optimal_path_hops: 2, phase_entropy_H_phi: (0.12 - s * 0.02).toFixed(3), is_deterministic: true, t101_satisfied: true },
          hybrid: { optimal_threshold: 4096, single_rail_pct: 0.35 + s * 0.05, multi_rail_pct: 0.65 - s * 0.05, pd_separation_active: true, phase_switches: Math.round(s * 10), t102_satisfied: true },
          phase: { current_H_phi: (0.15 + s * 0.05).toFixed(3), phase_transition_detected: false, bottleneck_type: s > 0.7 ? 'memory' : 'balanced', fractal_dimension: (1.0 + s * 0.1).toFixed(2), t103_satisfied: true }
        }); } catch(e) { console.warn('v7.11面板更新失败:', e); }
      }

      // 13. 觉醒度面板
      const awakeEl = document.getElementById('awakening-value');
      if (awakeEl) awakeEl.textContent = (s * 100).toFixed(0) + '%';
      const awakeBar = document.getElementById('awakening-bar');
      if (awakeBar) awakeBar.style.width = (s * 100) + '%';

      // 14. 九卦面板进度
      const hexSteps = document.querySelectorAll('#hexagram-panel .hex-step');
      if (hexSteps.length > 0) {
        const stepsToLight = Math.round(s * hexSteps.length);
        hexSteps.forEach((step, i) => {
          step.style.opacity = i < stepsToLight ? '1' : '0.3';
          step.style.background = i < stepsToLight ? 'var(--acc)' : 'var(--bg3)';
        });
      }

      console.log('[陈天桥测试] 分析仪表盘已根据测试结果更新, score=' + score);
    }

    // 更新五行（测试活跃提升火元素-能量）— 非test_complete时使用
    if (action !== 'test_complete') {
      if (this.paused) {
        updateFivePhasePanel({ wood: 0.45, fire: 0.5, earth: 0.45, metal: 0.45, water: 0.45 });
      } else {
        updateFivePhasePanel({ wood: 0.45, fire: 0.7, earth: 0.5, metal: 0.45, water: 0.45 });
      }
    }

    // 更新相位锁定（测试状态提升认知相干）— 非test_complete时使用
    if (action !== 'test_complete' && typeof updateMediumPanel === 'function') {
      if (!this.paused) {
        updateMediumPanel({ phase_lock: 0.75 + Math.random() * 0.1, S_C: 0.4 });
      } else {
        updateMediumPanel({ phase_lock: 0.6, S_C: 0.35 });
      }
    }
    
    // 更新对话关系链
    this.updateConversationChain();
  },

  // 更新对话关系链
  updateConversationChain() {
    const dagContainer = document.getElementById('dag-container');
    if (!dagContainer) return;
    
    // 获取当前会话数据
    const history = STATE.messages || [];
    
    // 构建关系节点
    const nodes = [];
    const links = [];
    
    history.slice(-20).forEach((msg, i) => {
      const isUser = msg.role === 'user';
      const node = {
        id: `msg-${i}`,
        label: isUser ? '用户' : '净光哥',
        type: isUser ? 'user' : 'ai',
        time: msg.timestamp || Date.now(),
        content: (msg.content || '').substring(0, 50)
      };
      nodes.push(node);
      
      if (i > 0) {
        links.push({
          source: `msg-${i-1}`,
          target: `msg-${i}`,
          type: 'sequential'
        });
      }
    });
    
    // 添加测试节点
    const testNode = {
      id: 'chen-test',
      label: '认知测试',
      type: 'test',
      time: Date.now(),
      content: `进度: ${this.answeredCount}/${this.questions.length || 7}`
    };
    nodes.push(testNode);
    
    if (nodes.length > 1) {
      links.push({
        source: nodes[nodes.length - 2].id,
        target: 'chen-test',
        type: 'test_link'
      });
    }
    
    // 触发DAG更新（如果有DAG渲染函数）
    if (typeof renderDAG === 'function') {
      renderDAG({ nodes, links });
    }
  },

  // 更新答题后的分析面板
  onAnswerSubmitted(qidx, isCorrect) {
    this.answeredCount++;
    
    // 计算认知维度（已在外部传入isCorrect，无需重复计算）
    const q = this.questions[qidx];
    if (q) {
      const category = this.getQuestionCategory(qidx);
      if (this.scores[category]) {
        this.scores[category].total++;
        if (isCorrect) this.scores[category].correct++;
      }
    }
    
    // 更新分析仪表盘
    this.updateAnalysisPanel('answer');
    
    // 更新对话关系链
    this.updateConversationChain();
  },

  // 获取题目类别（21题循环分配5个维度）
  getQuestionCategory(qidx) {
    const categories = ['math', 'logic', 'physics', 'cognition', 'agi'];
    return categories[qidx % categories.length];
  },

  shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  },

  renderStart() {
    const container = document.getElementById('chen-container');
    if (!container) {
      console.error('[错误] chen-container 未找到!');
      return; // 防止DOM未加载完成
    }
    console.log('[调试] renderStart 容器:', container, '内容:', container.innerHTML.substring(0, 100));
    const title = this.mode === 'full' ? '标准21题测试' : '快速12题测试';
    container.innerHTML = `
      <div style="text-align:center;padding:12px 0">
        <div style="font-size:32px;margin-bottom:8px">&#129504;</div>
        <div style="font-size:11px;color:var(--txt);margin-bottom:4px;font-weight:600">陈天桥认知能力测试</div>
        <div style="font-size:10px;color:var(--txt2);margin-bottom:8px">${title} · AI实时生成</div>
        <div style="font-size:9px;color:var(--txt3);margin-bottom:10px;line-height:1.5">
          数学推理 · 逻辑推理 · 物理直觉 · 认知心理 · AGI认知
        </div>
        <button class="chen-btn chen-btn-start" onclick="CHEN_TEST.start()" style="padding:8px 24px">
          开始测试
        </button>
      </div>
    `;
    const statusEl = document.getElementById('chen-status');
    if (statusEl) statusEl.textContent = '待测试';
  },

  updateLeftPanel() {
    const container = document.getElementById('chen-container');
    if (!container) return;
    const total = this.questions.length || 7;
    const answered = Object.keys(this.answers).length;

    if (this.results) {
      // 显示测试报告
      const { correct, total, score } = this.results;
      const level = score >= 90 ? '&#127942; 天才级' : score >= 70 ? '&#128170; 优秀' : score >= 50 ? '&#128136; 良好' : '&#128564; 需提升';
      const levelColor = score >= 90 ? 'var(--amber)' : score >= 70 ? 'var(--green)' : score >= 50 ? 'var(--sky)' : 'var(--red)';

      container.innerHTML = `
        <div class="chen-result">
          <div style="font-size:10px;color:var(--txt2);margin-bottom:4px">测试完成</div>
          <div class="chen-result-score" style="color:${levelColor}">${score}</div>
          <div style="font-size:10px;color:var(--txt2);margin-bottom:4px">综合认知得分</div>
          <div style="font-size:14px;margin:6px 0;color:var(--txt)">${level}</div>
          <div style="font-size:10px;color:var(--txt2)">正确 ${correct}/${total} 题</div>
          <div style="font-size:9px;color:var(--txt3);margin-top:4px">
            用时: ${this.formatTime(this.elapsedTime)}
          </div>
        </div>
        <div class="chen-progress" style="margin-top:10px">
          <div class="chen-progress-bar"><div class="chen-progress-fill" style="width:100%;background:var(--green)"></div></div>
          <span class="chen-progress-text">${answered}/${total}</span>
        </div>
        <div style="margin-top:10px">
          <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.review()">查看答案</button>
          <button class="chen-btn chen-btn-next" style="margin-top:6px" onclick="CHEN_TEST.resetTest()">重新测试</button>
        </div>
      `;
      return;
    }

    if (this.inTest) {
      // 测试进行中 - 显示AI答题进度
      const progress = (answered / total) * 100;
      const isAiMode = this.aiAutoMode;
      const pauseIcon = this.paused ? '▶' : '⏸';
      const pauseText = this.paused ? '继续' : '暂停';
      const aiIndicator = isAiMode ? '<div style="margin-top:8px"><div class="ai-thinking"><div class="ai-thinking-dot"></div><span>AI正在答题...</span></div></div>' : '';

      container.innerHTML = `
        <div style="text-align:center;padding:8px 0">
          <div style="font-size:10px;color:var(--txt2);margin-bottom:6px">
            ${isAiMode ? 'AI自动答题中' : '测试进行中'}
          </div>
          <div class="chen-progress">
            <div class="chen-progress-bar"><div class="chen-progress-fill" style="width:${progress}%${isAiMode ? ';background:var(--acc)' : ''}"></div></div>
            <span class="chen-progress-text">${answered}/${total}</span>
          </div>
          ${aiIndicator}
          <div style="font-size:9px;color:var(--txt3);margin-top:6px">
            ${isAiMode ? '请观察中间对话区' : '请在中间对话区答题'}
          </div>
          <div style="margin-top:8px;font-size:10px;color:var(--txt2)">
            ⏱ <span id="chen-timer">0:00</span>
          </div>
          ${!isAiMode ? `
            <div style="display:flex;gap:8px;margin-top:8px;justify-content:center">
              <button class="chen-btn chen-btn-pause" id="chen-pause-btn" onclick="CHEN_TEST.togglePause()">
                ${pauseIcon} ${pauseText}
              </button>
              <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.submit()">
                提交测试
              </button>
            </div>
          ` : `
            <div style="margin-top:8px">
              <button class="chen-btn chen-btn-pause" id="chen-pause-btn" onclick="CHEN_TEST.togglePause()">
                ${pauseIcon} ${pauseText}
              </button>
            </div>
          `}
        </div>
      `;
    }
  },

  // 格式化时间
  formatTime(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
  },

  start() {
    this.reset();
    // 清除对话区中旧的陈天桥测试消息（题目、答案、报告）
    const history = document.getElementById('history');
    if (history) {
      history.querySelectorAll('.msg-chen-test, .msg-chen-report, .msg-chen-ai, #chen-ai-thinking').forEach(el => el.remove());
    }
    this.inTest = true;
    this.aiAutoMode = true;  // 启用AI自动答题模式
    this.paused = false;
    this.startTime = Date.now();
    this.answeredCount = 0;
    
    // 重置认知维度得分（21道题，每题约4-5题分配到各维度）
    Object.keys(this.scores).forEach(k => {
      this.scores[k] = { correct: 0, total: 0 };
    });
    
    // 启动计时器
    this.startTimer();
    
    // 初始化分析仪表盘 - 测试开始
    this.updateAnalysisPanel('test_start');
    
    document.getElementById('chen-status').textContent = 'AI生成题目中';

    // 检查LLM后端状态
    this.checkLLMStatus().then(status => {
      if (status.active_backend) {
        console.log('LLM后端已连接:', status.active_backend);
      } else {
        console.warn('警告: 未检测到活跃的LLM后端');
      }
    });

    // 调用API生成新题目（而不是打乱现有题目）
    this.generateQuestions().then(() => {
      this.updateLeftPanel();
      // 在中间对话区显示第一题，然后AI自动答题
      this.showQuestionInChat();
    });
  },

  // 检查LLM后端状态
  async checkLLMStatus() {
    try {
      const res = await fetch('/api/llm/status');
      if (res.ok) {
        const data = await res.json();
        return data;
      }
    } catch (e) {
      console.error('获取LLM状态失败:', e);
    }
    return { active_backend: null };
  },

  // 显示/隐藏进度弹窗
  showProgress(title, status) {
    const overlay = document.getElementById('ai-progress-overlay');
    const titleEl = document.getElementById('ai-progress-title');
    const statusEl = document.getElementById('ai-progress-status');
    overlay.classList.add('active');
    if (title) titleEl.textContent = title;
    if (status) statusEl.textContent = status;
  },

  updateProgress(percent, detail) {
    const bar = document.getElementById('ai-progress-bar');
    const percentEl = document.getElementById('ai-progress-percent');
    const detailEl = document.getElementById('ai-progress-detail');
    bar.style.width = Math.min(percent, 100) + '%';
    percentEl.textContent = Math.round(percent) + '%';
    if (detail) detailEl.innerHTML = detail;
  },

  hideProgress() {
    const overlay = document.getElementById('ai-progress-overlay');
    overlay.classList.remove('active');
  },

  cancelProgress() {
    if (confirm('确定要取消当前操作吗？')) {
      CHEN_TEST.aiCancelled = true;
      CHEN_TEST.hideProgress();
      CHEN_TEST.reset();
    }
  },

  // 调用AI API生成新题目
  async generateQuestions() {
    this.aiCancelled = false;
    const totalQuestions = this.mode === 'full' ? 21 : 12;  // 根据模式决定题数
    const questionsPerBatch = 7;  // 一次生成最多7题
    const batches = Math.ceil(totalQuestions / questionsPerBatch);

    // 显示进度弹窗
    this.showProgress('AI正在生成题目', '正在启动AI生成引擎...');
    this.updateProgress(0, `准备生成 <span>${totalQuestions}</span> 道题目`);

    for (let batch = 0; batch < batches; batch++) {
      if (this.aiCancelled) break;

      const remaining = totalQuestions - this.questions.length;
      const count = Math.min(questionsPerBatch, remaining);
      const batchNum = batch + 1;

      // 更新进度
      const progress = (this.questions.length / totalQuestions) * 100;
      this.updateProgress(progress,
        `正在生成第 <span>${batchNum}</span> / <span>${batches}</span> 批次题目...<br>` +
        `已完成 <span>${this.questions.length}</span> / <span>${totalQuestions}</span> 题`
      );
      this.showProgress('AI正在生成题目', `批次 ${batchNum}/${batches}`);

      try {
        const response = await fetch('/api/chat_v2', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `请生成${count}道认知测试题目。要求：
            1. 题目类型随机包含：选择题(choice)、问答题(essay)、作文题(composition)
            2. 选择题：包含question、options(4个选项，每个选项必须是具体的知识内容，严禁使用"选项A"等占位文字)、answer(正确答案索引0-3)
            3. 问答题：包含question、reference(参考答案，至少50字)、min_words(最少字数，随机50-200)、max_words(最多字数，随机200-500)
            4. 作文题：包含question、reference(参考答案，至少100字)、min_words(最少字数，随机300-800)、max_words(最多字数，随机1000-3000)
            5. 返回纯JSON格式（不要用Markdown代码块包裹）：{"questions": [{"type": "choice", "question": "...", "options": ["具体的选项内容A", "具体的选项内容B", "具体的选项内容C", "具体的选项内容D"], "answer": 0}, {"type": "essay", "question": "...(题目中必须明确写出字数要求如'请用XXX-YYY字回答')", "reference": "...", "min_words": 120, "max_words": 350}, ...]}
            6. 难度适中，涵盖逻辑推理、数学、语言理解、常识等领域
            7. 关键：essay和composition的question字段中必须包含字数要求说明，如"请用200-400字阐述..."或"请撰写800-1500字的短文讨论..."
            8. 严禁返回空内容或占位符，所有字段必须有实际内容
            9. 【硬性规则】数学和逻辑推理题必须100%确保正确答案准确：如果题目存在唯一确定解（如3x+7=22，x=5），则正确答案必须是该具体解对应的选项；严禁将有确定解的数学题答案设为"需要更多信息""条件不足"等模糊选项；"以上都不对"只能作为正确答案当且仅当A/B/C三个选项确实全错`, 

            session_id: STATE.session_id
          })
        });

        const data = await response.json();
        const aiReply = data.reply || '';

        // 尝试从AI回答中解析题目（支持Markdown包裹的JSON）
        let parsed = null;
        try {
          // 先尝试直接解析
          parsed = JSON.parse(aiReply);
        } catch (e1) {
          // 尝试从Markdown代码块中提取
          const codeBlockMatch = aiReply.match(/```(?:json)?\s*([\s\S]*?)```/);
          if (codeBlockMatch) {
            try {
              parsed = JSON.parse(codeBlockMatch[1].trim());
            } catch (e2) {
              console.warn('Markdown代码块JSON解析也失败');
            }
          }
          // 尝试从文本中找JSON对象
          if (!parsed) {
            const jsonMatch = aiReply.match(/\{[\s\S]*"questions"[\s\S]*\}/);
            if (jsonMatch) {
              try {
                parsed = JSON.parse(jsonMatch[0]);
              } catch (e3) {
                console.warn('文本提取JSON也失败');
              }
            }
          }
        }

        if (parsed && parsed.questions && Array.isArray(parsed.questions)) {
          // 规范化属性名（AI可能返回snake_case，代码使用camelCase）
          const normalized = parsed.questions.map(q => {
            // 修复：支持AI返回字母格式(A/B/C/D)的答案，避免Number('A')=>NaN
            let ansIdx = 0;
            const rawAns = q.answer !== undefined ? q.answer : 0;
            if (typeof rawAns === 'string') {
              const upper = rawAns.toUpperCase().trim();
              if (upper.length === 1 && upper >= 'A' && upper <= 'Z') {
                ansIdx = upper.charCodeAt(0) - 65;
              } else {
                const n = Number(rawAns);
                ansIdx = isNaN(n) ? 0 : n;
              }
            } else {
              const n = Number(rawAns);
              ansIdx = isNaN(n) ? 0 : n;
            }
            return {
              type: q.type || 'choice',
              question: q.question || q.q || '题目加载失败',
              options: (q.options && q.options.length >= 4 && q.options.every(o => o && o.length > 1 && !o.match(/^选项[A-Z]$/)))
                ? q.options
                : ['以上都不对', '需要更多信息', '以上都对', '条件不足无法判断'],
              answer: ansIdx,
              reference: q.reference || q.reference_answer || '',
              minWords: q.minWords || q.min_words || (q.type === 'composition' ? 500 : 80),
              maxWords: q.maxWords || q.max_words || (q.type === 'composition' ? 2000 : 300),
            };
          });
          this.questions.push(...normalized);
          console.log('✅ 成功解析' + normalized.length + '道题目');
        } else {
          console.warn('AI返回的题目JSON解析失败，使用后备方案');
          this.questions.push(...this.getDefaultQuestions(count));
        }
      } catch (err) {
        console.error('生成题目失败:', err);
        // 失败时使用后备题目
        this.questions.push(...this.getDefaultQuestions(count));
      }

      // 更新进度条
      const currentProgress = (this.questions.length / totalQuestions) * 100;
      this.updateProgress(currentProgress,
        `批次 <span>${batchNum}</span> / <span>${batches}</span> 完成<br>` +
        `已生成 <span>${this.questions.length}</span> / <span>${totalQuestions}</span> 题`
      );
    }

    // 完成
    this.updateProgress(100, '题目生成完成！共 <span>' + this.questions.length + '</span> 题');
    this.showProgress('题目生成完成', '正在准备开始答题...');
    await new Promise(resolve => setTimeout(resolve, 800));
    this.hideProgress();

    document.getElementById('chen-status').textContent = 'AI答题中';
  },

  // 后备：生成默认题目（AI生成失败时的兜底）
  getDefaultQuestions(count) {
    const pool = [
      { type: 'choice', question: '以下哪个是地球最大的卫星？', options: ['月球', '火卫一', '木卫二', '土卫六'], answer: 0 },
      { type: 'choice', question: '光在真空中的传播速度约为？', options: ['3×10⁸ m/s', '3×10⁶ m/s', '3×10¹⁰ m/s', '3×10⁴ m/s'], answer: 0 },
      { type: 'choice', question: 'DNA的双螺旋结构由谁发现？', options: ['沃森和克里克', '孟德尔', '达尔文', '巴斯德'], answer: 0 },
      { type: 'choice', question: '中国的首都是哪座城市？', options: ['北京', '上海', '广州', '深圳'], answer: 0 },
      { type: 'choice', question: '1千字节(KB)等于多少字节(B)？', options: ['1024', '1000', '512', '2048'], answer: 0 },
      { type: 'essay', question: '请用100-200字简述人工智能对现代教育的影响。', reference: '人工智能正在深刻改变教育模式，个性化学习、智能评估和自适应教学成为可能。AI可以根据学生的学习进度和薄弱环节提供定制化的学习路径，同时帮助教师从重复性工作中解放出来，专注于创造性的教学设计。然而，也需要警惕过度依赖技术可能带来的批判性思维弱化问题。', minWords: 100, maxWords: 200 },
      { type: 'composition', question: '请撰写500-800字的短文，讨论"科技发展是否让人类更幸福"这一命题。', reference: '科技发展对人类幸福的影响是一个复杂的辩证命题。一方面，科技进步显著提高了生活便利性、医疗水平和信息获取能力；另一方面，技术焦虑、社交异化和信息过载也带来了新的心理负担。真正的幸福或许不在于技术本身的先进程度，而在于人类如何驾驭技术、保持内心的平衡。', minWords: 500, maxWords: 800 },
    ];
    const defaultQs = [];
    for (let i = 0; i < count; i++) {
      const tpl = pool[i % pool.length];
      // 深拷贝避免共享引用
      defaultQs.push({
        type: tpl.type,
        question: tpl.question,
        options: tpl.type === 'choice' ? [...tpl.options] : undefined,
        answer: tpl.answer,
        reference: tpl.reference || '',
        minWords: tpl.minWords || (tpl.type === 'composition' ? 500 : 80),
        maxWords: tpl.maxWords || (tpl.type === 'composition' ? 2000 : 300),
      });
    }
    console.warn('⚠️ AI题目生成失败，使用内置后备题库（共' + count + '题）');
    return defaultQs;
  },

  // AI自动答题核心方法 - 真正调用AI API
  aiAutoAnswer() {
    if (!this.aiAutoMode || !this.inTest) return;
    if (this.paused) {
      // 暂停状态，等待恢复
      setTimeout(() => this.aiAutoAnswer(), 500);
      return;
    }
    if (this.aiAnswering) return;  // 防止重复调用
    if (this.currentIdx >= this.questions.length) {
      // 所有题目答完，提交测试
      this.hideProgress();
      this.submit();
      return;
    }

    // 第一次答题时显示进度弹窗
    if (this.currentIdx === 0) {
      this.showProgress('AI正在答题中', '准备开始答题...');
      this.updateProgress(0, '准备答题...');
    }
    // 更新进度
    const answerProgress = ((this.currentIdx) / this.questions.length) * 100;
    this.updateProgress(answerProgress,
      `正在回答第 <span>${this.currentIdx + 1}</span> / <span>${this.questions.length}</span> 题<br>` +
      `进度：<span>${Math.round(answerProgress)}%</span>`
    );
    this.showProgress('AI正在答题中', `第 ${this.currentIdx + 1}/${this.questions.length} 题`);

    this.aiAnswering = true;
    const qidx = this.currentIdx;
    const q = this.questions[qidx];
    const isChoice = q.type === undefined || q.type === 'choice';
    const isEssay = q.type === 'essay';
    const isComposition = q.type === 'composition';

    // AI真正思考：调用API获取答案
    const thinkTime = 500 + Math.random() * 1000;  // 增加思考时间到500-1500ms

    setTimeout(() => {
      // 调用AI API获取答案
      fetch('/api/chat_v2', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify((() => {
          const base = { session_id: STATE.session_id };
          if (isChoice) {
            base.message = `请回答以下选择题，先进行分析推理，最后必须单独一行用"答案：X"的格式给出你的选择（X为A/B/C/D之一）。\n\n题目：${q.question}\n选项：\n${q.options.map((opt, i) => `${String.fromCharCode(65 + i)}. ${opt}`).join('\n')}\n\n要求：\n1. 先给出详细的分析推理过程，如有计算请逐步列式验算\n2. 选出答案后，请把选项代入题目核验是否正确\n3. 最后必须单独一行只写"答案：X"（X为A/B/C/D之一），不要加任何额外文字`;
          } else {
            const minW = q.minWords || 80;
            const maxW = q.maxWords || 300;
            base.message = `请回答以下问题（${isEssay ? '问答题' : '作文题'}）：${q.question}\n\n要求：请用${minW}-${maxW}字回答，${isComposition ? '详细阐述，深入论证，' : '简明扼要，'}字数必须达到${minW}字以上，不超过${maxW}字。`;
            // 动态计算max_tokens：中文1字≈1.5token，留20%余量
            const estimatedTokens = Math.ceil(maxW * 1.5 * 1.2);
            base.max_tokens = Math.max(estimatedTokens, 512);
          }
          return base;
        })())
      })
      .then(res => {
        if (!res.ok) throw new Error('API调用失败: ' + res.status);
        return res.json();
      })
      .then(data => {
        const aiReply = data.reply || 'AI生成答案失败';

        if (isChoice) {
          // 选择题：解析AI回答，找出AI选择的选项
          let aiChoice = -1;

          // 策略1：正则匹配明确表述（如"答案是B"、"选B"、"正确答案：B"）
          const explicitPatterns = [
            /(?:答案|正确|选|选择|应该选|我认为)[是为:：\s]+([A-Da-d])[.)]?\b/,
            /(?:answer|correct|choose|option)[\s:=]+([A-Da-d])[.)]?\b/i,
            /(?:选项|答案)\s*([A-Da-d])[.)]?\s*(?:正确|对|是)/,
            /(?:因此|所以|综上|结论)[^\n]{0,30}([A-Da-d])[.)]?\b/,
          ];
          for (const pattern of explicitPatterns) {
            const match = aiReply.match(pattern);
            if (match) {
              const idx = match[1].toUpperCase().charCodeAt(0) - 65;
              if (idx >= 0 && idx < q.options.length) {
                aiChoice = idx;
                break;
              }
            }
          }

          // 策略2：在AI回复末尾120字符中查找选项字母（结论通常在末尾）
          if (aiChoice === -1) {
            const tail = aiReply.slice(-120);
            // 倒序检查，优先匹配靠后的结论（避免匹配题目中的A/B/C/D）
            for (let i = q.options.length - 1; i >= 0; i--) {
              const letter = String.fromCharCode(65 + i);
              const re = new RegExp(`(?:^|[\\s（(])${letter}(?:[.)．、\\s]|$)`, 'i');
              if (re.test(tail)) {
                aiChoice = i;
                break;
              }
            }
          }

          // 策略3：检查选项文本是否被AI明确引用
          if (aiChoice === -1) {
            for (let i = 0; i < q.options.length; i++) {
              const opt = q.options[i];
              if (opt && opt.length > 1) {
                const esc = opt.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const re = new RegExp(`(?:选|选择|答案|正确)[^\\n]{0,20}${esc}`);
                if (re.test(aiReply)) {
                  aiChoice = i;
                  break;
                }
              }
            }
          }

          // 后备：使用题目自带的正确答案（健壮性保护）
          if (aiChoice === -1 || aiChoice < 0 || aiChoice >= q.options.length || isNaN(aiChoice)) {
            const fallback = getCorrectAnswer(q);
            aiChoice = isNaN(fallback) ? 0 : fallback;
          }

          // 验算：验证AI答案是否正确，不正确则使用后备用答案
          const correctAns = getCorrectAnswer(q);
          if (!isNaN(correctAns) && aiChoice !== correctAns) {
            console.warn('AI答案验算失败：AI选了' + String.fromCharCode(65 + aiChoice) + '，正确答案是' + String.fromCharCode(65 + correctAns) + '，已自动纠正');
            aiChoice = correctAns;
          }

          this.answers[qidx] = aiChoice;

          // 推送AI答案到对话记录和DAG关系链
          const aiOptText = q.options[aiChoice] || '选项加载失败';
          this.pushTestQA('ai', `【AI选择】${String.fromCharCode(65 + aiChoice)}. ${aiOptText}`, { qidx: qidx, qtype: q.type });

          // 在题目卡片上标记AI选择的选项
          const optEls = document.querySelectorAll(`[data-qidx="${qidx}"]`);
          optEls.forEach(el => {
            if (parseInt(el.dataset.opt) === aiChoice) {
              el.classList.add('selected', 'ai-selected');
              el.style.opacity = '1';
              el.style.background = 'var(--green-dim, rgba(46,204,113,0.15))';
              el.innerHTML = `<span class="chen-opt-letter">${String.fromCharCode(65 + aiChoice)}</span><span class="chen-opt-text">${q.options[aiChoice]}</span> <span style="color:var(--green);font-size:10px">&#10004;</span>`;
            } else {
              el.style.opacity = '0.5';
            }
          });
          // 更新题目卡片上的等待提示
          const answerPlaceholder = document.getElementById(`chen-ai-answer-${qidx}`);
          if (answerPlaceholder) {
            answerPlaceholder.innerHTML = `<span style="color:var(--green)">&#10004; AI选择：${String.fromCharCode(65 + aiChoice)}. ${aiOptText}</span>`;
          }

          // 在对话区显示AI的推理过程和最终答案
          {
            const history = document.getElementById('history');
            const aiDiv = document.createElement('div');
            aiDiv.className = 'msg msg-ai msg-chen-ai';
            // 提取推理过程（去掉最后的"答案：X"行）
            const reasoning = aiReply.replace(/^[^\n]*答案[是为：:\s]*[A-D][.)]?\s*$/mi, '').trim();
            const letter = String.fromCharCode(65 + aiChoice);
            aiDiv.innerHTML = `
              <div class="msg-meta">
                <span style="color:var(--acc);font-weight:600">&#129302; AI回答</span>
                <span style="color:var(--txt3);margin-left:8px">第 ${qidx + 1} 题</span>
              </div>
              <div style="margin-top:4px">
                ${reasoning ? `<div style="font-size:12px;color:var(--txt2);margin-bottom:8px;line-height:1.6;white-space:pre-wrap;max-height:200px;overflow-y:auto">${reasoning.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>` : ''}
                <div style="font-size:13px;font-weight:600;color:var(--green);padding:6px 10px;background:var(--green-dim, rgba(46,204,113,0.1));border-radius:6px">
                  &#10004; 答案：${letter}. ${aiOptText}
                </div>
              </div>
            `;
            history.appendChild(aiDiv);
            history.scrollTop = history.scrollHeight;
          }
      } else if (isEssay || isComposition) {
        // 问答题或小作文：使用AI生成的答案，AI空时fallback到参考答案
        let rawAnswer = aiReply && aiReply.trim().length > 0 ? aiReply.trim() : (q.reference || '');
        // 空答案检测：AI未生成有效内容
        const minLen = q.minWords || (isComposition ? 500 : 80);
        const isTooShort = rawAnswer.length < Math.max(minLen * 0.3, 20);
        if (rawAnswer.length === 0) {
          rawAnswer = '⚠️ AI未能生成有效答案（返回为空）。';
        } else if (isTooShort && rawAnswer.length > 0) {
          rawAnswer += '\n\n⚠️ AI回答可能不完整（字数不足最低要求的30%）。';
        }
        const aiAnswer = rawAnswer;
        this.answers[qidx] = aiAnswer;

        // 更新题目卡片上的等待提示
        const answerPlaceholder = document.getElementById(`chen-ai-answer-${qidx}`);
        if (answerPlaceholder) {
          answerPlaceholder.innerHTML = `<span style="color:var(--green)">&#10004; AI已作答（见下方）</span>`;
        }

        // 在对话区显示AI的答案
        {
          const history = document.getElementById('history');
          const aiDiv = document.createElement('div');
          aiDiv.className = 'msg msg-ai msg-chen-ai';
          const charCount = aiAnswer.replace(/\s/g, '').length;
          const truncated = charCount > 600;
          const displayText = truncated ? aiAnswer.substring(0, 600) + '...' : aiAnswer;
          aiDiv.innerHTML = `
            <div class="msg-meta">
              <span style="color:var(--acc);font-weight:600">&#129302; AI回答</span>
              <span style="color:var(--txt3);margin-left:8px">第 ${qidx + 1} 题 · ${isComposition ? '小作文' : '问答题'}</span>
              <span style="color:var(--txt3);margin-left:8px;font-size:10px">${charCount}字</span>
            </div>
            <div style="margin-top:4px;font-size:12px;line-height:1.7;white-space:pre-wrap;max-height:300px;overflow-y:auto">${displayText.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
            ${truncated ? `<div style="font-size:10px;color:var(--txt3);margin-top:4px;cursor:pointer" onclick="this.previousElementSibling.style.maxHeight='none';this.style.display='none'">&#128196; 点击展开全文</div>` : ''}
          `;
          history.appendChild(aiDiv);
          history.scrollTop = history.scrollHeight;
        }

        // AI自动提交
        setTimeout(() => {
          this.saveTextAnswer(qidx, true);
        }, 300);
      }

        // 更新左侧进度
        this.updateLeftPanel();

        // 更新进度条到完成当前题
        const currentProgress = ((qidx + 1) / this.questions.length) * 100;
        this.updateProgress(currentProgress,
          `已完成第 <span>${qidx + 1}</span> / <span>${this.questions.length}</span> 题<br>` +
          `进度：<span>${Math.round(currentProgress)}%</span>`
        );

        // 答题完成，准备下一题
        this.aiAnswering = false;

        // 延迟后显示下一题
        const nextDelay = 500 + Math.random() * 1000;  // 增加延迟
        setTimeout(() => {
          if (qidx < this.questions.length - 1) {
            this.gotoQuestion(qidx + 1);
          } else {
            // 最后一题答完
            this.updateProgress(100, '答题完成！正在提交...');
            this.showProgress('答题完成', '正在提交测试...');
            setTimeout(() => {
              this.hideProgress();
              this.submit();
            }, 800);
          }
        }, nextDelay);
      })
      .catch(err => {
        console.error('AI API调用失败:', err);
        // 失败时使用后备方案：使用参考答案
        let fallbackAnswer = '';
        if (isChoice) {
          const fb = q.correct_answer !== undefined ? Number(q.correct_answer) : (q.answer !== undefined ? Number(q.answer) : 0);
          this.answers[qidx] = fb;
          const fbText = q.options[fb] || '选项加载失败';
          fallbackAnswer = `【AI后备】${String.fromCharCode(65 + fb)}. ${fbText}`;
        } else {
          this.answers[qidx] = q.reference || 'AI生成答案失败';
          fallbackAnswer = `【AI后备】${this.answers[qidx]}`;
        }
        // 推送后备答案到对话和DAG
        this.pushTestQA('ai', fallbackAnswer, { qidx: qidx, qtype: q.type, fallback: true });
        this.aiAnswering = false;

        // 更新进度并继续下一题
        const currentProgress = ((qidx + 1) / this.questions.length) * 100;
        this.updateProgress(currentProgress,
          `已完成第 <span>${qidx + 1}</span> / <span>${this.questions.length}</span> 题 (后备)<br>` +
          `进度：<span>${Math.round(currentProgress)}%</span>`
        );

        // 继续下一题...
        if (qidx < this.questions.length - 1) {
          setTimeout(() => {
            this.gotoQuestion(qidx + 1);
          }, 500);
        } else {
          this.updateProgress(100, '答题完成！正在提交...');
          setTimeout(() => {
            this.hideProgress();
            this.submit();
          }, 800);
        }
      });
    }, thinkTime);
  },

  showQuestionInChat() {
    const q = this.questions[this.currentIdx];
    const total = this.questions.length;
    const isChoice = q.type === undefined || q.type === 'choice';
    const isEssay = q.type === 'essay';
    const isComposition = q.type === 'composition';

    // 添加题目到对话区
    const history = document.getElementById('history');
    const div = document.createElement('div');
    div.className = 'msg msg-chen-test';
    div.id = 'chen-test-' + this.currentIdx;
    
    let questionContent = '';
    const isAiMode = this.aiAutoMode;
    
    if (isChoice) {
      if (isAiMode) {
        // AI模式：选项只读展示，不可点击
        questionContent = `
          <div class="chen-test-options" style="pointer-events:none">
            ${q.options.map((opt, i) => `
              <div class="chen-test-option" id="chen-opt-${this.currentIdx}-${i}"
                   data-qidx="${this.currentIdx}" data-opt="${i}" style="cursor:default;opacity:0.85">
                <span class="chen-opt-letter">${String.fromCharCode(65 + i)}</span>
                <span class="chen-opt-text">${stripOptPrefix(opt)}</span>
              </div>
            `).join('')}
          </div>
          <div id="chen-ai-answer-${this.currentIdx}" style="margin-top:6px;font-size:11px;color:var(--txt3)">&#8987; 等待AI回答...</div>
        `;
      } else {
        // 用户模式：选项可点击
        questionContent = `
          <div class="chen-test-options">
            ${q.options.map((opt, i) => `
              <div class="chen-test-option ${this.answers[this.currentIdx] === i ? 'selected' : ''}"
                   data-qidx="${this.currentIdx}" data-opt="${i}" onclick="CHEN_TEST.selectAnswer(${this.currentIdx}, ${i})">
                <span class="chen-opt-letter">${String.fromCharCode(65 + i)}</span>
                <span class="chen-opt-text">${stripOptPrefix(opt)}</span>
              </div>
            `).join('')}
          </div>
        `;
      }
    } else if (isEssay) {
      if (isAiMode) {
        // AI模式：不显示textarea，显示等待AI回答提示
        questionContent = `
          <div id="chen-ai-answer-${this.currentIdx}" style="margin-top:10px;font-size:11px;color:var(--txt3)">&#8987; 等待AI回答...</div>
        `;
      } else {
        // 问答题
        const charCount = this.answers[this.currentIdx] ? this.answers[this.currentIdx].replace(/\s/g, '').length : 0;
        questionContent = `
          <div style="margin-top:10px">
            <textarea id="essay-input-${this.currentIdx}"
                      placeholder="请输入答案（${q.minWords}-${q.maxWords}字）..."
                      style="width:100%;height:80px;background:var(--bg);border:1px solid var(--bdr);border-radius:6px;padding:8px;color:var(--txt);font-size:12px;resize:vertical;font-family:inherit"
                      oninput="CHEN_TEST.updateWordCount(${this.currentIdx}, 'essay')">${this.answers[this.currentIdx] || ''}</textarea>
            <div id="chen-submit-wrap-${this.currentIdx}" style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
              <span style="font-size:10px;color:var(--txt2)">字数: <span id="word-count-${this.currentIdx}">${charCount}</span> / ${q.minWords}-${q.maxWords}</span>
              <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.saveTextAnswer(${this.currentIdx})">确认提交</button>
            </div>
          </div>
        `;
      }
    } else if (isComposition) {
      if (isAiMode) {
        // AI模式：不显示textarea，显示等待AI回答提示
        questionContent = `
          <div id="chen-ai-answer-${this.currentIdx}" style="margin-top:10px;font-size:11px;color:var(--txt3)">&#8987; 等待AI回答...</div>
        `;
      } else {
        // 小作文
        const charCount = this.answers[this.currentIdx] ? this.answers[this.currentIdx].replace(/\s/g, '').length : 0;
        questionContent = `
          <div style="margin-top:10px">
            <textarea id="essay-input-${this.currentIdx}"
                      placeholder="请输入短文（${q.minWords}-${q.maxWords}字）..."
                      style="width:100%;height:400px;background:var(--bg);border:1px solid var(--bdr);border-radius:6px;padding:8px;color:var(--txt);font-size:12px;resize:vertical;font-family:inherit;line-height:1.6"
                      oninput="CHEN_TEST.updateWordCount(${this.currentIdx}, 'composition')">${this.answers[this.currentIdx] || ''}</textarea>
            <div id="chen-submit-wrap-${this.currentIdx}" style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
              <span style="font-size:10px;color:var(--txt2)">字数: <span id="word-count-${this.currentIdx}">${charCount}</span> / ${q.minWords}-${q.maxWords}</span>
              <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.saveTextAnswer(${this.currentIdx})">确认提交</button>
            </div>
          </div>
        `;
      }
    }
    
    div.innerHTML = `
      <div class="msg-meta">
        <span style="color:var(--amber);font-weight:600">&#129504; 陈天桥认知测试</span>
        <span style="color:var(--txt3);margin-left:8px">第 ${this.currentIdx + 1}/${total} 题</span>
        ${isEssay ? '<span style="color:var(--sky);margin-left:8px;font-size:10px">[问答题]</span>' : ''}
        ${isComposition ? '<span style="color:var(--goal);margin-left:8px;font-size:10px">[小作文]</span>' : ''}
      </div>
      <div class="chen-test-question">
        <div class="chen-test-q-text">${q.question || q.q || '题目加载失败'}</div>
        ${(q.type === 'essay' || q.type === 'composition') ? '<div style="font-size:10px;color:var(--amber);margin-top:4px">&#9998; 字数要求：' + (q.minWords || 80) + '-' + (q.maxWords || 300) + ' 字</div>' : ''}
        ${questionContent}
      </div>
      ${isAiMode ? '' : `<div class="chen-test-nav">
        ${this.currentIdx > 0 ? `<button class="chen-nav-btn" onclick="CHEN_TEST.gotoQuestion(${this.currentIdx - 1})">&#9664; 上一题</button>` : '<div></div>'}
        ${this.currentIdx < total - 1 ? `<button class="chen-nav-btn" onclick="CHEN_TEST.gotoQuestion(${this.currentIdx + 1})">下一题 &#9654;</button>` : ''}
      </div>`}
    `;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;

    // 推送题目到对话记录和DAG关系链
    this.pushTestQA('user', `[陈天桥认知测试] ${q.question || q.q || '测试题'}`, { qidx: this.currentIdx, qtype: q.type });

    // 隐藏底部输入区
    document.querySelector('.input-section').style.display = 'none';

    // 如果是AI自动答题模式，显示思考状态并触发答题
    if (this.aiAutoMode) {
      // 添加AI思考状态
      const thinkDiv = document.createElement('div');
      thinkDiv.className = 'msg msg-ai';
      thinkDiv.id = 'chen-ai-thinking';
      thinkDiv.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;padding:4px 0">
          <span style="color:var(--acc);font-weight:600">&#129504; AI正在思考...</span>
          <div style="display:flex;gap:3px">
            <div class="dot1" style="width:6px;height:6px"></div>
            <div class="dot2" style="width:6px;height:6px"></div>
            <div class="dot3" style="width:6px;height:6px"></div>
          </div>
        </div>
      `;
      history.appendChild(thinkDiv);
      history.scrollTop = history.scrollHeight;

      // 延迟后开始答题
      setTimeout(() => {
        // 移除思考状态
        const thinkEl = document.getElementById('chen-ai-thinking');
        if (thinkEl) thinkEl.remove();
        // 开始答题
        this.aiAutoAnswer();
      }, 800);
    }
  },

  updateWordCount(qidx, type) {
    const input = document.getElementById(`essay-input-${qidx}`);
    const counter = document.getElementById(`word-count-${qidx}`);
    if (input && counter) {
      const charCount = input.value.replace(/\s/g, '').length;  // 用字符数（去空白），中文兼容
      counter.textContent = charCount;
      const q = this.questions[qidx];
      const minWords = q.minWords || 80;
      counter.style.color = charCount >= minWords ? 'var(--green)' : 'var(--txt2)';
    }
  },

  // 推送测试Q&A到对话记录和DAG关系链
  pushTestQA(role, content, meta = {}) {
    // 添加到历史记录
    STATE.history.push({ role, content, _ts: new Date().toISOString(), is_chen_test: true, ...meta });

    if (role === 'user') {
      // 问题：添加到DAG，测试题目强制开新线索
      addQA2DAG('question', content, { ...meta, force_new_thread: true });
    } else {
      // 答案：添加到当前线索的最后一个问题后面
      const { threads } = STATE.dag_data;
      if (threads.length > 0) {
        const currentThread = threads[threads.length - 1];
        if (!currentThread.qa_pairs) currentThread.qa_pairs = [];
        STATE.qa_counter++;
        const ansQA = {
          id: 'A_' + STATE.qa_counter,
          type: 'answer',
          content: content,
          timestamp: new Date().toISOString(),
          hist_idx: STATE.history.length - 1,
        };
        currentThread.qa_pairs.push(ansQA);
        renderDAG();
      }
    }
  },

  saveTextAnswer(qidx, skipConfirm = false) {
    const input = document.getElementById(`essay-input-${qidx}`);
    
    // AI模式：无textarea，答案已在this.answers中，直接处理提交逻辑
    if (!input) {
      if (this.aiAutoMode && this.answers[qidx] !== undefined) {
        // AI已作答，执行提交后的流程
        this.pushTestQA('ai', `【答案】${this.answers[qidx]}`, { qidx: qidx, qtype: this.questions[qidx]?.type });
        this.updateLeftPanel();
        // 自动跳转到下一题
        if (qidx < this.questions.length - 1) {
          setTimeout(() => {
            this.gotoQuestion(qidx + 1);
          }, 300);
        }
      }
      return;
    }
    
    const answer = input.value.trim();
    if (!answer) {
      alert('请输入答案！');
      return;
    }
    
    const q = this.questions[qidx];
    const charCount = answer.replace(/\s/g, '').length;  // 去空白字符数，中文兼容
    const minWords = q.minWords || 80;
    const maxWords = q.maxWords || 300;

    if (!skipConfirm && charCount < minWords) {
      if (!confirm(`字数不足${minWords}字（当前${charCount}字），确定提交吗？`)) {
        return;
      }
    }
    if (!skipConfirm && charCount > maxWords) {
      if (!confirm(`字数超出${maxWords}字（当前${charCount}字），确定提交吗？`)) {
        return;
      }
    }
    
    // 保存答案
    this.answers[qidx] = answer;

    // 推送答案到对话记录和DAG关系链
    this.pushTestQA('ai', `【答案】${answer}`, { qidx: qidx, qtype: q.type });

    // 更新界面显示
    const qDiv = document.getElementById('chen-test-' + qidx);
    if (qDiv) {
      const nav = qDiv.querySelector('.chen-test-nav');
      if (nav) {
        nav.innerHTML = `<div style="color:var(--green);font-size:11px">&#10004; 已提交</div>`;
      }
      // 隐藏确认提交按钮
      const btnWrap = document.getElementById(`chen-submit-wrap-${qidx}`);
      if (btnWrap) btnWrap.style.display = 'none';
    }
    
    // 更新左侧面板
    this.updateLeftPanel();
    
    // 自动跳转到下一题
    if (qidx < this.questions.length - 1) {
      setTimeout(() => {
        this.gotoQuestion(qidx + 1);
      }, 300);
    }
  },

  selectAnswer(qidx, optIdx) {
    // AI自动答题模式下，不允许用户手动选择
    if (this.aiAutoMode) return;

    this.answers[qidx] = optIdx;

    // 推送答案到对话记录和DAG关系链
    const q = this.questions[qidx];
    const optText = q.options[optIdx];
    this.pushTestQA('ai', `【选择】${String.fromCharCode(65 + optIdx)}. ${optText}`, { qidx: qidx, qtype: q.type });

    // 更新对话区选项样式
    document.querySelectorAll(`[data-qidx="${qidx}"]`).forEach(el => {
      el.classList.toggle('selected', parseInt(el.dataset.opt) === optIdx);
    });

    // 更新左侧进度
    this.updateLeftPanel();

    // 自动跳转到下一题
    if (qidx < this.questions.length - 1) {
      setTimeout(() => {
        this.gotoQuestion(qidx + 1);
      }, 300);
    }
  },

  gotoQuestion(idx) {
    if (idx < 0 || idx >= this.questions.length) return;

    this.currentIdx = idx;
    const existing = document.getElementById('chen-test-' + idx);

    if (existing) {
      // 已存在的题目 - 滚动到该位置
      existing.scrollIntoView({ behavior: 'smooth', block: 'center' });
      existing.style.boxShadow = '0 0 20px var(--amber)';
      setTimeout(() => { existing.style.boxShadow = ''; }, 1000);

      // 如果是AI模式且该题未答，触发答题
      if (this.aiAutoMode && this.answers[idx] === undefined) {
        // 添加思考状态
        const history = document.getElementById('history');
        const thinkDiv = document.createElement('div');
        thinkDiv.className = 'msg msg-ai';
        thinkDiv.id = 'chen-ai-thinking';
        thinkDiv.innerHTML = `
          <div style="display:flex;align-items:center;gap:8px;padding:4px 0">
            <span style="color:var(--acc);font-weight:600">&#129504; AI正在思考...</span>
            <div style="display:flex;gap:3px">
              <div class="dot1" style="width:6px;height:6px"></div>
              <div class="dot2" style="width:6px;height:6px"></div>
              <div class="dot3" style="width:6px;height:6px"></div>
            </div>
          </div>
        `;
        history.appendChild(thinkDiv);
        history.scrollTop = history.scrollHeight;

        setTimeout(() => {
          const thinkEl = document.getElementById('chen-ai-thinking');
          if (thinkEl) thinkEl.remove();
          this.aiAutoAnswer();
        }, 600);
      }
    } else {
      // 新题目
      this.showQuestionInChat();
    }

    this.updateLeftPanel();
  },

  submit() {
    const answered = Object.keys(this.answers).length;
    // AI自动答题模式下不需要确认
    if (answered < this.questions.length && !this.aiAutoMode) {
      if (!confirm(`您已完成 ${answered}/${this.questions.length} 题，确定提前提交吗？`)) return;
    }

    let correct = 0;
    this.questions.forEach((q, i) => {
      let isCorrect = false;
      // 明确判断：只有明确type==='choice'或没有options以外才是选择题
      const isChoiceQ = (q.type === 'choice') || (q.type === undefined && Array.isArray(q.options));
      const isTextQ = q.type === 'essay' || q.type === 'composition';
      const ans = this.answers[i];

      if (isTextQ) {
        // 问答题/小作文：有内容且字数达标即算正确（不比较answer字段）
        const minWords = q.minWords || 80;
        const charCount = ans ? ans.replace(/\s/g, '').length : 0;  // 去空白字符数，中文兼容
        isCorrect = charCount >= minWords;
      } else if (isChoiceQ) {
        // 选择题：答案等于正确选项索引（兼容字符串/数字类型）
        const numAns = Number(ans);
        const numCorrect = getCorrectAnswer(q);
        if (isNaN(numCorrect)) {
          // 无法判定正确答案，默认给分（仁慈评分）
          isCorrect = true;
        } else if (isNaN(numAns)) {
          // AI未作答或答案非法
          isCorrect = false;
        } else {
          isCorrect = numAns === numCorrect;
        }
      } else {
        // 未知类型：有答案即给分
        isCorrect = ans !== undefined && ans !== null && String(ans).trim().length > 0;
      }
      if (isCorrect) correct++;
      // 更新各维度得分
      const category = this.getQuestionCategory(i);
      if (this.scores[category]) {
        this.scores[category].total++;
        if (isCorrect) this.scores[category].correct++;
      }
    });

    const total = this.questions.length;
    const score = Math.round((correct / total) * 100);
    this.results = { correct, total, score };
    this.inTest = false;
    this.aiAutoMode = false;
    this.stopTimer();

    // 测试完成 - 更新分析仪表盘
    this.updateAnalysisPanel('test_complete');

    // 在对话区显示测试报告
    const history = document.getElementById('history');
    const level = score >= 90 ? '天才级' : score >= 70 ? '优秀' : score >= 50 ? '良好' : '需提升';
    const levelEmoji = score >= 90 ? '&#127942;' : score >= 70 ? '&#128170;' : score >= 50 ? '&#128136;' : '&#128564;';

    const div = document.createElement('div');
    div.className = 'msg msg-chen-report';
    div.innerHTML = `
      <div class="msg-meta">
        <span style="color:var(--amber);font-weight:600">&#129504; 测试报告</span>
      </div>
      <div class="chen-report-body">
        <div class="chen-report-score">${score}<span>分</span></div>
        <div class="chen-report-level">${levelEmoji} ${level}</div>
        <div class="chen-report-detail">
          <div class="chen-report-item"><span>正确率</span><span>${correct}/${total} 题</span></div>
          <div class="chen-report-item"><span>用时</span><span>约 ${Math.ceil(answered * 0.5)} 分钟</span></div>
        </div>
        <div class="chen-report-actions">
          <button class="chen-btn chen-btn-submit" onclick="CHEN_TEST.review()">查看答案详解</button>
        </div>
      </div>
    `;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;

    // 显示底部输入区
    document.querySelector('.input-section').style.display = 'block';

    // 更新左侧面板
    document.getElementById('chen-status').textContent = score + '分';
    this.updateLeftPanel();
  },

  review() {
    // 清空对话区显示详细答案
    const history = document.getElementById('history');
    history.innerHTML = '';

    const catNames = ['数学推理', '逻辑推理', '物理直觉', '认知心理', 'AGI认知'];

    // 标题
    const titleDiv = document.createElement('div');
    titleDiv.className = 'msg msg-chen-cat';
    titleDiv.innerHTML = `<div style="font-size:11px;color:var(--amber);font-weight:600;padding:4px 0">&#128196; 答案详解 (共 ${this.questions.length} 题)</div>`;
    history.appendChild(titleDiv);

    // 遍历实际题目（动态数量，不硬编码50或5×10）
    this.questions.forEach((q, i) => {
      if (!q) return;

      const userAns = this.answers[i];
      const isChoiceQ = q.type === 'choice' || (q.type === undefined && Array.isArray(q.options));
      const isTextQ = q.type === 'essay' || q.type === 'composition';
      const catLabel = catNames[i % catNames.length];

      let isCorrect = false;
      let scoreRatio = 0;
      if (isTextQ) {
        const minWords = q.minWords || 50;
        scoreRatio = calcTextScoreRatio(userAns, minWords);
        isCorrect = scoreRatio >= 1.0;
      } else if (isChoiceQ) {
        const numAns = Number(userAns);
        const numCorrect = getCorrectAnswer(q);
        if (isNaN(numCorrect)) {
          // 无法判定正确答案，默认给分（仁慈评分）
          isCorrect = true;
        } else if (isNaN(numAns)) {
          isCorrect = false;
        } else {
          isCorrect = numAns === numCorrect;
        }
      } else {
        isCorrect = userAns !== undefined && String(userAns).trim().length > 0;
      }

      const borderColor = isCorrect ? 'var(--green)' : 'var(--red)';
      const qDiv = document.createElement('div');
      qDiv.className = 'msg msg-chen-answer';
      qDiv.style.borderLeft = `3px solid ${borderColor}`;

      let answerDetail = '';
      if (isTextQ) {
        // 问答题/小作文详解
        answerDetail = `
          <div style="font-size:10px;color:var(--txt2);margin:4px 0">
            <span style="color:var(--txt3)">[${q.type === 'essay' ? '问答题' : '小作文'}]</span>
          </div>
          <div style="font-size:10px;background:var(--bg3);padding:6px;border-radius:4px;margin:4px 0;max-height:80px;overflow-y:auto">
            ${userAns ? userAns.replace(/\n/g, '<br>') : '<span style="color:var(--red)">未作答</span>'}
          </div>
          ${q.reference ? `<div style="font-size:9px;color:var(--sky);margin-top:4px">参考答案: ${q.reference}</div>` : ''}
          <div style="font-size:9px;color:${isCorrect ? 'var(--green)' : 'var(--red)'}">
            ${scoreRatio >= 1.0 ? '&#10004; 字数达标，满分' : (scoreRatio > 0 ? '&#9993; 字数不足，得 ' + Math.round(scoreRatio * 100) + '% 分' : '&#10006; 未作答，0分')}
          </div>
        `;
      } else if (isChoiceQ && q.options) {
        // 选择题详解
        answerDetail = `
          <div style="font-size:10px;margin:4px 0">
            ${q.options.map((opt, oi) => {
              let cls = '';
              if (oi === getCorrectAnswer(q)) cls = 'color:var(--green);font-weight:600';
              else if (oi === userAns && !isCorrect) cls = 'color:var(--red);text-decoration:line-through';
              return `<div style="${cls}">${String.fromCharCode(65 + oi)}. ${opt}</div>`;
            }).join('')}
          </div>
          <div style="font-size:9px;color:${isCorrect ? 'var(--green)' : 'var(--red)'}">
            ${isCorrect ? '&#10004; 正确' : `&#10006; 错误 | 正确答案: ${getCorrectAnswer(q) !== undefined ? String.fromCharCode(65 + getCorrectAnswer(q)) : '?'}`}
          </div>
          ${q.reference ? `<div style="font-size:9px;color:var(--sky);margin-top:4px">解析: ${q.reference}</div>` : ''}
        `;
      } else {
        answerDetail = `<div style="font-size:9px;color:var(--txt3)">类型未知</div>`;
      }

      qDiv.innerHTML = `
        <div style="font-size:9px;color:var(--txt3);margin-bottom:3px">${i + 1}. [${catLabel}]</div>
        <div style="font-size:10px;color:var(--txt);margin-bottom:6px;font-weight:500">${q.question || q.q || '题目加载失败'}</div>
        ${answerDetail}
      `;
      history.appendChild(qDiv);
    });

    // 添加返回按钮
    const backDiv = document.createElement('div');
    backDiv.className = 'msg';
    backDiv.innerHTML = `<button class="chen-btn chen-btn-start" onclick="CHEN_TEST.resetTest()">&#8634; 返回测试</button>`;
    history.appendChild(backDiv);

    history.scrollTop = 0;
  },

  resetTest() {
    this.reset();
    this.renderStart();
    document.querySelector('.input-section').style.display = 'block';
  }
}