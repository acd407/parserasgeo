# Parserasgeo

解析 HEC-RAS 几何文件 - 导入/导出 [HEC-RAS](https://www.hec.usace.army.mil/software/hec-ras/) 几何文件。

Parserasgeo 是一个 Python 库，用于导入、编辑和导出 HEC-RAS 几何文件，可用于自动化敏感性分析、蒙特卡洛分析以及任何需要以编程方式更改 RAS 几何的工作流程。Parserasgeo 是一个正在开发中的项目，但其大部分横截面功能已经存在。无法理解的行将作为文本存储，并在导出几何时重新写入。Parserasgeo 已知可在 Python 2 中工作，也应该可以在 Python 3 中工作。

HEC-RAS 模型可以使用 [rascontrol](https://github.com/mikebannis/rascontrol) 自动运行。

---

## 关于此分支

这是 [mikebannis/parserasgeo](https://github.com/mikebannis/parserasgeo) 的一个积极维护的分支，托管在 [chunyaoyang/parserasgeo](https://github.com/chunyaoyang/parserasgeo)。

### 主要更改：
- 用 `pyflow.py` 替换了 `uflow.py`，提供对稳态（`*.f??`）和非稳态（`*.u??`）流量数据的统一支持。
- 增强了 `pyplan.py`，支持读取和写入其他计划文件内容和元数据。
- 更新了 `pyprj.py`，添加了以编程方式插入项目文件条目和更改活动计划设置的新方法。
- 改进了格式化、解析稳健性和文件导出支持。

此分支将继续开发并欢迎贡献。

---

## 开始使用

Parserasgeo 最容易从 GitHub 安装：

```bash
git clone https://github.com/chunyaoyang/parserasgeo.git
cd parserasgeo
pip install .
```

---

## 支持的文本块结构

ParseRASGeo 目前支持以下文本块结构：

1. **RiverReach** - 河流/河段
2. **CrossSection** - 横截面
3. **Culvert** - 涵洞
4. **Bridge** - 桥梁
5. **LateralWeir** - 侧堰
6. **InlineWeir** - 内堰
7. **Junction** - 节点
8. **StorageArea** - 存储区域

对于无法识别的文本行（如 "Geom Title"、"Program Version" 等），会将其作为原始文本存储在 geo_list 中，并在导出时原样写回。

---

## 示例

### 编辑几何文件

打开模型，将所有曼宁糙率值增加 50%，并将几何保存为新文件。

```python
import parserasgeo as prg

geo = prg.ParseRASGeo('my_model.g01')

for xs in geo.get_cross_sections():
    n_vals = xs.mannings_n.values 
    new_n = [(station, n*1.5, other) for station, n, other in n_vals]
    xs.mannings_n.values = new_n

geo.write('my_model.g02')
```

### 读取和修改计划文件（`prplan`）

```python
from parserasgeo import prplan

plan = prplan.ParseRASPlan("example.p01")
print(plan.plan_title)
print(plan.geo_file)

# 修改计划标题
plan.plan_title = "修改后的计划标题"
plan.write("example_modified.p01")
```

### 向稳态流量文件添加内部变化线（`prflow`）

```python
from parserasgeo import prflow

flow = prflow.SteadyFlow("example.f01")
flow.add_internal_change_line(river_station=2000.0, ws_change=1.5)
flow.export("example_modified.f01")
```

### 修改和添加项目文件条目（`prprj`）

```python
from parserasgeo import prprj

project = prprj.ParseRASProject("example.prj")

# 添加新的几何、流量和计划文件条目
project.insert_entry(["g03", "f03", "p03"])

# 将当前计划更改为 p02
project.change_plan("02")

project.write("example_modified.prj")
```

---

## 贡献

虽然目前功能正常，但这是一个正在进行中的工作。欢迎提交写得好且经过测试的拉取请求。

这个库的目标之一是导出的几何文件与原始几何文件完全匹配。这允许通过比较原始几何文件和从 parserasgeo 导出的文件（假设没有进行任何更改）来轻松测试新功能。