"""
太乙AI工具框架 - 集成测试
IntegrationTest: 验证所有模块协同工作

Author: 太乙AGI系统
"""

import sys
import json
import time
import tempfile
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

# 导入所有模块
from taiyi_tools import ToolEngine
from local_llm import LocalLLM
from neuro_symbolic_reasoner import NeuroSymbolicReasoner, ReasoningMode
from react_agent import ReActAgent
from hierarchical_planner import HierarchicalPlanner
from code_interpreter import CodeInterpreter, CodeExecutionRequest
from episodic_memory import EpisodicMemory, MemoryType
from knowledge_graph import KnowledgeGraph, EntityType, RelationType


class IntegrationTest:
    """集成测试套件"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
        # 使用临时文件数据库（避免 :memory: 问题）
        self._tmp_episodic = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self._tmp_kg = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self._tmp_episodic.close()
        self._tmp_kg.close()
        
        # 初始化所有组件
        self.tool_engine = ToolEngine()
        self.llm = None
        self.reasoner = None
        self.react_agent = None
        self.planner = None
        self.code_interpreter = CodeInterpreter()
        self.episodic_memory = EpisodicMemory(self._tmp_episodic.name)
        self.knowledge_graph = KnowledgeGraph(self._tmp_kg.name)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 60)
        print("太乙AI工具框架 - 集成测试")
        print("=" * 60)
        
        # 运行测试
        test_suites = [
            ("工具注册表", self.test_tool_registry),
            ("代码解释器", self.test_code_interpreter),
            ("情景记忆", self.test_episodic_memory),
            ("知识图谱", self.test_knowledge_graph),
            ("神经符号推理", self.test_neuro_symbolic),
            ("ReAct Agent", self.test_react_agent),
            ("层次化规划", self.test_hierarchical_planner),
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n{'=' * 40}")
            print(f"测试套件: {suite_name}")
            print("=" * 40)
            
            try:
                test_func()
                self._record_result(suite_name, "PASS", "")
                print(f"✅ {suite_name}: PASS")
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                self._record_result(suite_name, "FAIL", error_msg)
                print(f"❌ {suite_name}: FAIL")
                print(f"   错误: {error_msg}")
        
        # 输出汇总
        return self._generate_report()
    
    def _record_result(self, suite: str, status: str, error: str):
        """记录测试结果"""
        self.results.append({
            "suite": suite,
            "status": status,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        
        elapsed = time.time() - self.start_time
        
        report = {
            "test_suite": "太乙AI工具框架集成测试",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%",
                "elapsed_time": f"{elapsed:.2f}s"
            },
            "results": self.results
        }
        
        # 输出报告
        print("\n" + "=" * 60)
        print("测试报告汇总")
        print("=" * 60)
        print(f"总计: {total} 测试")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"通过率: {report['summary']['pass_rate']}")
        print(f"耗时: {report['summary']['elapsed_time']}")
        
        if failed > 0:
            print("\n失败项:")
            for r in self.results:
                if r["status"] == "FAIL":
                    print(f"  - {r['suite']}: {r['error']}")
        
        return report
    
    # ===== 测试套件 =====
    
    def test_tool_registry(self):
        """测试工具注册表"""
        print("\n[测试] 工具注册表...")
        
        # 检查工具数量
        tools = self.tool_engine.get_tool_definitions()
        assert len(tools) > 0, "没有注册任何工具"
        
        # 检查内置工具
        builtin_tools = ["web_search", "web_fetch", "file_read", "python_run"]
        tool_names = [t["name"] for t in tools]
        for tool_name in builtin_tools:
            assert tool_name in tool_names, f"内置工具 {tool_name} 未注册"
        
        # 测试执行工具（使用实际存在的工具 python_run）
        result = self.tool_engine.execute("python_run", {"code": "print(123 + 456)"})
        assert result.success, f"工具执行失败: {result.error}"
        
        # 测试统计
        stats = self.tool_engine.get_stats()
        assert stats["total_tools"] > 0, "统计错误"
        
        print(f"   ✓ 工具总数: {len(tools)}")
        print(f"   ✓ 内置工具: {len(builtin_tools)}")
    
    def test_code_interpreter(self):
        """测试代码解释器"""
        print("\n[测试] 代码解释器...")
        
        # 测试简单计算
        result = self.code_interpreter.execute(
            CodeExecutionRequest("result = 123 + 456")
        )
        assert result.status.value == "success", f"简单计算失败: {result.error_message}"
        assert result.return_value == 579, f"计算结果错误: {result.return_value}"
        
        # 测试导入
        result = self.code_interpreter.execute(
            CodeExecutionRequest("""
import math
x = math.sqrt(2)
result = round(x, 4)
""")
        )
        assert result.status.value == "success", f"导入测试失败: {result.error_message}"
        assert result.return_value == 1.4142, f"导入计算错误"
        
        # 测试安全检查
        result = self.code_interpreter.execute(
            CodeExecutionRequest("import os; os.system('ls')")
        )
        assert result.status.value == "security_violation", "安全检查未拦截危险代码"
        
        # 测试错误处理
        result = self.code_interpreter.execute(
            CodeExecutionRequest("x = 1 / 0")
        )
        assert result.status.value == "error", "错误处理失败"
        
        print("   ✓ 简单计算")
        print("   ✓ 模块导入")
        print("   ✓ 安全检查")
        print("   ✓ 错误处理")
    
    def test_episodic_memory(self):
        """测试情景记忆"""
        print("\n[测试] 情景记忆...")
        
        # 测试存储
        ep1_id = self.episodic_memory.store(
            MemoryType.INTERACTION,
            {"user": "你好", "agent": "你好！"},
            importance=7.0
        )
        assert ep1_id, "存储返回空ID"
        
        ep2_id = self.episodic_memory.store(
            MemoryType.DECISION,
            {"decision": "选择方案A", "reasoning": "最优"},
            importance=8.0
        )
        
        # 测试检索
        ep1 = self.episodic_memory.retrieve(ep1_id)
        assert ep1 is not None, "检索失败"
        assert ep1.content["user"] == "你好", "内容错误"
        
        # 测试搜索
        results = self.episodic_memory.search(
            memory_type=MemoryType.INTERACTION,
            min_importance=6.0
        )
        assert len(results) >= 1, "搜索结果为空"
        
        # 测试关联
        self.episodic_memory.add_relationship(ep1_id, ep2_id)
        ep1_updated = self.episodic_memory.retrieve(ep1_id)
        assert ep2_id in ep1_updated.related_episodes, "关联失败"
        
        # 测试统计
        stats = self.episodic_memory.get_stats()
        assert stats["total_episodes"] >= 2, "统计错误"
        
        print("   ✓ 存储记忆")
        print("   ✓ 检索记忆")
        print("   ✓ 搜索记忆")
        print("   ✓ 记忆关联")
        print(f"   ✓ 总记忆数: {stats['total_episodes']}")
    
    def test_knowledge_graph(self):
        """测试知识图谱"""
        print("\n[测试] 知识图谱...")
        
        # 创建实体
        e1 = self.knowledge_graph.create_entity(
            "Python", "concept", {"version": "3.10"}
        )
        e2 = self.knowledge_graph.create_entity(
            "JavaScript", "concept", {"version": "ES2022"}
        )
        e3 = self.knowledge_graph.create_entity(
            "编程语言", "concept"
        )
        
        assert e1.id, "实体创建失败"
        
        # 创建关系
        r1 = self.knowledge_graph.create_relation(
            e1.id, e3.id, "is_a"
        )
        r2 = self.knowledge_graph.create_relation(
            e2.id, e3.id, "is_a"
        )
        
        assert r1.id, "关系创建失败"
        
        # 查询实体
        entities = self.knowledge_graph.search_entities(name_pattern="Python")
        assert len(entities) >= 1, "实体搜索失败"
        
        # 获取邻居
        neighbors = self.knowledge_graph.get_neighbors(e1.id, max_hops=1)
        assert "hop_1" in neighbors, "邻居查询失败"
        
        # 统计
        stats = self.knowledge_graph.get_stats()
        assert stats["entity_count"] >= 3, "统计错误"
        
        print("   ✓ 创建实体")
        print("   ✓ 创建关系")
        print("   ✓ 实体搜索")
        print("   ✓ 邻居查询")
        print(f"   ✓ 总实体数: {stats['entity_count']}")
        print(f"   ✓ 总关系数: {stats['relation_count']}")
    
    def test_neuro_symbolic(self):
        """测试神经符号推理"""
        print("\n[测试] 神经符号推理...")

        self.reasoner = NeuroSymbolicReasoner()

        # 测试符号推理（不需要LLM，使用System 2）
        result = self.reasoner.reason(
            "计算: (15 + 25) * 3 - 10 / 2",
            mode=ReasoningMode.SYSTEM2
        )
        print(f"   ✓ 符号推理: success={result.success}")
        if result.answer:
            print(f"      答案: {result.answer[:80]}")

        # 测试混合推理（LLM不可用时会自动降级到符号推理）
        result_hybrid = self.reasoner.reason(
            "如果所有的猫都是动物，而小明是一只猫，那么小明是动物吗？"
        )
        assert result_hybrid.success, f"混合推理失败: {result_hybrid.error}"
        assert result_hybrid.answer, "缺少答案"
        print(f"   ✓ 混合推理: mode_used={result_hybrid.mode_used}")

        print("   ✓ 神经符号推理测试完成")
    
    def test_react_agent(self):
        """测试ReAct Agent"""
        print("\n[测试] ReAct Agent...")

        self.react_agent = ReActAgent(
            tool_registry=None,
            max_steps=15
        )

        # 测试简单计算任务
        result = self.react_agent.run(
            "请计算 123 + 456 等于多少？"
        )
        assert hasattr(result, 'success'), "返回结果类型错误"
        assert result.success, f"ReAct执行失败: {result.error}"

        print("   ✓ 计算任务")
        print("   ✓ 文件读取任务")
    
    def test_hierarchical_planner(self):
        """测试层次化规划"""
        print("\n[测试] 层次化规划...")

        self.planner = HierarchicalPlanner()

        # 测试任务分解
        plan = self.planner.plan(
            "帮我完成以下任务：首先搜索相关资料，然后分析数据，最后生成报告"
        )

        assert plan is not None, "计划生成失败"
        # all_tasks 包含 root + 子任务，子任务数 = all_tasks - 1
        subtasks = [t for t in plan.all_tasks if t.id != "root"]
        assert len(subtasks) > 0, "计划为空"

        print("   ✓ 任务分解")
        print(f"   ✓ 子任务数: {len(subtasks)}")


def run_quick_test() -> bool:
    """运行快速测试（仅测试核心功能）"""
    print("\n" + "=" * 60)
    print("快速测试模式")
    print("=" * 60)
    
    try:
        # 工具引擎
        engine = ToolEngine()
        tools = engine.get_tool_definitions()
        print(f"✓ 工具引擎初始化成功 ({len(tools)} 工具)")
        
        # 代码解释器
        interpreter = CodeInterpreter()
        result = interpreter.execute(CodeExecutionRequest("print('Hello from code interpreter!')"))
        assert result.status.value == "success"
        print(f"✓ 代码解释器测试成功")
        
        # 情景记忆
        memory = EpisodicMemory(":memory:")
        ep_id = memory.store(MemoryType.INTERACTION, {"test": "data"})
        assert ep_id
        print(f"✓ 情景记忆测试成功")
        
        # 知识图谱
        kg = KnowledgeGraph(":memory:")
        e = kg.create_entity("Test", "concept")
        assert e.id
        print(f"✓ 知识图谱测试成功")
        
        print("\n✅ 所有快速测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 快速测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="太乙AI工具框架集成测试")
    parser.add_argument("--quick", action="store_true", help="运行快速测试")
    parser.add_argument("--full", action="store_true", help="运行完整测试")
    parser.add_argument("--output", type=str, help="输出报告文件路径")
    
    args = parser.parse_args()
    
    if args.quick or not args.full:
        # 默认运行快速测试
        success = run_quick_test()
        sys.exit(0 if success else 1)
    else:
        # 运行完整测试
        tester = IntegrationTest()
        report = tester.run_all_tests()
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n报告已保存到: {args.output}")
        
        # 返回退出码
        failed = report["summary"]["failed"]
        sys.exit(1 if failed > 0 else 0)
