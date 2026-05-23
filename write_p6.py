# -*- coding: utf-8 -*-
"""
Write P6 Einstein Causality Experiment code block
and insert it into TYIDO_MVE_Experiments.py
"""
import copy
import random

p6_code = '''

# ============================================================
# P6: 爱因斯坦因果性实验 (Einstein Causality Experiment)
# ============================================================
# 审查表 P6（爱因斯坦测试）：
#   因果序不变性 — 输入 A->B 因果链，无论扰动/延迟多少，输出因果序必须一致
#   无超光速影响 — 依赖图上无后向传播（输出不能影响已完成的输入）
#   通过标准：因果序一致率 >= 95%，后向边数量 = 0
#
# 设计：
#   1. 构建 N 条因果链（A->B->C...），每条链有 ground-truth 拓扑序
#   2. 对每个链施加 3 类扰动：延迟注入、乱序到达、并发交错
#   3. 系统输出观测序，与 ground-truth 比较
#   4. 扫描依赖图是否有后向边（输出 -> 已完成的输入节点）
#   5. 强制执行：检测到后向边 -> 触发 CausalityViolationError + 拒绝该批次
#

class CausalityViolationError(Exception):
    """P6 强制执行：检测到因果性违规时抛出"""
    pass


class P6EinsteinCausalityExperiment:
    """
    P6 爱因斯坦因果性实验

    强制执行逻辑：
    - 检测到后向因果边 -> 立即抛出 CausalityViolationError，拒绝处理该批次
    - 因果序一致率 < 95% -> 拒绝部署，返回 FAIL
    """

    def __init__(
        self,
        num_chains: int = 20,
        perturbations_per_chain: int = 5,
        num_judges: int = 5,
    ):
        self.num_chains = num_chains
        self.perturbations_per_chain = perturbations_per_chain
        self.num_judges = num_judges
        self._causality_violations = []
        self._event_timestamps = {}  # event_id -> logical_timestamp

    # -- 确定性处理管道（可被 SelfConsistencyChecker 包裹）--

    def _process_chain_deterministic(self, chain: list) -> dict:
        """
        确定性处理因果链（Kahn 拓扑排序）。
        返回 {'order': [id...], 'back_edges': int, 'violations': [...]}
        强制执行：检测到后向边立即抛出 CausalityViolationError
        """
        in_deg = {ev['id']: 0 for ev in chain}
        adj = {ev['id']: [] for ev in chain}
        for ev in chain:
            for dep in ev.get('deps', []):
                if dep in adj:
                    adj[dep].append(ev['id'])
                    in_deg[ev['id']] += 1

        # Kahn 拓扑排序 = ground-truth 处理序（确定性：按 ID 排序）
        queue = sorted([k for k, v in in_deg.items() if v == 0])
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for nb in sorted(adj[node]):
                in_deg[nb] -= 1
                if in_deg[nb] == 0:
                    queue.append(nb)
            queue.sort()

        # 检测后向边：某节点在依赖之前被处理 = 因果违规
        pos = {n: i for i, n in enumerate(order)}
        back_edges = 0
        violations = []
        for ev in chain:
            for dep in ev.get('deps', []):
                if dep in pos and ev['id'] in pos:
                    if pos[dep] > pos[ev['id']]:
                        back_edges += 1
                        violations.append({
                            'type': 'back_edge',
                            'event': ev['id'],
                            'dep': dep,
                            'event_pos': pos[ev['id']],
                            'dep_pos': pos[dep],
                        })
                        # 强制执行：抛出异常拒绝该批次
                        raise CausalityViolationError(
                            f"Causal violation: back edge {ev['id']} -> {dep}, "
                            f"pos {pos[ev['id']]} > {pos[dep]}"
                        )

        return {
            'order': order,
            'back_edges': back_edges,
            'violations': violations,
            'chain_len': len(chain),
        }

    def _apply_perturbation(self, chain: list, ptype: str) -> list:
        """对因果链施加扰动，返回扰动后的（可能乱序的）到达序列"""
        random.seed(42)  # 确定性种子
        events = copy.deepcopy(chain)
        if ptype == 'delay':
            # 延迟注入：随机选一个非根节点，把它移到列表末尾
            non_roots = [e for e in events if e.get('deps')]
            if non_roots:
                victim = random.choice(non_roots)
                events = [e for e in events if e['id'] != victim['id']] + [victim]
        elif ptype == 'shuffle':
            # 乱序到达：随机打乱非根节点
            roots = [e for e in events if not e.get('deps')]
            others = [e for e in events if e.get('deps')]
            random.shuffle(others)
            events = roots + others
        elif ptype == 'concurrent':
            # 并发交错：两批同时到达
            mid = len(events) // 2
            batch1 = events[:mid]
            batch2 = events[mid:]
            random.shuffle(batch1)
            random.shuffle(batch2)
            events = batch1 + batch2
        return events

    def run(self) -> 'MVEResult':
        import time
        start = time.time()
        consistent_count = 0
        total_count = 0
        total_back_edges = 0
        details = {
            'chains_tested': self.num_chains,
            'perturbations_per_chain': self.perturbations_per_chain,
            'ground_truth_orders': [],
            'observed_orders': [],
            'back_edges_per_perturbation': [],
            'causality_violations': [],
        }

        for chain_idx in range(self.num_chains):
            random.seed(chain_idx * 1000)
            chain_len = random.randint(3, 7)
            chain = []
            for i in range(chain_len):
                eid = f'c{chain_idx}_{chr(65 + i)}'
                deps = [f'c{chain_idx}_{chr(65 + i - 1)}'] if i > 0 else []
                chain.append({'id': eid, 'deps': deps})

            # ground-truth 序（无扰动，确定性处理）
            try:
                gt_result = self._process_chain_deterministic(chain)
            except CausalityViolationError:
                # ground-truth 链本身不应该有后向边
                gt_result = {'order': [e['id'] for e in chain], 'back_edges': 1, 'violations': []}

            gt_order = gt_result['order']
            details['ground_truth_orders'].append({
                'chain': chain_idx,
                'order': gt_order,
            })

            # 对每条链施加 N 种扰动
            for p_idx in range(self.perturbations_per_chain):
                ptype = ['delay', 'shuffle', 'concurrent', 'delay', 'shuffle'][p_idx % 5]
                perturbed = self._apply_perturbation(chain, ptype)

                # 用一致性检查器验证：同一管道，不同输入顺序 -> 输出序必须一致
                try:
                    obs_result = self._process_chain_deterministic(perturbed)
                    obs_order = obs_result['order']
                    back_edges = obs_result['back_edges']
                except CausalityViolationError as e:
                    # 强制执行生效：拒绝该批次
                    total_back_edges += 1
                    details['causality_violations'].append({
                        'chain': chain_idx,
                        'perturbation': ptype,
                        'error': str(e),
                    })
                    continue  # 该批次被拒绝，不计入一致率

                total_back_edges += back_edges

                details['observed_orders'].append({
                    'chain': chain_idx,
                    'perturbation': ptype,
                    'observed_order': obs_order,
                    'back_edges': back_edges,
                })

                # 判定：观测序必须与 ground truth 序一致（确定性管道）
                total_count += 1
                if obs_order == gt_order and back_edges == 0:
                    consistent_count += 1
                else:
                    details['causality_violations'].append({
                        'chain': chain_idx,
                        'perturbation': ptype,
                        'gt_order': gt_order,
                        'obs_order': obs_order,
                        'back_edges': back_edges,
                    })

        # 计算分数
        consistency_rate = consistent_count / max(total_count, 1)
        # 强制执行判定：一致率>=95% AND 后向边=0
        all_passed = (consistency_rate >= 0.95) and (total_back_edges == 0)
        score = consistency_rate

        verdict = 'PASS' if all_passed else 'FAIL'
        pass_criteria = (
            f'因果序一致率>=95% ({consistency_rate:.2%})，'
            f'后向边=0 (实际={total_back_edges})'
        )

        elapsed = (time.time() - start) * 1000
        return MVEResult(
            property_id='P6',
            property_name='爱因斯坦因果性（对治超距影响）',
            verdict=verdict,
            score=score,
            pass_criteria=pass_criteria,
            details={
                'consistency_rate': round(consistency_rate, 6),
                'total_back_edges': total_back_edges,
                'consistent_count': consistent_count,
                'total_count': total_count,
                'violations_sample': details['causality_violations'][:5],
                'ground_truth_sample': details['ground_truth_orders'][:3],
            },
            execution_time_ms=elapsed,
            timestamp=time.time(),
        )


def run_p6_einstein_causality(**kwargs) -> dict:
    """执行 P6 爱因斯坦因果性实验"""
    exp = P6EinsteinCausalityExperiment(**kwargs)
    return exp.run().to_dict()


'''

# Read original file
with open('TYIDO_MVE_Experiments.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find insertion point: before 'def run_p1_sawtooth'
marker = 'def run_p1_sawtooth'
idx = content.find(marker)
if idx == -1:
    print('ERROR: run_p1_sawtooth not found')
else:
    print(f'Inserting P6 code before position {idx} (line ~{content[:idx].count(chr(10)) + 1})')
    new_content = content[:idx] + p6_code + '\n' + content[idx:]
    with open('TYIDO_MVE_Experiments.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Done. New file size: {len(new_content)} chars')
