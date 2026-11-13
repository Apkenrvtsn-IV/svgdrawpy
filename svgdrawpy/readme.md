# svgdrawpy

`svgdrawpy` 是一个用于二维几何构造和 SVG 绘图的 Python 库。它以点、直线、圆、圆弧和折线等对象描述几何关系，并将支持的对象输出为 SVG。它更关注几何构造，而非复杂的视觉排版，适合简单图形设计和几何演示。

## 快速开始

在项目目录的上级目录运行 Python，并导入所需对象：

```python
from svgdrawpy import Circle, Comm, Lines, ORIG, Vec, draw

triangle = Lines().include(
    Vec(0, 100),
    Vec(-86, -50),
    Vec(86, -50),
).set_is_close(True).set_style({
    "stroke": "#176B5B",
    "stroke-width": "3",
})

circle = Circle().by_c_r(ORIG, 120).set_style({
    "stroke": "#D34A3A",
    "stroke-width": "2",
})

draw(
    [Comm("圆和三角形"), circle, triangle],
    filepath="example.svg",
    viewbox="-150 -150 300 300",
)
```

`draw()` 会在指定路径生成 SVG 文件，不返回绘图对象。当前实现需要显式传入 `viewbox`。

源码使用 Python 3.12 的 f-string 语法，需使用 Python 3.12 或更新版本。几何计算使用 Python 标准库和项目自身模块。

## 坐标与角度

- 原点为 `ORIG`，坐标系向右为 x 正方向、向上为 y 正方向，支持负坐标。
- 旋转和圆弧绕行默认按逆时针方向。
- 角度参数使用弧度。`deg` 等于 `pi / 180`，例如 `90 * deg` 表示 90 度。
- `viewbox` 使用 SVG `viewBox` 的四个整数值：`"最小x 最小y 宽度 高度"`，例如 `"-150 -150 300 300"`。
- 输出 SVG 时，绘图器会将 y 坐标取反，以适配 SVG 的坐标方向。
- 绘图时建议使用靠近原点的坐标，并控制几何尺寸的数量级；这是使用建议，不是代码限制。

## 对象定义与命名

几何对象继承自 `LineGeo`，其 `define` 属性表示几何定义是否完成。部分方法要求对象已定义，否则会抛出 `UndefinedError`。以 `by_` 开头的方法通常用于定义几何对象，例如 `by_xy()`、`by_2p()`、`by_c_r()`。

可以在实例化时用字符串命名并在同类型命名空间中引用对象：

```python
Line("x-axis").by_2p(ORIG, Vec(100, 0))
axis = Line("x-axis")
```

也可以在创建后调用 `set_name()` 命名。命名对象存放在共享实例表中；使用已存在的同类型名称会取回该对象。

## 几何类型

| 类型 | 含义 | 常用构造方式 |
| --- | --- | --- |
| `Vec` | 点或向量 | `Vec(x, y)`、`Vec().by_xy(x, y)` |
| `VecSet` | 点集 | `VecSet([p1, p2, ...])` |
| `Line` | 无限长直线 | `Line().by_2p(p1, p2)` |
| `Lines` | 折线或多边形边界 | `Lines().include(p1, p2, ...)` |
| `Circle` | 圆 | `Circle().by_c_r(center, radius)` |
| `Arc` | 圆弧 | `Arc().by_circ_theta(circle, start, stop)` |
| `Group` | 几何对象组合 | `Group().include(obj1, obj2, ...)` |

源码还定义了 `Eclipse` 椭圆参数类，但它未列入包的 `__all__`，也没有对应的 SVG 绘制分支；目前不属于可通过 `draw()` 绘制的类型。

### Vec

`Vec` 同时表示点和向量，支持加减、数乘、取模、点积、叉积、求夹角、投影、旋转和平移。

- `.x`、`.y`：坐标分量。
- `.r`：向量长度，等价于 `abs(vec)`。
- `.arc`：相对正 x 轴的角度，范围为 `[0, 2*pi)`；零向量没有定义方向。
- `rVec(r, theta)`：按长度和角度创建向量。
- `distance(p1, p2)`：计算支持类型之间的距离。

```python
from svgdrawpy import Vec, distance

p = Vec(3, 4)
q = Vec(0, 0)
length = abs(p)
direction = p.unit()
gap = distance(p, q)
```

### Line

`Line` 表示无限长直线。可通过两个点或一般式 $Ax + By + C = 0$ 定义：

```python
line = Line().by_2p(Vec(100, 0), Vec(0, 100))
line = Line().by_ABC(1, 1, -100)
```

常用属性包括 `.A`、`.B`、`.C`、`.uVec`（法向量）和 `.epsl`（系数向量长度，`sqrt(A**2 + B**2)`）。点到直线的距离可用 `distance(point, line)` 求得。

`clip_x(x1, x2)` 和 `clip_y(y1, y2)` 可将直线转换为指定坐标区间内的线段；对无法用对应坐标区间表示的水平或竖直直线会抛出 `GeoError`。

### Circle 与 Arc

圆的常用构造方式：

```python
Circle().by_c_r(ORIG, 100)
Circle().by_3p(p1, p2, p3)
```

圆的 `.c` 是圆心，`.r` 是半径。圆弧可由圆和起止角构造；`by_circ_theta()` 按从起始角到结束角的逆时针方向定义圆弧。`by_2p_theta()` 可由两个端点及圆心角构造弧。

`Arc` 的 `.start`、`.stop` 为起止角，`.start_Vec`、`.stop_Vec` 为圆心指向起止点的向量，`.theta` 为圆心角。可以用 `point in geometry` 判断点是否属于圆或圆弧；边界判断使用项目中的距离容差。

### Lines

`Lines` 依次连接 `points` 中的点。默认是开放折线，使用 `set_is_close(True)` 闭合并在 SVG 中输出为多边形。可用 `by_rect(p1, p2)` 创建矩形，或用 `by_npoly_2p(n, center, first_vertex_vector)` 创建正多边形。

### VecSet 与 Group

`VecSet` 只保存 `Vec`，插入时按点相等规则去重，并可索引、求长度和迭代。构造结果会按元素数量退化：零个有效点返回 `None`，一个点返回该 `Vec`，多个点才返回 `VecSet`。它继承自 `list`，因此仍可通过列表方法修改。

`Group` 在 `.group` 属性中保存 `LineGeo` 对象，可用 `include()` 或 `extend()` 加入对象；非 `LineGeo` 对象会被忽略。绘制组时，绘图器递归绘制其中的对象。

## 交集

支持的几何组合可使用 `&` 求交点，结果依交点数返回 `Vec`、`VecSet` 或 `None`。例如：

```python
circle = Circle().by_2p(Vec(100, 0), ORIG)
line = Line().by_2p(Vec(50, 0), Vec(50, 100))
intersection = circle & line
```

交集只对源码实际实现的类型组合可用，并非任意两个 `LineGeo` 对象都支持，也不保证所有组合都可交换。多个交点时可使用 `VecSet.filter()` 按几何条件筛选。

## 样式、过滤与流式调用

`set_style()` 将 SVG 属性应用到对象；值为 `None` 的属性会被移除。`clear_style()` 清除显式样式，绘制时会使用类型默认样式。`VecSet.set_style()` 和 `Group.set_style()` 会将样式应用到容器内的对象。

```python
line = Line().by_2p(
    Vec(100, 100), Vec(200, 300)
).set_style({
    "stroke": "green",
    "stroke-width": "2",
})
```

多数构造和样式方法可链式调用。`print()` 打印对象并返回自身；`out()` 返回 `None`，可把辅助对象从绘图列表中排除。`filter()` 在 `LineGeo` 中筛选单个对象，在 `VecSet` 和 `Group` 中筛选容器元素。

几何变换通常返回新对象；**变换结果是否保留原对象样式依具体方法而定**，当前不应假设样式一定被复制。

## SVG 输出

```python
draw(elem, filepath, viewbox)
```

- `elem`：可迭代对象，包含几何对象、`Comm` 注释对象或 `None`。
- `filepath`：输出 SVG 文件路径。
- `viewbox`：必填字符串，格式为四个整数：`"min_x min_y width height"`。

支持的 SVG 输出对应关系：

| 对象 | SVG 元素 |
| --- | --- |
| `Vec` | `circle` |
| `VecSet` | `g`，包含点标记 |
| `Line` | `line` |
| `Lines` | `polyline` 或 `polygon` |
| `Circle` | `circle` |
| `Arc` | `path` |
| `Group` | `g`，包含子对象 |
| `Comm` | XML 注释 |

`None` 不会作为图形绘制，但会写入一条说明注释。直线输出受 `viewbox` 影响；绘图器会先求直线与包围视窗的辅助圆的交点，再写入 SVG。无法编译的对象也会尝试写入说明注释。

`Comm` 内容会对 `--` 做替换处理，但 XML 属性值目前是直接拼接的；样式值包含 `&`、引号等特殊字符时可能生成无效 SVG。注释文本也不应以单个 `-` 结尾。

## 公开便捷对象

包公开了 `ORIG`、`deg`、`pi`、`rVec()`、`distance()`、`distance_eps`、`theta_eps`、`xyLine` 和 `xyLines` 等名称。`xyLine` 表示主坐标轴，`xyLines` 表示次网格线；可按需将它们放入 `draw()` 的对象列表。
