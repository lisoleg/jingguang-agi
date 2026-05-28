import time
from task_interface import TextProcessor

# 初始化（包含训练）
start = time.time()
processor = TextProcessor()
init_time = time.time() - start
print(f"初始化时间: {init_time:.2f}s")

# 推理测试
test_texts = [
    "我今天很开心",
    "这个产品太糟糕了",
    "你好，请问现在是几点"
]

for text in test_texts:
    start = time.time()
    result = processor.process(text)
    elapsed = (time.time() - start) * 1000
    print(f"文本: {text[:20]}... 时间: {elapsed:.2f}ms 情感: {result.get('sentiment')}")
    assert elapsed < 100, f"推理时间超过100ms: {elapsed:.2f}ms"
print("所有推理时间测试通过")
