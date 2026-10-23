# 多精度张量单元与配比

这是领域方法建议，不声称某论文已研究 BF16:FP8:FP4 最佳配比。

结构分系统供数→阵列/PE 组织→单 PE 位级路径。多 mode 保持同布局，用 lane 分组表达拆分/融合，明确共享与新增。按 RTL 画输入拆分、指数处理、乘法、移位对齐、规约、累加、舍入。不能隐藏控制、buffer/collector、交换与规约成本。

格式写 BF16×BF16→FP32、FP8 E4M3×FP4 E2M1→FP32；量化画 group size/block scale 及元数据供给。INT4 composability 不能直接当 FP4 实现。K 路点积与跨周期 K 累加分开，latency 与 II 分开。

1:x:y 先说明是每周期 dense ops、MAC 数、PE 数还是面积预算，并给绝对吞吐；不能只用比例隐藏 BF16 基准下降。固定面积包括 SRAM/寄存器/路由/控制/供数；固定功耗考虑频率、活动率。

供数按有效复用算，不按每 MAC 两个新输入机械相加。标重用域、buffer 容量、广播范围、端口位宽、频率、读写开销。带宽足够不证明无 bank 冲突/依赖；理想与可持续带宽区分。

推荐图组：
1. 同布局 baseline/proposed 微架构。
2. 面积与功耗分面，绝对值与公平条件。
3. area/energy–应用时延可行 Pareto，不只比 TOPS。
4. 配比×context/batch 热图，缺测 mask，prefill/decode 分面。
5. 非重叠瓶颈分解和多层 roofline。
6. 模型对实测校准及适用范围。

CSV 可含 design,ratio,precision_a,precision_b,acc_precision,process_nm,frequency_ghz,area_mm2,power_w,energy_j,latency_ms,workload,batch,context,phase,feasible,seed,source。未知留空。不要由商用峰值倒推未公开微架构或 PPA。

