# 太乙AGI 5.0.0 升级指南

## 版本信息
- 旧版本：v4.2.0（29个模块）
- 新版本：v5.0.0（33个模块）

## 新增模块（30-33）

| 编号 | 模块名称 | 文件 | 核心功能 |
|------|----------|------|----------|
| 30 | 分形全息场 | FractalHolismField.py | 跨尺度自相似性、IBL边界层控制 |
| 31 | CTM相位同步器 | CTMPhaseSynchronizer.py | 连续思维机器、世界帧Tick |
| 32 | 零信任治理 | ZeroTrustGovernance.py | PEP/PDP/PAP三组件、RBAC |
| 33 | 虹光身存算 | RainbowBodyCompute.py | 存储即计算、阿卡西不可变日志 |

## 升级步骤

### 方法1：直接使用新文件
1. 新文件 `CompositeAGI_V5.py` 已创建
2. 运行测试：`python test_v5_modules.py`
3. 启动服务：`python app.py`

### 方法2：手动升级现有文件
在 `CompositeAGI_V2.py` 中添加以下内容：

1. **在文件开头的import区域添加**（约第247行后）：
```python
# 新增模块30-33（基于4篇新论文）
try:
    from FractalHolismField import FractalHolismField, HolonScale
except:
    FractalHolismField = None

try:
    from CTMPhaseSynchronizer import CTMPhaseSynchronizer, WorldFrameTick
except:
    CTMPhaseSynchronizer = None

try:
    from ZeroTrustGovernance import ZeroTrustGovernance, TrustLevel
except:
    ZeroTrustGovernance = None

try:
    from RainbowBodyCompute import RainbowBodyCompute, DataState
except:
    RainbowBodyCompute = None
```

2. **修改版本号**（约第281行）：
```python
self.version = "5.0.0"  # 升级到5.0.0（新增4个模块）
```

3. **在 `_initialize_modules` 方法末尾添加**（约第575行后）：
```python
# 模块30: 分形全息场 ⭐ 新增
if FractalHolismField:
    self.fractal_holism = FractalHolismField()
    print("  ✓ 分形全息场已加载")

# 模块31: CTM相位同步器 ⭐ 新增
if CTMPhaseSynchronizer:
    self.ctm_sync = CTMPhaseSynchronizer()
    print("  ✓ CTM相位同步器已加载")

# 模块32: 零信任治理 ⭐ 新增
if ZeroTrustGovernance:
    self.zero_trust = ZeroTrustGovernance()
    print("  ✓ 零信任治理已加载")

# 模块33: 虹光身存算 ⭐ 新增
if RainbowBodyCompute:
    self.rainbow_body = RainbowBodyCompute()
    print("  ✓ 虹光身存算已加载")
```

4. **添加处理方法**（在文件末尾的 `process_query` 方法中添加）：
```python
# 模块30: 分形全息场
if self.fractal_holism:
    fractal_result = self.fractal_holism.process(query)
    result['module_results']['fractal_holism'] = fractal_result

# 模块31: CTM相位同步器
if self.ctm_sync:
    ctm_result = self.ctm_sync.process(query)
    result['module_results']['ctm_sync'] = ctm_result

# 模块32: 零信任治理
if self.zero_trust:
    zt_result = self.zero_trust.process(query)
    result['module_results']['zero_trust'] = zt_result

# 模块33: 虹光身存算
if self.rainbow_body:
    rb_result = self.rainbow_body.process(query)
    result['module_results']['rainbow_body'] = rb_result
```

## 验证升级

运行测试脚本验证：
```bash
python test_v5_modules.py
```

预期输出：
```
============================================================
太乙AGI 5.0 - 4个新模块测试
============================================================
[30] 分形全息场: 指数=0.844, 阴阳=0.409
[31] CTM相位同步: 指数=0.423, Ticks=3
[32] 零信任治理: 决策=deny, 信任=0.6
[33] 虹光身存算: 指数=0.498, 阿卡西=full
============================================================
所有4个新模块测试通过!
============================================================
```

## 技术支持

如有问题，请检查：
1. 所有模块文件是否存在
2. Python版本是否为3.8+
3. 所有依赖包是否已安装
