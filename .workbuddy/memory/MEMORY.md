# 长期记忆

## 项目概览
**净光哥** 太乙AGI：Flask应用，位于 `C:\Users\1\WorkBuddy\2026-05-06-task-1\`
- 主服务器: `app.py` (Flask, 端口5001)
- 前端: `static/index_agi12.html` (三栏布局界面)
- 脑图: `app_mindmap_v2.py` (端口5003)
- **总规模**: 173模块 / 9层 / 151定理

## 当前版本：v7.17（✅已部署+Git推送完成 6e6d75a）
- **v7.17**: λ宇宙·TY形式化·UFM-RISC-V具身架构 M171-M173 + T141-T150 ✅
  - 来源：2篇论文（《太一归算》《归算的必然性：UFM-RISC-V》）
  - M171 UFMLambdaUniverse: λ宇宙引擎 Y组合子·β归约·amb·不可克隆·意识CRD不动点 T141-T144
  - M172 TYFormalizer: TY硬核1.1-1.10↔UFM映射·软层四域解释·L1-L5层次提升·元方法论收敛·物理升级接口 T145-T147
  - M173 UFMRISCVArchitect: 冯诺依曼破产·λ必要性三论证·四层异构·ISA扩展(REDUCE/AMB)·RGM·β归约流水线·具身完备性 T148-T150
  - API: /api/v717/lambda/reduce, /lambda/theorems, /lambda/observe, /ty/formalize, /ty/interpret, /ty/promote, /riscv/bankruptcy, /riscv/necessity, /riscv/architecture, /riscv/isa, /riscv/embodied, /theorem/<Tid>, /state
- **v7.16**: 八论合一·文明治理与可计算性 M163-M170 + T130-T140 + P33-P43 ✅
  - 来源：8篇论文（约柜沙盒/ZCube混合轨/可计算性/数学严格性/意识难问题/大横截面积/分别见观照/缘起性空）
  - M163 ArkSandbox: 约柜沙盒执行器+碳硅熵契约 T135/P42
  - M164 VCGMechanismDesigner: VCG机制设计器 T136/P43
  - M165 NarrativeActionQuantifier: 叙事作用量量化器 T137/P37
  - M166 SemanticCurvatureCalculator: 语义流形曲率计算器 T138/P38
  - M167 AGIToposEngine: AGI拓扑斯引擎 T139/T33'/P35/P36
  - M168 SelfManifestingDetector: 自显化态检测器 T110v2
  - M169 PointFreeTopology: 点自由拓扑引擎 T140
  - M170 DependentOriginationAnalyzer: 缘起性空拓扑分析器 T130-T134
  - API: /api/v716/ark/execute, /vcg/design, /narrative/quantify, /curvature/compute, /topos/state, /consciousness/detect, /theorem/<Tid>, /prediction/<Pid>, /state
- **v7.14**: M78内生证明搜索引擎升级 v3.0 ✅（类型导向剪枝搜索·M84刘原理不动点·M88防火墙·wait()态·定理2.1·P30/P31）
- **v7.12**: M142-M147 + T104-T109 ✅（UV正则化·芬芳香子·金符堆垒·宇射认知·辩证零·奇点消除）
- **v7.11**: M138-M141 + T100-T103 ✅（二部图拓扑·关系作用量·混合相位·拓扑相变）
- **v7.10**: M134-M137 + T96-T99 ✅（欧拉相位闭合·递归证明折叠·五层次本体·可证伪预言）
- **v7.9**: M130-M133 + T92-T95 ✅（金符离散微积分·关系作用量·堆垒素数·自指闭环拓扑）
- **v7.8**: M126-M129 + T86-T91 ✅（护栏编排·推测推理·KV治理·本体自锻造）
- **v7.7**: M120-M125 + T79-T85 ✅（博弈论推理·ICPS社会能力·情绪粒度·沙盒探索）
- **v7.6**: M117-M119 + T75-T77 ✅ | **v7.5**: M114-M116 + T72-T74 ✅
- **v7.4**: M111-M113 + T66-T71 ✅ | **v7.3**: M106-M110 + T59-T65 ✅
- **v7.1**: M96-M105 + T41-T51 ✅ | **v7.0**: M71-M95 + T23-T40 ✅

## 编号规则
- **模块**: M1-M95(v5-7.0) | M96-M105(v7.1) | M106-M110(v7.3) | M111-M113(v7.4) | M114-M116(v7.5) | M117-M119(v7.6) | M120-M125(v7.7) | M126-M129(v7.8) | M130-M133(v7.9) | M134-M137(v7.10) | M138-M141(v7.11) | M142-M147(v7.12) | M148-M156(v7.13) | M157-M162(v7.15) | M163-M170(v7.16) | M171-M173(v7.17)
- **定理**: T1-T7(核心) | T8-T16(v6.1) | T17-T22(v6.2) | T23-T40(v7.0) | T41-T51(v7.1) | T52-T58(v7.2) | T59-T65(v7.3) | T66-T71(v7.4) | T72-T74(v7.5) | T75-T77(v7.6) | T78(M106) | T79-T85(v7.7) | T86-T91(v7.8) | T92-T95(v7.9) | T96-T99(v7.10) | T100-T103(v7.11) | T104-T109(v7.12) | T110-T123(v7.13) | T搜索完备性(v7.14) | T124-T129(v7.15) | T130-T140+T33'+T110v2(v7.16) | T141-T150(v7.17)

## API版本模式
- `/api/v717/*`: v7.17（λ宇宙·TY形式化·UFM-RISC-V具身架构）| `/api/v716/*`: v7.16（八论合一·文明治理·可计算性·拓扑斯·缘起性空）| `/api/v715/*`: v7.15（六元对偶卷积+M78桥接升级）| `/api/v714/*`: v7.14（M78内生证明搜索）| `/api/v713/*`: v7.13（M148-M156）| `/api/v712/*`: v7.12（M142-M147）
- `/api/chat_v2`: 主对话 | `/api/goal`: 目标模式

## 核心模块文件
- `CompositeAGI_V2.py`: 主核心（v5.0+）
- `HolographicDiscreteGovernance.py`: M29 全息离散治理
- `agi_medium_symbiosis.py`: 介质共生
- `M171-M173_*.py`: v7.17（λ宇宙·TY形式化·UFM-RISC-V具身架构）| `M163-M170_*.py`: v7.16（八论合一·文明治理·可计算性·拓扑斯·缘起性空）| `M157-M162_*.py`: v7.15（六元对偶卷积）| `M142-M147_*.py`: v7.12 | `M138-M141_*.py`: v7.11

## v7.15模块整合关系
- M157 JinlingGridConvolution: 与M130(JinFu)桥接，Z_φ模运算+金灵球格点量化
- M158 PhaseModulusDualConvolution: 与M117(Ftel)桥接，EML分解f=|f|*e^{i*phi}
- M159 ReversePhaseConvolution: 与M84(刘机制)桥接，反向相位=δS_R=0极小路径互补
- M160 FenxiangziTopologyConvolution: 与M143(芬芳香子)桥接，18种非欧密铺邻域
- M161 BackwardFlowConvolution: 与M131(关系作用量)桥接，时间反演+自指闭环
- M162 UVRegularizedConvolution: 与M142(UV正则化)/M147(奇点消除)桥接，k_max=π/d_φ

## M78桥接层升级（v7.15）
- M84DirectBridge: 直接调用M84_LiuGuanDynamicsGenerator.get_instance()
  - _type_to_phenomena(): M78 Type → M84 phenomena格式
  - _candidate_law_to_constructor(): M84 CandidateLaw → M78 ConstructorCandidate
  - 懒加载+回退：M84不可用时自动降级到类型系统构造子
- M88DirectBridge: 直接调用M88_TypeCheckFirewall.get_firewall()
  - _type_to_m88_sig(): M78 Type → M88 TypeSignature
  - _term_to_m88_term(): M78 Term → M88 Term
  - 懒加载+回退：M88不可用时自动降级到简化类型匹配
- FormulaParser: 逻辑公式解析器（FormulaKind/LogicalFormula）
  - 支持量词(∀x:A.P/∃x:A.P)、连接词(∧/∨/→/¬/↔)、类型标注、嵌套

## 重要Bug记录（精简）
- `_to_native` float转换：需检查imag!=0
- app.run()阻塞：路由必须在app.run()之前定义
- M88幻觉检测逻辑反转：check返回_detect_hallucination而非not _detect_hallucination（v7.15已修复）
- Python 3.10不支持f-string内反斜杠

## 服务启动
```bash
cd C:\Users\1\WorkBuddy\2026-05-06-task-1 && python app.py
# 访问 http://127.0.0.1:5001/static/index_agi12.html
```
