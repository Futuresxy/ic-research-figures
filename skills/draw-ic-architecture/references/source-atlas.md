# 论文图片参考索引

检索/图页检查日期：2026-10-24。方法：作者/学校/项目官网优先，打开 PDF 并查看指定页的实际图像，不仅看摘要。以下 8 篇/版本是代表性样本，不是穷尽综述，也不将 ISPASS 称为与 ISCA 同类的顶会。只总结表达方法，不复制论文图片；本仓库示例均原创、数据均 synthetic。

页数使用 PDF 从 1 起计数，与印刷页可能不同。图号只对下面链接的版本成立。设计建议为本技能归纳，不声称是作者或会议规定。

| 论文 / 版本 | 类型与已检查图片 | 可借鉴方法 | 使用边界 |
|---|---|---|---|
| Eyeriss，ISSCC 2016 | PDF p2，Fig.14.5.1–14.5.6：架构、PE、数据映射、实验图 | 总览/局部细节分离，同类 PE 规则网格，通路用一致标识，图注解释运行条件 | 芯片实测论文；不要与 ISCA 2016 dataflow 论文的图号混用 |
| Bit Fusion，ISCA 2018 作者版 | p4 Fig.3，p5 Fig.5–7：融合示例、层次架构、位级微架构 | 从阵列到 FU 再到 bit brick 分层展开；不同精度用平行面板对照 | 其低位宽整数实现不能直接证明浮点 FP4 方案可行 |
| Timeloop，ISPASS 2019 | p2 Fig.1–3，p9 Fig.12–13：框架、硬件抽象、映射、DSE | 输入/mapper/model/output 分离，硬件组织和 mapping 分开；多图共用编码比较能量/空间 | 是性能分析工具会议的参考；不要把 mapping 差异错当纯硬件差异 |
| Accelergy，ICCAD 2019 | p3 Fig.3–4，p7 Fig.10–11：估计框架、组件分层、能量分解 | 区分 action count、ERT、估计器；同类组件一致配色，细粒度与总量分层展示 | energy 与 power 不混；示例条件不外推到新工艺 |
| LLMCompass，arXiv:2312.03134v1（2023），对应工作后发表于 ISCA 2024 | p3 Fig.3、p9 Fig.7–9：硬件模板和计算/存储敏感性 | 系统/核心/存储层级清楚；Prefill/Decode、参数扫描并排展示 | 实际查看的是 v1，会议版标题、图号和数据可能不同，不当最终会议版复现 |
| Distributed Microarchitectural Protocols in the TRIPS Prototype Processor，MICRO 2006 | p3 Fig.3–4：执行 tile 和网络 | 分离 tile 内部通路与全局网络；明确队列/寄存器与连接方向 | 历史 CPU 设计，只学习表达，不用来断言现代 GPU 结构 |
| Gemmini，DAC 2021 | p1 Fig.1：SoC 集成与加速器内部 | 系统边界内嵌细节，controller/DMA/TLB/scratchpad/array/accumulator 明确分工 | 不把完整 SoC 评估简化为单阵列 peak 性能 |
| Aladdin，ISCA 2014 | p2 Fig.2、p8 Fig.8：含/不含存储的 DSE 与 PPA 校准 | 用同坐标比较建模范围；性能/功耗/面积独立面板与同一基线对齐 | 图中趋势不等于新芯片数据；校准与设计探索都要保留条件 |

## 一手链接

1. Eyeriss [项目](https://eyeriss.mit.edu/) · [ISSCC PDF](https://www.rle.mit.edu/eems/wp-content/uploads/2016/02/eyeriss_isscc_2016.pdf)
2. Bit Fusion [作者 PDF](https://jongse-park.github.io/files/paper/2018-isca-bitfusion.pdf) · [项目](https://www.act-lab.org/artifacts/bitfusion/)
3. Timeloop [作者 PDF](https://www.parashar.org/ispass19.pdf) · [官方引用列表](https://timeloop.csail.mit.edu/references)
4. Accelergy [作者机构页面](https://research.nvidia.com/publication/2019-11_accelergy-architecture-level-energy-estimation-methodology-accelerator-designs) · [PDF](https://d1qx31qr3h6wln.cloudfront.net/publications/ICCAD_2019_Accelergy.pdf)
5. LLMCompass [明确 v1 PDF](https://arxiv.org/pdf/2312.03134v1) · [ISCA 2024 机构书目](https://collaborate.princeton.edu/en/publications/llmcompass-enabling-efficient-hardware-design-for-large-language-/) · [代码](https://github.com/PrincetonUniversity/LLMCompass)
6. TRIPS [作者 PDF](https://www.cs.utexas.edu/ftp/dburger/papers/MICRO06_trips.pdf)
7. Gemmini [作者 PDF](https://people.eecs.berkeley.edu/~ysshao/assets/papers/genc2021-dac.pdf)
8. Aladdin [作者 PDF](https://vlsiarch.eecs.harvard.edu/sites/g/files/omnuum11281/files/vlsiarch/files/aladdin_a_pre-rtl_power-performance_accelerator_simulator_enabling_large_design_space_exploration_of_customized_architectures.pdf) · [官方代码/会议说明](https://github.com/harvard-acc/ALADDIN)

## 其他检索到但未做图页检查的资料

[Simba，MICRO 2019](https://people.eecs.berkeley.edu/~ysshao/assets/papers/shao2019-micro.pdf)：作者 PDF 体积超出本次检索工具限制。可作为 chiplet/MCM 后续扩展参考；未据此编造图号或完成视觉分析的声明。

## 从观察到技能规则

- Eyeriss、Bit Fusion、TRIPS、Gemmini → 分层与局部放大、独立可编辑模块、通路/存储/控制语义。
- Timeloop、Accelergy、LLMCompass → mapping/model/输入输出分开，参数搜索和建模边界清楚。
- Aladdin 与上述评估图 → PPA 分面、baseline/条件一致、校准先于结果解释。
- 颜色、字体、图内少注释、原生 draw.io、Python+CSV、严格 Pareto 与人工编辑保护是本技能的综合设计选择，不是这些论文共同发布的规范。

## 格式依据

[draw.io 原生保存格式](https://www.drawio.com/docs/manual/editor/save-file-formats/) 明确 .drawio 为原生 XML；含嵌入图数据的 SVG 与普通 SVG 不同。
[Codex skills 官方入口](https://developers.openai.com/codex/skills)（当前重定向到 ChatGPT Learn）用于核对 SKILL.md/资源组织。安装目录因客户端版本可能不同，优先项目 .agents/skills 并检查客户端可发现性。

## 引用与再使用

保留原论文链接与版本；若未来用户要求直接复用原图，先核实相应许可/出版政策并按要求注明转载或改绘。原创重绘仍需引用所表达的原研究思想；不能将原论文截图套用本仓库代码许可。

