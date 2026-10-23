# 原生编辑与生命周期

首选 uncompressed .drawio，内部 mxfile/diagram/mxGraphModel/root/mxCell。节点唯一 ID、vertex=1、parent、mxGeometry；边 edge=1、source/target 指真实节点，relative=1。容器是真正 parent 层级，文字存 value，不转曲线；不嵌整张 raster、不锁整图。

diagram.py 从 JSON 输出独立对象及容器，以及 SVG 预览。节点字段 id,label,x,y,w,h,role,parent(可选)。role 支持 group/memory/compute/control/io。子节点坐标相对 parent，边 waypoints 用画布绝对坐标。边 id,source,target,label,kind(data/control)，exit/entry 为 [0..1,0..1]，默认右中到左中。无提供数据不添加虚构容量。

SVG 保留对象 ID 和 text，可在矢量编辑器修改；但普通 SVG 在 draw.io 可能作为单张图片导入，原生 .drawio 才是保证可编辑的主文件。简化 SVG 路由不等于 draw.io 自动路由；投稿预览需从最终原生文件重新导出。

## 人工修改后

1. 人工 .drawio 成为最新真源，读取 ID/坐标/连接后再更新。
2. 不运行旧 JSON 覆盖原生文件，新版本另存。
3. 生成器默认拒绝覆盖，用户明确要求重建才用 --force；禁止自动绕过保护。
4. 保持语义相同实体的 ID，删节点前检查引用边；复杂 XML 保留，不能用简化 schema 重写丢失功能。
5. 在 diagrams.net 中 File → Open From → Device 打开 .drawio；双击改文字，拖动改布局，再 Save As。完成后重新导出 SVG/PDF。

## 数据图

CSV/JSON 是数值真源，Python 是处理与绘图真源，样式 JSON 是样式真源。副本改数据、不同路径输出；手动修饰 SVG 会被重跑覆盖，应把稳定样式迁回代码。

图旁保存 caption.md、metadata.json，包括来源、输入、命令、公式、假设。生成器不能证明电路正确，绘图代码不能证明性能模型可信。

