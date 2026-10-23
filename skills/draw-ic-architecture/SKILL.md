---
name: draw-ic-architecture
description: Create and revise editable research figures for integrated circuits, digital IC, computer architecture, microarchitecture, accelerators, chip modeling, PPA, roofline and design-space exploration (DSE). Use for chip/system block diagrams, datapaths, PE arrays, pipeline/control flow, modeling workflows, power/area breakdowns and scientific plots. Deliver native editable draw.io objects for structural figures and Python plus CSV/JSON for data figures.
---

# IC / Architecture Research Figures

## 交付约定

- 架构、流程、微架构交付原生 .drawio、SVG 预览，按需导出 PDF。模块、连线、文字必须可分别编辑；禁止把整张位图包装进 draw.io 冒充可编辑图。
- 数据图交付 Python、原始 CSV/JSON、配置、SVG/PDF/PNG 与复现命令。数据与代码分离，用 Matplotlib 原生 subplot/GridSpec 拼版；不用图像生成模型画精确图表。
- 数据图内部只放轴标题、刻度、图例、必要子图编号与用户要求的简短标题；解释、条件、结论放独立图注。默认不加数值贴纸、结论箭头、水印、装饰和长句。架构图允许模块名、位宽和必要协议标签。
- 人工编辑后的 .drawio 是最新真源。直接更新原生对象并保留 ID/位置/改动，禁止用旧 JSON 重建覆盖。
- 不虚构硬件参数、实验结果、论文图号或数据。示例在文件名、元数据、图注标明 synthetic/demo；不能当作研究结果。

## 工作流程

1. 确定图支持的一条论证、受众、栏宽、编辑格式和来源。信息足够即开始；关键拓扑/协议/数值缺失时标假设或询问，不擅自补全。
2. 从 [source-atlas](references/source-atlas.md) 选表达模式；它是代表性样本，非完整综述、非顶会强制标准。不将原论文图片复制进交付仓库。
3. 结构图读 [structural](references/structural.md) 和 [editability](references/editability.md)；数据图读 [quantitative](references/quantitative.md)；多精度/供数/配比问题加读 [precision-dse](references/precision-dse.md)。
4. 从 assets/*.json 或 *.drawio 起稿，或按真实设计新建图。复杂系统拆 overview/detail；保持比较面板尺度、角色配色与端口顺序一致。
5. 运行模板脚本。以下路径相对技能目录：

```bash
python3 scripts/diagram.py assets/system.json --out output/system
python3 scripts/plot.py assets/demo_dse.csv --kind dse --out output/demo_dse
python3 scripts/plot.py assets/demo_ppa.csv --kind breakdown --out output/demo_ppa
python3 scripts/check.py output/system.drawio
```

结构图仅需 Python 标准库；默认数据后端需 matplotlib>=3.6,<4。优先装到项目虚拟环境；无法安装时显式用 --backend svg 并说明只输出 SVG 的限制。参数见 --help。

6. 在 draw.io/diagrams.net 打开结构源文件，移动模块确认连接仍附着，编辑标签并另存临时副本。渲染并检查最终尺寸。数据图在副本中修改一行，重跑并核对变化。
7. 执行 [quality](references/quality.md) 中语义、数值、视觉、编辑与复现检查。XML 检查不能替代编辑器/视觉验证；缺工具准确说明未验证项。
8. 交付源文件、预览、图注和复现命令，列实际假设与限制。保存到用户指定目录/仓库。

## 路由

| 任务 | 产物 | 参考 |
|---|---|---|
| SoC、GPU/NPU、chiplet、存储互联 | 分层 draw.io | structural §1 |
| PE、tensor core、位宽重构、流水/反馈 | draw.io + 时序面板 | structural §2–4 |
| 编译、仿真、建模、DSE 流程 | draw.io 流程 | structural §5 |
| 功耗/能耗/面积分解 | Python 分组/堆叠柱 | quantitative §2 |
| 参数扫描、Pareto、消融、roofline | Python 散点/折线/热图 | quantitative §3–6 |
| 16:8:4 配比与供数瓶颈 | 架构 + DSE 面板 | precision-dse |

## 示例请求

- “画 HBM/L2/本地 buffer/4×4 PE 架构图，组内广播、组间脉动。”核实层级与方向，不把通用示意当成特定芯片事实。
- “把综合报告面积与三类功耗画双子图。”核对单位、PVT、活动率和估计阶段，分开面积与功耗，交付数据和代码。
- “比较 1:2:4、1:4:8 收益。”明确固定面积/功耗预算与 workload，画应用时延/能量 Pareto 和瓶颈分解，不把 peak TOPS 当应用加速。

