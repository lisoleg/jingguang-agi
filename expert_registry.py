"""
expert_registry.py — 215位AI专家注册表
解析 agency-agents-zh/ 目录下的 .md 文件，提取专家人格数据，
供太乙AGI系统在聊天时注入专家System Prompt。

数据来源: https://github.com/jnMetaCode/agency-agents-zh
  215个专家 (agency-agents 原版165个 + 50个中国本土化专家)
"""

from __future__ import annotations

import os
import re
import json
import threading
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path

# ─────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────

@dataclass
class ExpertConfig:
    """单个专家的完整配置"""
    id: str                     # 文件基名，如 "academic-anthropologist"
    name: str                    # YAML frontmatter 中的 name
    description: str             # YAML frontmatter 中的 description
    emoji: str                   # YAML frontmatter 中的 emoji
    color: str                   # YAML frontmatter 中的 color (hex字符串)
    department: str              # 所属部门目录名，如 "academic"
    system_prompt: str           # 将整个 .md 文件内容转为 system prompt
    file_path: str               # 原始 .md 文件路径
    tags: List[str] = field(default_factory=list)   # 搜索标签（name + description 分词）

    def to_dict(self) -> Dict[str, Any]:
        """序列化为API响应字典（不含 system_prompt 全文以节省带宽）"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "emoji": self.emoji,
            "color": self.color,
            "department": self.department,
            "tags": self.tags,
            "file_path": self.file_path,
        }

    def to_detail_dict(self) -> Dict[str, Any]:
        """完整序列化（含 system_prompt）"""
        d = self.to_dict()
        d["system_prompt"] = self.system_prompt
        return d


# ─────────────────────────────────────────────
# YAML Frontmatter 解析
# ─────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _parse_frontmatter(text: str) -> Dict[str, str]:
    """
    解析 Markdown YAML frontmatter (--- 分隔)。
    返回 {key: value} 字典，未找到时返回空字典。
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def _extract_system_prompt(md_text: str) -> str:
    """
    将整个 .md 文件转换为适合作为 system prompt 的文本。
    保留 YAML frontmatter 中的 name/description/emoji 作为身份声明，
    正文 Markdown 直接作为人格描述。
    """
    # 去掉 frontmatter 标记，保留内容
    # 策略：整个文件作为 system prompt，但在最前面加一句身份说明
    fm = _parse_frontmatter(md_text)
    name = fm.get("name", "专家")
    emoji = fm.get("emoji", "🤖")
    desc = fm.get("description", "")
    lines = [
        f"你是一位AI专家，名为「{name}」{emoji}。",
        f"专业领域：{desc}",
        "",
        "以下是你的完整人格设定和行为准则：",
        "---",
        "",
    ]
    # 去掉 ---frontmatter--- 标记后附加正文
    body = _FRONTMATTER_RE.sub("", md_text).strip()
    lines.append(body)
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 核心注册表类
# ─────────────────────────────────────────────

class ExpertRegistry:
    """
    215位专家注册表，单例模式，线程安全。
    启动时扫描 agency-agents-zh/ 目录，解析所有 .md 文件。
    """

    _instance: Optional[ExpertRegistry] = None
    _lock = threading.Lock()

    def __init__(self, base_dir: str = "agency-agents-zh"):
        self.base_dir = base_dir
        self._experts: Dict[str, ExpertConfig] = {}
        self._by_department: Dict[str, List[ExpertConfig]] = {}
        self._loaded = False

    @classmethod
    def instance(cls, base_dir: str = "agency-agents-zh") -> ExpertRegistry:
        """单例访问"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(base_dir)
        return cls._instance

    def load_all(self, force: bool = False) -> int:
        """
        扫描 base_dir 下所有子目录的 .md 文件，解析并注册。
        返回加载的专家数量。
        """
        if self._loaded and not force:
            return len(self._experts)

        base = Path(self.base_dir)
        if not base.is_dir():
            raise FileNotFoundError(f"专家目录不存在: {self.base_dir}")

        count = 0
        for md_file in base.rglob("*.md"):
            # 跳过文档文件
            if md_file.name.upper() in (
                "README.md", "README.ZH-TW.md", "CONTRIBUTING.md",
                "CATALOG.md", "AGENT-LIST.md", "LICENSE", "UPSTREAM.md",
            ):
                continue
            # 跳过 .github/ 目录
            if ".github" in md_file.parts:
                continue
            try:
                expert = self._parse_file(md_file)
                if expert:
                    self._register(expert)
                    count += 1
            except Exception as e:
                print(f"[ExpertRegistry] 跳过文件 {md_file}: {e}")

        self._loaded = True
        print(f"[ExpertRegistry] 加载完成: {count} 位专家")
        return count

    def _parse_file(self, md_file: Path) -> Optional[ExpertConfig]:
        """解析单个 .md 文件，返回 ExpertConfig 或 None"""
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()

        fm = _parse_frontmatter(text)
        if not fm:
            return None  # 无 frontmatter，跳过

        department = md_file.parent.name  # 部门 = 所在子目录名
        expert_id = md_file.stem         # 文件名（不含扩展名）作为 ID

        name = fm.get("name", md_file.stem)
        description = fm.get("description", "")
        emoji = fm.get("emoji", "🤖")
        color = fm.get("color", "#6366F1")

        system_prompt = _extract_system_prompt(text)

        # 搜索标签：name + description 分词
        tags = self._make_tags(name, description, department)

        return ExpertConfig(
            id=expert_id,
            name=name,
            description=description,
            emoji=emoji,
            color=color,
            department=department,
            system_prompt=system_prompt,
            file_path=str(md_file),
            tags=tags,
        )

    def _make_tags(self, name: str, description: str, department: str) -> List[str]:
        """生成搜索标签列表"""
        text = f"{name} {description} {department}"
        # 简单中文+英文分词：按空格/标点/·/·分割后去重
        tokens = re.findall(r"[\w\u4e00-\u9fff·]+", text.lower())
        return list(dict.fromkeys(tokens).keys())  # 保序去重

    def _register(self, expert: ExpertConfig):
        """注册单个专家"""
        self._experts[expert.id] = expert
        if expert.department not in self._by_department:
            self._by_department[expert.department] = []
        self._by_department[expert.department].append(expert)

    # ── 查询 API ─────────────────────────────────────────────

    def get_expert(self, expert_id: str) -> Optional[ExpertConfig]:
        """按 ID 获取专家详情（含 system_prompt）"""
        return self._experts.get(expert_id)

    def list_experts(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有专家摘要（不含 system_prompt 全文）。
        department: 按部门过滤（可选）
        """
        if department:
            experts = self._by_department.get(department, [])
        else:
            experts = list(self._experts.values())
        return [e.to_dict() for e in experts]

    def list_departments(self) -> Dict[str, int]:
        """列出所有部门及专家数量"""
        return {dept: len(exps) for dept, exps in self._by_department.items()}

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        全文搜索专家（在 name/description/tags 中匹配）。
        返回匹配的前 `limit` 个专家摘要。
        """
        q = query.lower().replace(" ", "")
        scored: List[tuple] = []
        for expert in self._experts.values():
            score = 0
            # name 匹配（权重最高）
            if q in expert.name.lower():
                score += 10
            # description 匹配
            if q in expert.description.lower():
                score += 5
            # tags 匹配
            for tag in expert.tags:
                if q in tag.lower():
                    score += 3
                    break
            # department 匹配
            if q in expert.department.lower():
                score += 2
            if score > 0:
                scored.append((score, expert))
        # 按分数降序排列
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e.to_dict() for _, e in scored[:limit]]

    def get_system_prompt(self, expert_id: str) -> Optional[str]:
        """获取指定专家的完整 system prompt（用于注入聊天）"""
        expert = self._experts.get(expert_id)
        return expert.system_prompt if expert else None

    @property
    def count(self) -> int:
        return len(self._experts)


# ─────────────────────────────────────────────
# 模块级便捷函数（推荐使用）
# ─────────────────────────────────────────────

_registry: Optional[ExpertRegistry] = None
_registry_lock = threading.Lock()


def get_registry(base_dir: str = "agency-agents-zh") -> ExpertRegistry:
    """获取全局 ExpertRegistry 单例，首次调用时自动 load_all()"""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = ExpertRegistry.instance(base_dir)
                _registry.load_all()
    return _registry


def refresh_registry(base_dir: str = "agency-agents-zh") -> ExpertRegistry:
    """强制重新加载（开发时用）"""
    global _registry
    with _registry_lock:
        _registry = ExpertRegistry.instance(base_dir)
        _registry.load_all(force=True)
    return _registry


# ─────────────────────────────────────────────
# CLI 测试入口
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    registry = get_registry()
    print(f"总计加载专家: {registry.count}")
    print(f"部门分布: {registry.list_departments()}")
    print()
    # 展示前3个专家
    for dept, experts in registry._by_department.items():
        print(f"[{dept}] {experts[0].name} ({experts[0].emoji}) — {experts[0].description[:50]}...")
        if len(experts) > 1:
            print(f"  ... 还有 {len(experts)-1} 位专家")
        print()
    # 搜索测试
    print("搜索测试: '写作'")
    results = registry.search("写作")
    for r in results[:3]:
        print(f"  - {r['name']} ({r['department']})")
