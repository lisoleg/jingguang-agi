#!/usr/bin/env python3
"""测试__builtins__类型"""
import sys

def check_builtins():
    print('__builtins__ type:', type(__builtins__))
    if isinstance(__builtins__, dict):
        print('__builtins__ keys:', list(__builtins__.keys())[:10])
        print('print in __builtins__:', 'print' in __builtins__)
    else:
        print('__builtins__ is a module')
        print('print in module:', hasattr(__builtins__, 'print'))

if __name__ == "__main__":
    check_builtins()
