# 数值图与可复现性

## 1. 数据契约

记录 source、design、workload/model、batch、sequence length、precision、process/PVT、频率、电压、测量/仿真阶段、工具版本、重复次数、聚合方式。未知写 unknown；不可用 demo 补空。缺失保留 NaN/空，不填零，不跨不同条件混合平均。

单位明确：area mm²/µm²，power mW/W，energy pJ/nJ/J，latency ns/ms，bandwidth GB/s 或 GiB/s，throughput token/s 或明确操作计数的 TOPS。FMA 是否算两操作、dense/sparse peak、读写是否合计写图注。

归一化按相同 workload 配对：speedup=T_base/T_design，energy ratio=E_design/E_base，改善方向相反。不要只写“Normalized”。正数比例可用几何平均并注明；总吞吐/总时间按任务语义聚合，不机械平均一切。

## 2. 面积、功耗、能量

- 三种量分开图，不相加或共用堆叠轴；多面板保持设计排序。
- 绝对堆叠柱展示总量与组成；100% 堆叠只展示组成，不能证明总量下降。分类必须互斥、穷尽。
- internal/switching/leakage 依据报告定义，不再叠加已包含它们的 dynamic。模块分解和机制分解不要混合。
- post-synthesis/post-layout/analytical/measured silicon 分面或区分图例。说明 PVT、VCD/SAIF/活动率、时钟、SRAM macro 范围；综合功耗不等于实测。
- E=∫Pdt；明确同一时间区间才用平均功耗×时间，峰值功耗×时间不是实际能量。
- 柱轴默认从零起。跨工艺或频率比较说明归一化模型与误差。

## 3. DSE 与 Pareto

优先两目标散点，不用难读三维曲面。标单位、可行域与优化方向。先过滤约束再算前沿，颜色表示家族、形状表示阶段/精度；连续第三指标才用色条，别同时塞六个维度。

Min-min: a 支配 b 当且仅当每维 a≤b 且至少一维严格小。最大化目标先取负统一方向；重复坐标可保留多个等价设计，不互相支配。前沿仅是已采样非支配集合，不保证全局最优。连线是视觉引导，不说明中间配置存在。

搜索轨迹用评价预算/次数对 best-so-far；算法比较同预算、同可行域，多随机种子可画区间。热图缺测 mask，不插值伪造配置。固定面积、功耗约束分别验证，不能只比 peak TOPS。

## 4. Roofline 与瓶颈

P≤min(P_peak,B·AI)，统一 ops/s、bytes/s；每级存储用本级流量算 AI，不把 HBM AI 套 SRAM roof。log-log 必须正值，ridge=P_peak/B。理论、校准、实测区分；注明精度和稀疏倍率。SFU、launch、依赖、通信不被简化 roofline 完整捕捉。

latency breakdown 可含 compute、memory、communication、launch/stall，但重叠段不能相加；使用 critical path 或明确非重叠归因。Prefill/Decode 分面并保留 batch/context/并行策略。

## 5. 校准、误差与消融

模型 vs 实测加 y=x，可补残差图。定义 relative error 分母和零值处理；MAPE 不用于零真实值。CI/std/min-max 明确区分；没有重复实验不伪造误差棒。

消融说明逐项移除还是增量开启，保持 baseline/workload 一致，交互收益不重复相加。sensitivity 固定其他参数；如果每点重新优化 mapping，须说明。非单调结果不得擅自平滑。

## 6. 导出

默认 Matplotlib，独立函数解析数据和计算派生指标；JSON 管理字体、配色、轴范围和排序。全篇一致色盲友好配色+marker/线型，连续量用 viridis/cividis，有意义中心才用 diverging。避免 jet、无意义 3D 和装饰。

用 subplots/GridSpec 原生布局，共尺度/图例；输出 PDF/SVG 矢量和 300 dpi PNG。SVG 保留文字，PDF TrueType 嵌字。PNG 转 PDF 不算矢量。

plot.py 内置 area–latency DSE 与单指标组件 breakdown；折线、热图、roofline、校准图需按规则扩展，不声称模板实现所有图类。缺 Matplotlib 的 SVG 后端仅输出 SVG，不代替最终质量检查。

