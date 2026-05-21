# 长期记忆

## 项目概览
**净光哥** 太乙AGI：Flask应用，位于 `C:\Users\1\WorkBuddy\2026-05-06-task-1\`
- 主服务器: `app.py` (Flask, 端口5001)
- 前端: `static/index_agi12.html` (三栏布局界面)
- 脑图: `app_mindmap_v2.py` (端口5003)

## 当前版本：v7.10（🔄开发中）
- **v7.10**: M134-M137 + T96-T99 + 4面板（欧拉相位闭合·递归证明折叠·五层次本体·可证伪预言）
  - 来源论文：《论关系实在的终极压缩》（章锋）— 欧拉恒等式相位闭合 + zk-SNARK递归证明折叠 + L1-L5五层次本体 + 可证伪预言框架
- **v7.9**: M130-M133 + T92-T95 ✅（金符离散微积分·关系作用量·堆垒素数·自指闭环拓扑）
- **v7.8**: M126-M129 + T86-T91 ✅（护栏编排·推测推理·KV治理·本体自锻造）
- **v7.7**: M120-M125 + T79-T85 ✅（博弈论推理·ICPS社会能力·情绪粒度·沙盒探索）
- **v7.6**: M117-M119 + T75-T77 ✅（Ftel目的约束·认知递归动力学·层间保真度）
- **v7.5**: M114-M116 + T72-T74 ✅（HoTT截面搜索）
- **v7.4**: M111-M113 + T66-T71 ✅（演员-导演复合体+流贯截断+痕迹验证）
- **v7.3**: M106-M110 + T59-T65 + T78 ✅
- **v7.1**: M96-M105 + T41-T51 ✅
- **v7.2**: M81-M87 + T52-T58 ✅
- **v7.0**: M71-M95 + T23-T40 ✅

## 模块编号规则
- M1-M95: v5.0-v7.0 | M96-M105: v7.1 | M106-M110: v7.3 | M111-M113: v7.4
- M114-M116: v7.5 | M117-M119: v7.6 | M120-M125: v7.7 | M126-M129: v7.8
- M130-M133: v7.9 | M134-M137: v7.10

## 定理编号规则
- T1-T7: 核心 | T8-T16: v6.1 | T17-T22: v6.2 | T23-T40: v7.0
- T41-T51: v7.1 | T52-T58: v7.2 | T59-T65: v7.3 | T66-T71: v7.4
- T72-T74: v7.5 | T75-T77: v7.6 | T78: M106升级 | T79-T85: v7.7
- T86-T91: v7.8 | T92-T95: v7.9 | T96-T99: v7.10

## API版本模式
- `/api/v710/*`: v7.10 API（M134-M137）
- `/api/v79/*`: v7.9 | `/api/v78/*`: v7.8 | `/api/v77/*`: v7.7 | `/api/v76/*`: v7.6
- `/api/v75/*`: v7.5 | `/api/v74/*`: v7.4 | `/api/v73/*`: v7.3 | `/api/v71/*`: v7.1
- `/api/chat_v2`: 主对话 | `/api/goal`: 目标模式

## 核心模块文件
- `CompositeAGI_V2.py`: 主核心（v5.0+）
- `HolographicDiscreteGovernance.py`: M29 全息离散治理
- `agi_medium_symbiosis.py`: 介质共生
- `M56-M62_*.py`: v6.2 | `M71-M80_*.py`: v7.0 | `M81-M95_*.py`: v7.0 Phase2
- `M106-M110_*.py`: v7.3 | `M120-M125_*.py`: v7.7 | `M126-M129_*.py`: v7.8
- `M130-M133_*.py`: v7.9 | `M134-M137_*.py`: v7.10

## 重要Bug记录（精简）
- `_to_native` float转换：需检查imag!=0
- app.run()阻塞：路由必须在app.run()之前定义
- 模块/定理编号冲突：M88+被占用从M111开始，T59+被占用从T66开始
- 工程师模块缺get_instance()：需手动添加模块级单例
- 多进程占端口：用taskkill //PID //F逐个杀掉
- M133 compute_self_ref_penalty返回float非dict：已知不一致
- M106 Φ值精度低：sigmoid软激活+Laplace平滑修复
- Python 3.10不支持f-string内反斜杠

## v7.10模块与现有模块整合（预定）
- M134 EulerPhaseClosure: 与M130(金符phase)和M133(自指闭环)桥接
- M135 RecursiveProofFolder: 与M81(记忆树)和M128(KV治理)整合
- M136 FiveLayerOntology: L1→M117 Ftel, L2→M130金符, L3→M112截断, L4→M123 ICPS, L5→M62叙事
- M137 FalsifiablePrediction: 通用预言框架，支持任意定理生成预言

## 服务启动
```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1 && python app.py
# 访问 http://127.0.0.1:5001/static/index_agi12.html
```
