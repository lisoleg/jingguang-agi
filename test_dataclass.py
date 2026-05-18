#!/usr/bin/env python3
"""测试@dataclass对__builtins__的影响"""
print(f"Before dataclass: __builtins__ type = {type(__builtins__)}")

from dataclasses import dataclass, field

print(f"After dataclass import: __builtins__ type = {type(__builtins__)}")

@dataclass
class TestClass:
    name: str = "test"

print(f"After @dataclass: __builtins__ type = {type(__builtins__)}")
