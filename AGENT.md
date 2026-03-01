# parserasgeo 项目概述

## 项目简介
`parserasgeo` 是一个用于解析 HEC-RAS 几何文件 (.g01) 的 Python 库。HEC-RAS (Hydrologic Engineering Center's River Analysis System) 是美国陆军工程兵团开发的河流分析系统，用于执行水力计算和洪水分析。

## 项目结构
```
parserasgeo/
├── parserasgeo/           # 主要库代码
│   ├── __init__.py       # 导出主要类
│   ├── prg.py            # 主解析器 ParseRASGeo
│   └── features/         # 各种几何要素的解析类
├── test/                 # 测试文件
├── leak.g01              # 示例几何文件
└── ...
```

## 核心功能

### ParseRASGeo 类
- 主要的几何文件解析器
- 读取 .g01 文件并将其转换为 Python 对象
- 提供访问不同几何要素的方法

### 支持的几何要素
- 河流河段 (River Reach)
- 横断面 (Cross Section)
- 涵洞 (Culvert)
- 桥梁 (Bridge)
- 侧堰 (Lateral Weir)
- 蓄水区域 (Storage Area)
- 连接点 (Junction)

## 解析机制
1. 逐行读取几何文件
2. 使用 `test` 方法检测每行是否为特定要素的开始
3. 如果匹配，则创建相应要素对象并导入数据
4. 数据以结构化对象形式存储在 `geo_list` 中

## 代码约定

### 特征类设计模式
每个特征类都遵循相同的接口：
```python
class Feature(object):
    @staticmethod
    def test(line):
        # 判断一行是否为此特征的开始
        pass
    
    def import_geo(self, line, geo_file):
        # 从文件导入此特征的数据
        pass
```

### 文件格式
HEC-RAS 几何文件是文本格式，包含：
- 河流和河段定义
- 横断面数据（包括站点/高程点）
- 结构物定义（桥梁、涵洞、堰等）
- 蓄水区域和其他要素

## 最近的修复
最近修复了一个关键问题：LateralWeir 类在解析过程中没有检测新要素的开始，导致吞噬了后续的 Storage Area 数据。修复方法是：
1. 为 LateralWeir 及其子组件添加 `_is_new_feature` 检查
2. 修改输出方法以避免输出未初始化的 None 值

## 扩展性
该项目设计良好，易于扩展新的几何要素类型。只需：
1. 创建新的特征类，继承基本特征接口
2. 实现 `test` 和 `import_geo` 方法
3. 在主解析器中添加相应的检测逻辑

## 测试
项目包含测试脚本 `test/test_g01.py` 来验证解析功能的正确性。