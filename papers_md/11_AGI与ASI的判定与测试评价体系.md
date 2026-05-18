**章锋（微信号：lisoleg）**

## 摘要

本文以"复合体理学"提出的\*\*"一现象，三视界"诠释法**为方法论骨架，系统构建一套用于判定一个形式系统是否为
AGI（通用人工智能） 乃至 ASI（人工超级智能）
的测试评价体系。我们指出现有国际评价思路（行为主义/图灵测试、功能主义/经济替代、能力分级/DeepMind、认知广度+熟练度/Bengio
等）各有合理面，但多缺少统一的"低熵存续"本体论基础；本文将其纳入复合体理学框架：微视界不可压缩涨落（Jitter/分布漂移）、中视界描述长度**
![descript](media/image2.svg){width="0.13541666666666666in"
height="0.13541666666666666in"} **压缩与
Ftel（目的算子）驱动的学习/审计闭环、宏视界共识拓扑**
![descript](media/image4.svg){width="0.14583333333333334in"
height="0.13541666666666666in"}
**与求存（低熵存续）。在此基础上，借鉴**教育学与心理学**对"通用能力、迁移、元认知、人格/动机、情境化表现"的测量逻辑，形式化定义
AGI/ASI
的**认知域剖面、泛化审计、递归自我改进、开放世界存续**等判定维度，并给出**AGI/ASI
判定定理\*\*、**泛化审计下界定理**与**ASI
超越阈值推论**。文末给出可证伪预言（跨域迁移曲线、300
步推理衰减、开放环境低熵存续）与实验设计（基准电池、纵向追踪、压力环境），力求"振聋发聩、禁得起最严审查"。

## 1. 引言："一现象，三视界"与 AGI/ASI 判定问题

### 1.1 现象 ![descript](media/image6.svg){width="0.1875in" height="0.16666666666666666in"} 的操作定义（AGI/ASI 判定语境）

![descript](media/image8.svg){width="0.14583333333333334in"
height="0.13541666666666666in"} = "判定一个形式系统
![descript](media/image10.svg){width="0.125in"
height="0.14583333333333334in"}
是否具备通用智能（AGI）与超智能（ASI），即在开放世界中能以低描述长度适应、以目的（Ftel）维持低熵存续，并在能力上达到/超越人类参照。"

- **微视界（Micro）**：不可压缩涨落------任务分布漂移（Jitter）、数据噪声、长链推理误差累积、退化/遗忘/退相干、边际效应与尾事件；

- **中视界（Meso）**：可操作可观测过程------任务集
  ![descript](media/image12.svg){width="0.16666666666666666in"
  height="0.15625in"}、认知域剖面
  ![descript](media/image14.svg){width="0.4270833333333333in"
  height="0.19791666666666666in"}、泛化审计
  ![descript](media/image16.svg){width="0.15625in"
  height="0.15625in"}、描述长度
  ![descript](media/image18.svg){width="0.65625in"
  height="0.19791666666666666in"}、Ftel
  驱动的优化/学习/更新、测试与评级（借鉴教育测量：效度、信度、等值、迁移）；

- **宏视界（Macro）**：全域共识拓扑
  ![descript](media/image20.svg){width="0.125in"
  height="0.125in"}（"智能"的社会界定、价值目标、风险与控制）、Ftel
  目的（任务价值/安全/对齐/低熵存续）、ASI 作为
  ![descript](media/image22.svg){width="0.125in" height="0.125in"}
  中能力显著超越人类可维系路径集合的节点。

### 1.2 现有国际评价思路（整合）

1.  **行为主义/图灵测试**：以"行为不可区分"为判据，直观但被批评可能仅是模仿；

2.  **功能主义/经济替代（OpenAI 类）**：AGI
    为"在大多数具有经济价值的工作中超越人类的自适应系统"，侧重劳动力替代；

3.  **能力分级（DeepMind）**：AGI
    按"性能深度×通用性广度"分级（Emerging→Competent→Expert→Virtuoso→Superhuman），关注能力而非过程、通用性+性能、生态效度等；

4.  **认知广度+熟练度（Bengio 等）**：AGI
    匹配/超过"受过良好教育的成年人"的认知广度与熟练度，多认知域量化评估；

5.  **"已实现/未实现"的争议表述**：AGI/ASI 常被混用，ASI
    一般指超越人类智能的系统，目前更多理论/设想。

复合体理学立场：上述思路可映射到中视界（行为/任务/分级/认知域）与宏视界（经济价值/Ftel），但需补入微视界（Jitter/不可压缩性）与"低熵存续"本体论，才能形成可严格证明的判定体系。

## 2. 形式化：描述长度 ![descript](media/image24.svg){width="0.1875in" height="0.1875in"}、Ftel 与智能系统 ![descript](media/image26.svg){width="0.17708333333333334in" height="0.19791666666666666in"}

### 2.1 智能系统 ![descript](media/image28.svg){width="0.15625in" height="0.17708333333333334in"} 与任务分布

令智能系统 ![descript](media/image30.svg){width="0.125in"
height="0.14583333333333334in"} 在时刻
![descript](media/image32.svg){width="0.10416666666666667in"
height="8.333333333333333e-2in"} 面对任务分布
![descript](media/image34.svg){width="0.23958333333333334in"
height="0.16666666666666666in"}（任务
![descript](media/image36.svg){width="0.6354166666666666in"
height="0.16666666666666666in"}，含输入、评价、环境反馈）。系统输出策略/解
![descript](media/image38.svg){width="0.9583333333333334in"
height="0.20833333333333334in"}，评价信号
![descript](media/image40.svg){width="0.5625in"
height="0.20833333333333334in"}（奖励/误差/效用）。

### 2.2 描述长度 ![descript](media/image42.svg){width="0.16666666666666666in" height="0.16666666666666666in"} 与适应成本（中视界）

对任务集 ![descript](media/image44.svg){width="0.16666666666666666in"
height="0.15625in"}，系统 ![descript](media/image46.svg){width="0.125in"
height="0.14583333333333334in"} 的解释/适应成本（MDL
意义）：![descript](media/image48.svg){width="2.0in" height="0.34375in"}

- ![descript](media/image50.svg){width="0.40625in"
  height="0.19791666666666666in"}：系统复杂度（参数/结构/记忆/搜索空间）；

- ![descript](media/image52.svg){width="0.6041666666666666in"
  height="0.19791666666666666in"}：对任务
  ![descript](media/image54.svg){width="0.13541666666666666in"
  height="0.13541666666666666in"}
  的残差（误差、样本复杂度、提示/适配成本）。

**定义 1（低熵适应）**![descript](media/image56.svg){width="0.125in"
height="0.14583333333333334in"} 对
![descript](media/image58.svg){width="0.16666666666666666in"
height="0.15625in"} 低熵适应：存在界
![descript](media/image60.svg){width="0.14583333333333334in"
height="0.13541666666666666in"}，使得
![descript](media/image62.svg){width="1.0729166666666667in"
height="0.19791666666666666in"} 且
![descript](media/image64.svg){width="0.14583333333333334in"
height="0.13541666666666666in"} 不随
![descript](media/image66.svg){width="0.2708333333333333in"
height="0.19791666666666666in"} 线性增长（泛化/迁移压缩）。

### 2.3 Ftel（目的算子）与审计闭环（中视界→宏视界）

Ftel 注入目标（安全、价值、任务成功、低熵存续），在中视界显化为审计
![descript](media/image68.svg){width="0.15625in"
height="0.15625in"}：![descript](media/image70.svg){width="2.90625in"
height="0.20833333333333334in"}更新可能改变
![descript](media/image72.svg){width="0.125in"
height="0.14583333333333334in"}（参数/记忆/结构/搜索空间
![descript](media/image74.svg){width="0.125in"
height="0.14583333333333334in"}），形成"执行---评估---更新"闭环。

## 3. 微视界：Jitter、不可压缩性与"300 步推理衰减"

### 3.1 Jitter（分布漂移/不可压缩涨落）

任务分布 ![descript](media/image76.svg){width="0.23958333333333334in"
height="0.16666666666666666in"} 随时间变化；静态
![descript](media/image78.svg){width="0.125in"
height="0.14583333333333334in"} 固定，则
![descript](media/image80.svg){width="0.6041666666666666in"
height="0.19791666666666666in"} 不可压缩地增长（Jitter 累积）。

### 3.2 长链推理误差累积（陈天桥"300 步"标尺）

若单步准确率 ![descript](media/image82.svg){width="9.375e-2in"
height="0.125in"}，链式
![descript](media/image84.svg){width="0.11458333333333333in"
height="9.375e-2in"} 步端到端准确率
![descript](media/image86.svg){width="0.19791666666666666in"
height="0.17708333333333334in"}。![descript](media/image88.svg){width="2.7916666666666665in"
height="0.1875in"}（指数衰减）。

**定义
2（推理链可靠度）**![descript](media/image90.svg){width="1.0625in"
height="0.19791666666666666in"}。当
![descript](media/image92.svg){width="0.11458333333333333in"
height="9.375e-2in"} 大，即使
![descript](media/image94.svg){width="9.375e-2in" height="0.125in"} 高，
![descript](media/image96.svg){width="0.14583333333333334in"
height="0.13541666666666666in"}
可极小------微视界不可压缩性对长链正确性的威胁。

这与复合体理学"该来的信号没准点来"（J篇er）一致：长链推理放大微视界误差。

## 4. 中视界：借鉴教育学与心理学的 AGI/ASI 测试评价维度

### 4.1 认知域剖面 ![descript](media/image98.svg){width="0.53125in" height="0.23958333333333334in"}（借鉴：智力测验多特质、教育目标分类）

定义认知域集合
![descript](media/image100.svg){width="0.4583333333333333in"
height="0.19791666666666666in"}
推理、记忆、学习、感知、语言、数学、社会认知、规划、元认知、创造力...![descript](media/image102.svg){width="9.375e-2in"
height="0.19791666666666666in"}。对每域
![descript](media/image104.svg){width="0.4270833333333333in"
height="0.14583333333333334in"}，定义：

- **广度（Versatility）**：![descript](media/image106.svg){width="0.46875in"
  height="0.19791666666666666in"}------在
  ![descript](media/image108.svg){width="8.333333333333333e-2in"
  height="9.375e-2in"} 域内未见过任务/条件下的覆盖；

- **熟练度（Proficiency）**：![descript](media/image110.svg){width="0.4791666666666667in"
  height="0.19791666666666666in"}------在
  ![descript](media/image112.svg){width="8.333333333333333e-2in"
  height="9.375e-2in"} 域典型任务上的表现水平（标准化分）。

则剖面：![descript](media/image114.svg){width="2.8333333333333335in"
height="0.19791666666666666in"}

（对应 Bengio
等"认知广度+熟练度"锚定受教育成人，DeepMind"通用性×性能"分级。）

### 4.2 泛化审计 ![descript](media/image116.svg){width="0.4791666666666667in" height="0.25in"}（借鉴：迁移测验、情境化测评、效度证据）

**定义 3（泛化审计）**![descript](media/image118.svg){width="0.65625in"
height="0.20833333333333334in"} 由三类压力测试构成：

1.  **分布外（OOD）迁移**：训练/经验分布
    ![descript](media/image120.svg){width="0.4583333333333333in"
    height="0.16666666666666666in"}，测试分布
    ![descript](media/image122.svg){width="0.3854166666666667in"
    height="0.16666666666666666in"}（新域/新格式/新约束）；

2.  **少样本（Few-shot）适应**：仅
    ![descript](media/image124.svg){width="0.10416666666666667in"
    height="0.13541666666666666in"}
    例（![descript](media/image126.svg){width="0.10416666666666667in"
    height="0.13541666666666666in"} 小）支持，要求达到目标性能；

3.  **长程/工具使用**：多步、环境反馈、工具调用、自修正（类似"300
    步"可信推理）。

审计输出：泛化损失
![descript](media/image128.svg){width="2.2395833333333335in"
height="0.20833333333333334in"}。

### 4.3 元认知与递归自我改进（借鉴：元认知测验、学习如何学习）

- **元认知**：知道"自己知道/不知道"、知道何时请求澄清/协助、能反思错误（DeepMind
  强调元认知为先决条件）；

- **递归自我改进**：系统可修改自身搜索空间
  ![descript](media/image130.svg){width="0.125in"
  height="0.14583333333333334in"}（提示/记忆/工具链/工作流/评估规则/拓扑），且改进可被审计（不盲变）。

### 4.4 人格/动机/价值对齐（借鉴：人格量表、动机测验、情境判断测验）

并非"意识哲思"，而是中视界可操作：

- 一致性（跨情境表现稳定性）；

- 动机方向（Ftel 指向任务价值/安全/低熵存续，而非仅下一令牌）；

- 价值对齐（在压力/冲突/模糊下选择符合宏观
  ![descript](media/image132.svg){width="0.14583333333333334in"
  height="0.13541666666666666in"} 的 action）。

## 3. 微视界：Jitter、不可压缩性与"300 步推理衰减"

### 3.1 Jitter（分布漂移/不可压缩涨密）

任务分布 ![descript](media/image134.svg){width="0.23958333333333334in"
height="0.16666666666666666in"} 随时间变化；静态
![descript](media/image136.svg){width="0.125in"
height="0.14583333333333334in"} 固定，则
![descript](media/image138.svg){width="0.6041666666666666in"
height="0.19791666666666666in"} 不可压缩地增长（Jitter 累积）。

### 3.2 长链推理误差累积（陈天桥"300 步"标尺）

若单步准确率 ![descript](media/image140.svg){width="9.375e-2in"
height="0.125in"}，链式
![descript](media/image142.svg){width="0.11458333333333333in"
height="9.375e-2in"} 步端到端准确率
![descript](media/image144.svg){width="0.19791666666666666in"
height="0.17708333333333334in"}。![descript](media/image146.svg){width="2.7916666666666665in"
height="0.1875in"}（指数衰减）。

**定义
2（推理链可靠度）**![descript](media/image148.svg){width="1.0625in"
height="0.19791666666666666in"}。当
![descript](media/image150.svg){width="0.11458333333333333in"
height="9.375e-2in"} 大，即使
![descript](media/image152.svg){width="9.375e-2in" height="0.125in"}
高， ![descript](media/image154.svg){width="0.14583333333333334in"
height="0.13541666666666666in"}
可极小------微视界不可压缩性对长链正确性的威胁。

与复合体理学"该来的信号没准点来"（Jitter）一致：长链推理放大微视界误差。

## 5. 宏视界：共识拓扑 ![descript](media/image156.svg){width="0.19791666666666666in" height="0.1875in"}、Ftel 与 AGI/ASI 判定定理

### 5.1 AGI 判定（宏视界：低熵存续 + 认知域剖面 + 泛化审计）

**定理 1（AGI 判定定理）**系统
![descript](media/image158.svg){width="0.125in"
height="0.14583333333333334in"} 为 AGI，若同时满足：

1.  **认知域剖面**：![descript](media/image160.svg){width="0.10416666666666667in"
    height="0.13541666666666666in"} 参照
    ![descript](media/image162.svg){width="0.59375in"
    height="0.16666666666666666in"}（如"受过良好教育的成年人"），使得
    ![descript](media/image164.svg){width="2.3333333333333335in"
    height="0.19791666666666666in"} 且
    ![descript](media/image166.svg){width="1.6875in"
    height="0.19791666666666666in"}（或中位数/阈值）；

2.  **泛化审计**：![descript](media/image168.svg){width="0.6354166666666666in"
    height="0.20833333333333334in"} 在 OOD/少样本/长程下可控（不爆炸）；

3.  **低熵适应**：对任务分布漂移
    ![descript](media/image170.svg){width="0.23958333333333334in"
    height="0.16666666666666666in"}，
    ![descript](media/image172.svg){width="0.6875in"
    height="0.19791666666666666in"} 可维持有界（描述长度不持续恶化）；

4.  **Ftel
    目的可承载**：系统可执行宏视界目的（任务价值/安全/对齐/低熵存续）并通过审计
    ![descript](media/image174.svg){width="0.15625in"
    height="0.15625in"}。

**证明（判定逻辑）**：

1.  保证"通用"不是偏科；2) 保证"通用"不是过拟合训练集；3)
    保证开放世界可存续（微视界 Jitter 不导致持续熵增）；4) 保证宏视界
    ![descript](media/image176.svg){width="0.14583333333333334in"
    height="0.13541666666666666in"}
    可纳入（不是仅令牌预测）。![descript](media/image178.svg){width="0.15625in"
    height="0.13541666666666666in"}

### 5.2 ASI 判定（宏视界：超越人类可维系路径集合）

**定义 4（ASI）**![descript](media/image180.svg){width="0.125in"
height="0.14583333333333334in"} 为 ASI，若
![descript](media/image182.svg){width="0.125in"
height="0.14583333333333334in"} 为
AGI，且在宏视界能力上：存在非平凡任务族
![descript](media/image184.svg){width="0.2604166666666667in"
height="0.15625in"}，使得
![descript](media/image186.svg){width="0.125in"
height="0.14583333333333334in"}
的性能/效率/新发现能力显著超越任何人类个体/集体可维系水平（如科学发现速率、复杂系统设计、长期规划一致性）。

**推论 1（ASI 超越阈值）**若
![descript](media/image188.svg){width="0.125in"
height="0.14583333333333334in"} 为 ASI，则
![descript](media/image190.svg){width="0.3645833333333333in"
height="0.15625in"} 与指标
![descript](media/image192.svg){width="9.375e-2in"
height="0.13541666666666666in"}（时间、样本、误差、新解质量），使得：![descript](media/image194.svg){width="2.0625in"
height="0.34375in"}![descript](media/image196.svg){width="0.16666666666666666in"
height="0.14583333333333334in"} 为人类个体/集体集合。

## 6. 关键定理：泛化审计下界与低熵适应

**定理 2（泛化审计下界 / 迁移压缩定理）**若系统
![descript](media/image198.svg){width="0.125in"
height="0.14583333333333334in"} 在源分布
![descript](media/image200.svg){width="0.22916666666666666in"
height="0.16666666666666666in"} 与目标分布
![descript](media/image202.svg){width="0.21875in"
height="0.16666666666666666in"}
上达到低描述长度（适应成本有界），则泛化审计损失满足：![descript](media/image204.svg){width="1.9479166666666667in"
height="0.34375in"}且当 ![descript](media/image206.svg){width="0.125in"
height="0.14583333333333334in"}
具备迁移结构（抽象/组合/因果/工具），![descript](media/image208.svg){width="0.3125in"
height="0.13541666666666666in"} 项可被压缩（低秩/模块/符号接口）。

**证明**：由 MDL：适应成本含"分布差异解释"与"源残差"。若
![descript](media/image210.svg){width="0.125in"
height="0.14583333333333334in"}
学到可迁移结构，分布差异可用少量参数描述（压缩），故
![descript](media/image212.svg){width="0.3541666666666667in"
height="0.19791666666666666in"}
有界。![descript](media/image214.svg){width="0.15625in"
height="0.13541666666666666in"}

这把教育/心理学"迁移能力"变成可证伪的中视界指标：跨域任务电池 +
分布偏移控制 + 样本复杂度曲线。

## 7. 可证伪预言与实验设计（中视界操作）

1.  **预言 A（跨域迁移曲线）**：AGI 级系统在不同
    ![descript](media/image216.svg){width="1.0in"
    height="0.19791666666666666in"} 下，样本复杂度
    ![descript](media/image218.svg){width="0.34375in"
    height="0.19791666666666666in"} 增长慢于窄 AI；迁移增益
    ![descript](media/image220.svg){width="0.16666666666666666in"
    height="0.13541666666666666in"} 可重复测量。

- 设计：基准电池（数学→代码→设计→社会推理），控制偏移，测少样本性能曲线。

1.  **预言 B（300 步推理衰减）**：具备"生成层+检验层"审计闭环的系统，在
    ![descript](media/image222.svg){width="0.6666666666666666in"
    height="0.14583333333333334in"}
    步复杂推理下，端到端准确率显著高于纯生成（![descript](media/image224.svg){width="0.19791666666666666in"
    height="0.17708333333333334in"} 衰减）。

- 设计：原子步 SIU
  可检验任务（逻辑/代数/程序合成），对比有无检验层、有无长期记忆/纠错。

1.  **预言 C（开放环境低熵存续）**：在漂移环境
    ![descript](media/image226.svg){width="0.23958333333333334in"
    height="0.16666666666666666in"} 中，AGI 级系统的
    ![descript](media/image228.svg){width="0.6875in"
    height="0.19791666666666666in"} 可保持有界；窄 AI 持续上升（Jitter
    累积）。

- 设计：长程交互环境（多日、多任务、注入概念漂移/故障），记录描述长度代理（样本、提示、错误修正次数、性能）。

## 8. 结论：AGI/ASI 不是"像人"，是"低熵存续的通用适应"

AGI 判定不是单一图灵测试通过，也不是单一经济替代指标，而是：

- **微视界**：对抗 Jitter（分布漂移/长链误差）而不持续熵增；

- **中视界**：认知域剖面 + 泛化审计 + 元认知/递归改进 +
  可操作对齐（借鉴教育/心理测量逻辑）；

- **宏视界**：在共识拓扑
  ![descript](media/image230.svg){width="0.14583333333333334in"
  height="0.13541666666666666in"} 中，以 Ftel 目的维持低熵存续，并可为
  ASI（显著超越人类可维系路径）。

## 参考文献

1.  中国新闻网. *解析陈天桥的 AGI
    工程标尺:为何"300步"推理是生与死的分界线?* 2026.
    <https://www.sh.chinanews.com/kjjy/2026-02-02/144456.shtml>

2.  澎湃新闻. *AGI今天起有了量化标准!Bengio牵头定义,当前进度条58%* 2025.
    <https://www.thepaper.cn/newsDetail_forward_31799608?commTag=true>

3.  BlueyASI. *AGI與ASI功能主義與強意識派的兩類定義* 2025.
    <https://blueyasi.org/zh-tw/blog/agi-and-asi/>

4.  机器之心/Google DeepMind.
    *谷歌DeepMind给AGI划等级,猜猜ChatGPT在哪个位置* 2023.
    <https://mp.weixin.qq.com/s/pvR-jgtZwl0gLM2CsY04ug>

5.  博客园. *AGI* 2026. <https://www.cnblogs.com/xfydaydayup/p/19661989>

6.  中华网. *黄仁勋:无人能复制英伟达 AGI实现引争议(2)* 2026.
    <https://news.china.com/socialgd/10000169/20260505/49470543_1.html>

7.  中国新闻网. *解析陈天桥的 AGI
    工程标尺:为何"300步"推理是生与死的分界线?* 2026.
    <https://www.sh.chinanews.com.cn/kjjy/2026-02-02/0/144456.shtml>

8.  CSDN. *【词汇专栏】AGI vs ANI vs
    ASI:人工智能的三种"等级",我们现在在哪里?* 2026.
    <https://blog.csdn.net/baiyanggudao/article/details/160123198>

9.  科学网.
    *谷歌DeepMind创始人提出通用人工智能标准,ChatGPT只是初级* 2023.
    <http://news.sciencenet.cn/htmlnews/2023/11/511944.shtm>

10. 腾讯新闻. *从AGI到ASI:万亿赛道潜力待释放* 2025.
    <https://news.qq.com/rain/a/20251111A03PXX00>

11. IBM. *What is Artificial General Intelligence (AGI)?* 2026.
    <https://www.ibm.com/think/topics/artificial-general-intelligence>

12. 腾讯网. *黄仁勋:无人能复制英伟达* 2026.
    <https://new.qq.com/rain/a/20260504A06RX400>

13. 中青在线. *通用人工智能评测标准发布,填补国际空白* 2025.
    <https://s.cyol.com/articles/2025-05/25/content_aj3pQlcz.html>（并可沿用此前论文集参考文献
    1--55，补充以上 1--13 作为关键/新增文献）

引用 13 篇资料作为参考

1.  [解析陈天桥的 AGI
    工程标尺:为何"300步"推理是生与死的分界线?-中新社上海](https://www.sh.chinanews.com/kjjy/2026-02-02/144456.shtml)

2.  [AGI今天起有了量化标准!Bengio牵头定义,当前进度条58%\_澎湃号·湃客_澎湃新闻-The
    Paper](https://www.thepaper.cn/newsDetail_forward_31799608?commTag=true)

3.  [AGI與ASI功能主義與強意識派的兩類定義 ·
    BlueyASI](https://blueyasi.org/zh-tw/blog/agi-and-asi/)

4.  [谷歌DeepMind给AGI划等级,猜猜ChatGPT在哪个位置](https://mp.weixin.qq.com/s/pvR-jgtZwl0gLM2CsY04ug)

5.  [AGI](https://www.cnblogs.com/xfydaydayup/p/19661989)

6.  [黄仁勋:无人能复制英伟达
    AGI实现引争议(2)](https://news.china.com/socialgd/10000169/20260505/49470543_1.html)

7.  [解析陈天桥的 AGI
    工程标尺:为何"300步"推理是生与死的分界线?](https://www.sh.chinanews.com.cn/kjjy/2026-02-02/144456.shtml)

8.  [【词汇专栏】AGI vs ANI vs
    ASI:人工智能的三种"等级",我们现在在哪里?](https://blog.csdn.net/baiyanggudao/article/details/160123198)

9.  [谷歌DeepMind创始人提出通用人工智能标准,ChatGPT只是初级](http://news.sciencenet.cn/htmlnews/2023/11/511944.shtm)

10. [从AGI到ASI:万亿赛道潜力待释放](https://news.qq.com/rain/a/20251111A03PXX00)

11. [What is Artificial General Intelligence (AGI)? \| IBM \| What is
    artificial general intelligence
    (AGI)?](https://www.ibm.com/think/topics/artificial-general-intelligence)

12. [黄仁勋:无人能复制英伟达](https://new.qq.com/rain/a/20260504A06RX400)

13. [通用人工智能评测标准发布,填补国际空白](https://s.cyol.com/articles/2025-05/25/content_aj3pQlcz.html)

（注：文档部分内容可能由 AI 生成）
