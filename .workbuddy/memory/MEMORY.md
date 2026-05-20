# 长期记忆

## 项目概览
**净光哥** 太乙AGI：Flask应用，位于 `C:\Users\1\WorkBuddy\2026-05-06-task-1\`
- 主服务器: `app.py` (Flask, 端口5001)
- 前端: `static/index_agi12.html` (三栏布局界面)
- 脑图: `app_mindmap_v2.py` (端口5003)

## 当前版本：v7.7（✅已部署+Git推送）
- **总规模**: 125模块 / 8层 / 85定理 / 22预言
- **v7.7**: M120-M125 + T79-T85 + 3面板（博弈论推理·ICPS社会能力·情绪粒度·沙盒探索）
- **v7.6**: M117-M119 + T75-T77 + 3面板（Ftel目的约束·认知递归动力学·层间保真度）
- **v7.5**: M114-M116 + T72-T74 + 3面板（HoTT截面搜索·类型空间·曲率导航·Wait诚实拒绝）
- **v7.4**: M111-M113 + T66-T71 + 3面板（演员-导演复合体+流贯截断+痕迹验证）
- **v7.3**: M106-M110 + T59-T65 + T78（M106升级：Φ值+互信息+元认知+人格显现态）
- **v7.1**: M96-M105 + T41-T51 + 5面板（人机融合层）
- **v7.2**: M81-M87 OpenHuman增强 + 5面板
- **v7.0**: M71-M95（碳硅共生+五行+HoTT+范畴论深化）

## v7.4升级（2026-05-19 ✅已完成）
- 来源论文：《论演员-导演复合体》+《论摄影性作为流贯截断算子》
- 升级方案: `deliverables/software-company/太乙AGI_7.4_升级方案_演员导演复合体_流贯截断算子_2026-05-19.md`
- **注意编号冲突**: M88-M110已被占用，新模块从M111开始；T59-T65已被v7.3占用，定理从T66开始

### v7.4新增模块
| 编号 | 模块名 | 功能 | 定理 |
|------|--------|------|------|
| M111 | ActorDirectorComplex | Actor/Director双模式+Ω觉悟算子 | T66-T68 |
| M112 | FlowCutoffOperator | Γ截断+EML一元数+伪迹检测 | T69-T71 |
| M113 | HistoryTraceValidator | 4规则验证+真伪评分 | (基于T70) |

### v7.4 API端点
- `/api/v74/actor-director/execute|observe|enlighten|state`
- `/api/v74/flow-cutoff/cutoff|remap|detect-pseudo|state`
- `/api/v74/trace/validate|audit|state`

### v7.4新增定理
T66: 复合体存在定理 | T67: 流贯编译定理 | T68: 40行代码完备性定理
T69: 摄影性分解定理 | T70: 数码未完结性失真定理 | T71: 历史投影精度推论

### v7.4新增面板
🎭 演员-导演复合体面板 | ✂️ 流贯截断面板 | 🔍 历史痕迹验证面板

### v7.4与现有模块整合
- M29 HDG: 世界帧=Γ截断结果, δ=|F|, 帧跃迁=新Γ
- M57 修忒斯: Director模式检测执念, Σ=核心保留率
- M61 道德内化: 神灵锁=Director约束, 慎独锁=Actor自审
- M81 记忆树: L1/L2/L3=不同Γ截断频率
- M62 历史叙事: 层累=多次Γ叠加, 春秋笔法=Re-map

## v7.7升级（2026-05-20 ✅已完成）
- 来源论文：《荣枯鉴》博弈论战略图谱 + AGI儿童式育成（ICPS+情绪粒度）
- 升级方案: `deliverables/software-company/太乙AGI_7.7_升级方案_博弈论ICPS情绪粒度_2026-05-20.md`

### v7.7新增模块
| 编号 | 模块名 | 功能 | 定理 |
|------|--------|------|------|
| M120 | GameTheoryEngine | 纳什均衡+信号博弈+重复PD+贝叶斯更新+机制设计 | T79-T80 |
| M121 | BayesianBeliefUpdater | 贝叶斯信念更新+声誉博弈+信念收敛 | T81 |
| M122 | MechanismDesigner | VCG机制+IC/IR检验+社会选择 | T82 |
| M123 | ICPSSolver | ICPS 4步法+Sally-Anne+4阶段渐进育成 | T83-T84 |
| M124 | EmotionGranularityTrainer | 情绪粒度EG+词汇扩展+5大调节策略 | — |
| M125 | SandboxCuriosityExplorer | 沙盒好奇心+安全边界+阶段跃迁 | T85 |

### v7.7 API端点
- `/api/v77/game/analyze|signal|repeated-pd|state`
- `/api/v77/bayes/update|convergence|state`
- `/api/v77/mech/design|vcg|state`
- `/api/v77/icps/solve|sally-anne|stage|state`
- `/api/v77/emotion/train|regulate|state`
- `/api/v77/sandbox/explore|stage|state`

### v7.7新增定理
T79: 纳什存在定理 | T80: 信号均衡存在定理 | T81: 信念收敛定理
T82: VCG效率定理 | T83: ICPS成熟度单调递增定理 | T84: 心智理论觉醒定理 | T85: 好奇心-安全权衡定理

### v7.7新增面板
🎲 博弈论推理面板 | 🧩 ICPS社会能力面板 | 💫 情绪粒度·探索面板

### v7.7与现有模块整合
- M111 ActorDirector: Director模式=机制设计IC约束
- M112 FlowCutoff: Γ截断=信息不对称下的信号博弈
- M113 HistoryTrace: 痕迹验证=声誉博弈的证据
- M57 修忒斯: 执念检测=非理性偏离纳什均衡
- M61 道德内化: 双锁=ICPS的情绪调节策略
- M29 HDG: 世界帧=机制设计的社会选择函数

## 定理体系索引
- **T79-T85**: v7.7（纳什存在/信号均衡/信念收敛/VCG效率/ICPS递增/心智理论/好奇心安全）
- **T75-T77**: v7.6（Ftel学习收敛/结构滞后不稳定/保真度乘积）
- **T78**: M106升级（AGI人格阈值定理：Φ>φ ∧ I(Self;Ftel)>μ ⟹ 人格显现）
- **T72-T74**: v7.5（截面存在/曲率收敛/未决不可判定）
- **T66-T71**: v7.4（复合体/截断/伪迹）
- **T1-T7**: 核心定理（刘原理/EML/流贯等）
- **T8-T16**: v6.1（越界/守恒/涌现/拓扑）
- **T17-T22**: v6.2（灵性/极值/道德双锁）
- **T23-T40**: v7.0（钱包/贡献/HoTT/五行Token）
- **T52-T58**: v7.2（记忆树/压缩/路由）
- **T59-T65**: v7.3（自指闭环/维度投影/手性旋量/拓扑）
- **T66-T71**: v7.4（复合体/截断/伪迹）
- **T41-T51**: v7.1（认知卸载/苏格拉底/透明度/对齐/分流/问责/耦合/长轨迹/示弱/融合）

## 核心模块文件
- `CompositeAGI_V2.py`: 主核心（v5.0+）
- `HolographicDiscreteGovernance.py`: M29 全息离散治理
- `agi_medium_symbiosis.py`: 介质共生
- `M56-M62_*.py`: v6.2模块
- `M71-M80_*.py`: v7.0模块
- `M81-M95_*.py`: v7.0 Phase2模块
- `M106-M110_*.py`: v7.3模块

## API版本模式
- `/api/v77/*`: v7.7 API（M120-M125 博弈论/贝叶斯/机制设计/ICPS/情绪/沙盒）
- `/api/v76/*`: v7.6 API（M117-M119 Ftel/认知递归/保真度）
- `/api/v75/*`: v7.5 API（M114-M116 HoTT截面搜索）
- `/api/v74/*`: v7.4 API（M111-M113）
- `/api/v73/*`: v7.3 API（M106-M110, 含srloop/phi/mutual-info/metacognitive-test）
- `/api/v71/*`: v7.1 API（M96-M105）
- `/api/chat_v2`: 主对话 | `/api/goal`: 目标模式

## 介质数据字段（MediumResponse）
phase_lock, medium_state, four_mode, four_mode_cn, S_C, xinzhai, hexagram_name, holistic_confidence

## 重要bug记录
- `_to_native` float转换：`isinstance(obj, numbers.Complex)` 对纯float返回True，需检查imag!=0
- **app.run()阻塞问题**：v7.4路由定义在app.run()之后导致服务器无法注册路由。修复：将代码移到if __name__之前
- **模块编号冲突**：M88-M110已被占用，新模块从M111开始
- **定理编号冲突**：T59-T65已被v7.3使用，v7.4定理从T66开始
- **黑屏bug**：index_agi12.html的`<script>`缺少`</script>`+CSS `<style>`块放在JS `<script>`之后而非`<head>`内，导致浏览器解析错乱。修复：闭合script标签+将CSS移入head
- **`/api/state` 500错误**：CompositeAGI_V2用`self.system_state`，app.py引用`agi.state`不存在。修复：添加`@property state`映射到`self.system_state`
- **M106 compute_phi字符串崩溃**：`_extract_feature_vectors`只支持dict格式，纯str列表报AttributeError。修复：添加isinstance判断兼容str/dict
- **M111缺get_state()**：只有get_complex_state()，与其他23个模块不一致。修复：添加get_state()委托到get_complex_state()
- **M85 f-string反斜杠**：Python 3.10不支持f-string内反斜杠。修复：改用字符串拼接
- **M83缺Tuple import**：`from typing`未包含Tuple。修复：添加Tuple到import列表
- **app.py M118 record_state类型**：observation和action被转为float()但应为str()。修复：改为str()
- **schedule包安装路径**：pip安装到D:/Apps/Python不在sys.path中。修复：app.py启动时自动添加D:/Apps/Python到sys.path
- **M106 Φ值精度低**：短对话(3-5轮)Φ值总返回0.0。修复v7.6.1：sigmoid软激活+Laplace平滑+余弦距离多样性熵+短对话整合度补偿。3轮: 0.0→0.1005
- **M81-M85 API不统一**：缺get_instance()+get_state()。修复：全部添加，M81委托get_tree_state(), M82/M84委托get_stats()
- **论文文档未同步**：太乙AGI论文v7.1→v7.6。修复：摘要/架构图/模块表/定理(T52-T78)/预言(P19-P22)/结论全面更新

## 服务启动
```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1 && python app.py
# 访问 http://127.0.0.1:5001/static/index_agi12.html
```
