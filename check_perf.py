from task_interface import TextProcessor
import time

p = TextProcessor()
texts = [
    "你好，我是AGI系统",
    "这个产品太棒了，我很喜欢",
    "今天天气不好，心情差",
    "请问现在几点了"
]

total_time = 0
for t in texts:
    start = time.time()
    result = p.process(t)
    end = time.time()
    elapsed = (end - start) * 1000  # ms
    total_time += elapsed
    print(f"Text: {t[:20]}... Time: {elapsed:.2f}ms")

avg_time = total_time / len(texts)
print(f"\nAverage inference time: {avg_time:.2f}ms")
print(f"Meets <100ms requirement: {avg_time < 100}")
