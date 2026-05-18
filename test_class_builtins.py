#!/usr/bin/env python3
"""测试类方法中__builtins__的行为"""

class TestClass:
    def method1(self):
        print('In method1:')
        print('__builtins__ type:', type(__builtins__))
        print('len(dir(__builtins__)):', len(dir(__builtins__)))
    
    def method2(self):
        # 访问全局的__builtins__
        import builtins
        print('In method2:')
        print('builtins.__builtins__ type:', type(builtins.__builtins__))
        print('len(dir(builtins.__builtins__)):', len(dir(builtins.__builtins__)))

obj = TestClass()
print('Calling method1...')
obj.method1()
print()
print('Calling method2...')
obj.method2()
