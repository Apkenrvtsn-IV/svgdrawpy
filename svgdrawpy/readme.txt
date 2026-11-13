
# svgdrawpy


svgdrawpy 是一个用于二维几何构造和 SVG 绘图的 Python 库。程序中先创建点、直线、圆、圆弧、折线等几何对象，再通过 draw() 将这些对象写入 SVG 文件。

svgdrawpy(下简称draw) 可以用来进行一些简单的图形设计工作，相较于视觉效果，draw更关注图形间的几何关系和构造方法，所以也可以用来演示几何图形。

导入包以开始使用：

from svgdrawpy import *


## 坐标系

相较于大多数库的坐标系，draw并没有采用向右向下为正，左上角为原点的方案，draw的坐标系：

- 向右为x轴正方向，向上为y轴正方向
- 旋转和绕行的默认方向为逆时针
- 角度使用弧度制，可以间接地使用角度值，90*deg表示90度
- 建议使用靠近原点的区域绘图，支持负数坐标
- 建议基本几何图形数量级控制在100

之所以这样设计，因为这样的坐标系更“数学”。


## 向量


draw 使用 Vec 表示向量和点，由于向量和点的共通性，不区分向量和点。

定义一个向量：
Vec(100,100)

Vec 允许线性运算，取模（绝对值）.

Vec 常用方法和属性：

.x
.y
.r      # 等价于 abs(self)
.arc    # 向量角度，取值 [0,2*pi)


使用预定义的常量表示原点：
ORIG

两点间可求距离：
p1:Vec
p2:Vec
distance(p1,p2)



## 直线

此处直线为数学含义上的无限长的直线

直线是实现了后定义协议的类型，后定义协议允许你不必在实例化时定义一个对象，而是在实例化后根据对象特征确定它。

实例化直线：
l=Line()

一条直线可以由两个点确定，故可由此定义直线：
l.by_2p(
    Vec(100,0),Vec(0,100)
)

还可以由一般式方程中的参数确定：
l.by_ABC(
    1,1,-100
)   # 表示 1*x+1*y-100=0

一些实例方法，要求必须对象定义后才能使用，在源代码中这些方法以 @should_define 修饰，查看源代码以了解更多。

Vec 常用方法和属性：

.A
.B
.C
.epsl   # 系数弦，定义为 sqrt(A^2+B^2)
.uVec   # 法向量，等于 (A,B)

求点到直线的距离：
p:Vec
l:Line
distance(p,l)



## 命名和引用

将实例化的几何图形赋给变量，可以引用他们。后续在其上的操作都可以以变量名指代他。

除了这种方式，draw还允许你在实例化时传入一个字符串作为他的名称(name)，有名称的图形实例会被加载到实例池中，再次在实例化时传入name以引用这个对象：
Line('1').by_2p(
    ORIG,Vec(100,0)
)
Line('1')   # 上一条直线而非新的实例

不同类型的图形命名空间平行，可以重名。

这种命名引用方式的好处是：
- 字符串作为名称，更灵活，也不受python变量名命名规则限制
- 引用时显式地写明它的类型
- 命名行为是对象式的，命名只是实例化的一个过程，最终返回实例（python赋值是语句而非对象），方便流式处理

也可以实例化之后为图形命名：
Line().set_name('1')



## LineGeo类

LineGeo 是所有几何图形的父类，定义了所有几何图形共有的方法。

LineGeo 的子类：
    Vec         向量或点
    VecSet      向量集/点集
    Line        直线
    Lines       折线组
    Circle      圆
    Arc         弧
    Group       组

LineGeo 定义了控制样式的方法，这些样式会在编译时通过设置属性的方式传给svg标签

设置属性：
Line().set_style(
    {'stroke':'green'}
)

None作为键值对的值时表示删除属性

清空属性：
Line().clear_style()

这两个方法是原地方法，而几何变换相关的方法都是非原地方法。

LineGeo 定义了过滤器方法，当实例满足条件时返回自身，否则返回None（这个方法在VecSet，Group中重写了）：
Vec(100,200).filter(lambda x:distance(x,ORIG)<100)

LineGeo 还定义了print和out，这两个方法在后面流式处理时会用到

一些属性和方法虽然LineGeo没有定义，但它所有的子类都有定义，具备相同的含义：

.style
    样式
.move(self,vec:Vec)
    平移
.rotate(self,theta,p:Vec)
    旋转
.symm_line(self,l:Line)
    关于直线对称
.copy(self)
    拷贝

图形对象的几何变换方法可能不保留样式。


## 后定义协议

前文已说明后定义协议，通过对象特征确定他，用以实现这一行为的方法称为“确定方法”。

draw中所有图形的确定方法都以by_开头，图形被定义后，他的 define 属性变为 True（未定义时为Fasle）。

确定方法应只在图形未定义时使用，尽管代码上并没有对此限制。

确定方法的命名和参数匹配，例如
.by_3p
意为传入三个参数，每个参数都是点(Vec)，并且这三个参数对称性良好。


确定方法中参数的顺序，首先按照重要顺序排序，其次按照类型排序：
int < float < Vec < Line < Circle < Arc < Group
越小越靠左。

确定方法如果可以根据条件确定唯一的对象，那么调用确定方法的对象被定义，相当于原地方法。如果不能确定唯一的对象，可能返回 VecSet 或 Group，而调用方法的实例无变化。


## 圆

圆心和半径定圆：
Circle().by_c_r(ORIG,100)

三点定圆：
Circle().by_3p(p1,p2,p3)

圆还有更多的确定方法。

Circle 常用方法和属性：
.c      圆心
.r      半径

不同的图形间可以求交集（交点），得到 Vec,VecSet或None。LineGeo对求交满足交换律（可行的话）。直线和圆求交：
Circle().by_2p(
    Vec(100,0),ORIG
) & Line().by_2p(
    Vec(50,0),Vec(50,100)
)


## 流式处理

draw可以使用一种不使用赋值语句，同一对象多次调用方法，上一方法返回值作为下一方法调用者的风格：

Line('1').by_2p(
    Vec(100,100),Vec(200,300)
).set_style(
    {'stroke':'green'}
).move(
    Vec(20,20)
)

这是可行的，draw在设计上让所有原地方法正常情况下的返回值都为self，而非原地方法的返回值是处理后的对象，所以可以连贯地写下去。



## 编译函数

draw(elem:Iterable[LineGeo|Comm],filepath,viewbox:str)

该函数用以编译 LineGeo 图形对象，生成svg文件。

无返回值。

elem是待编译的对象列表，除了LineGeo，还允许存在Comm对象，Comm对象用以向svg文件中写入注释。None会被忽略

filepath是文件输出目录，viewbox是视窗，例如 '-500 500 1000 1000'。视窗会影响直线的编译


LineGeo 对象会被转化为 svg标签，对应关系：

Vec         circle
VecSet      g,circle
Line        line
Lines       polyline/polygon
Circle      circle
Arc         path
Group       g,...


在写入这些svg标签时，同时也会写入图形相关的注释，可在svg中查找编译异常时的相关信息。



有时需要一些辅助线性质的图形，他们对于构造图形而言必需，但不希望他出现在画布上，使用.out返回None，以跳过该图形：
draw(
    [
        Vec('A').by_xy(0,200).out(),
        Vec('B').by_xy(10,20).out(),
        Comm('点A和点B不会被绘制在画布上'),
        Line().by_2p(Vec('A'),Vec('B'))
    ],
    ...
)

使用print打印实例同时返回self以不中断流式处理


## 弧

确定方法：
.by_circ_theta(self,circ:Circle, start,stop)

使用 in 来判断点是否在图形上：
p in Arc('name')

Arc 常用方法和属性：
.circle     对应圆
.start      起始角度
.stop       终止角度
.start_Vec  圆心指向起点的向量
.stop_Vec   圆心指向终点的向量
.theta      圆心角



## 折线组

折线组通过若干个点来确定由这些点依次连接起来的折线组：

Lines().include(
    Vec(100,0),Vec(200,20),Vec(100,20),Vec(200,0)
)

所有点存放在 points 属性里。

.set_is_close用以控制最终是否绕回起点：

Lines('1').set_is_close(True)



## Group和VecSet

这两个类型是容器类型，Group存放任意的LineGeo，VecSet存放Vec且去重。

VecSet 可以在实例化时传入组成参数：
VecSet(
    [Vec(0,100*i) for i in range(10)]
)

VecSet 在实例化时有退化规则，VecSet实例化需要一个可迭代对象，当其长度为一时，返回这个元素，长度为零则返回None

VecSet 继承自list，可索引可求长可迭代

.filter作用于其中的点，是非原地方法，返回一个由符合条件的全部点组成的子集


Group不允许实例化时传入组成参数，通过include或extend方法加入元素：
Group().include(
    Line('1'),
    Circle('1')
)

Group本身不继承自list，元素存放在属性 group 中

编译Group实例，本质上是在编译他group的元素




## 附录

向量的方法，other均为 Vec类

.theta(self, other)             求夹角
.is_para(self, other)         判断平行
.mul_in(self,other)             求内积
.mul_out(self,other)            求外积
.unit(self)               单位化

.rotate(self,theta=pi/2,p:Vec=ORIG)
.move(self,vec:Vec)
.mid_line(self,p:Vec)           中垂线
.symm_line(self,l:Line)         
.projVec(self,vec:Vec)          ->Vec 投影
.proj(self,vec:Vec)             ->float 投影

直线的方法：

.W(self,p:Vec)
.near_point(self,p:Vec)
.is_para(self,other:Line)
.symm_line(self,l:Line)
.mid_line(self,l:Line,p:Vec)    ->Line
.mid_lines(self,l:Line)         ->Group
.move(self,v:Vec)
.rotate(self,theta:float,p:Vec)
.clip_x(self,x1,x2)
.clip_y(self,y1,y2)

折线组的方法：

.set_is_close(self,z:bool)
.move(self,vec:Vec)
.rotate(self,theta,p:Vec)
.symm_line(self,l:Line)
.to_line(self,i:int,j=None)
.by_rect(self,p1:Vec,p2:Vec)
.by_npoly_2p(self,n:int,p0:Vec,p1:Vec)
.by_npoly_a_p_theta(self,n:int,a:float,p1:Vec,theta=0,swing=True)


圆的方法：

.W(self,p)
.near_point(self,p:Vec)
.theta_to_Vec(self,theta)
.move(self,vec:Vec)
.rotate(self,theta,p:Vec)
.symm_line(self,l:Line)

圆弧的方法：
.move(self,vec:Vec)
.rotate(self,theta,p:Vec)
.symm_line(self,l:Line)
.oppo_arc(self)


向量确定方法：

.by_xy(self,x,y)
.by_2p_theta(self,p1:Vec,p2:Vec,theta)

直线确定方法：

.by_ABC(self,A:float,B:float,C:float)
.by_2p(self,p1:Vec,p2:Vec)
.by_vec_p(self,uVec:Vec,p:Vec)
.by_theta_p(self,theta,p:Vec)

圆的确定方法：

.by_c_r(self,c:Vec,r)
.by_c_p(self,c:Vec,p:Vec)
.by_3p(self,p1:Vec,p2:Vec,p3:Vec)
.by_2p(self,p1:Vec,p2:Vec)
.by_3line(self,l1:Line,l2:Line,l3:Line)
.by_2line_line(self,l1:Line,l2:Line,*,ls:Line)
.by_3lines(self,l1:Line,l2:Line,l3:Line)
.by_p_2line(self,p:Vec,l1:Line,l2:Line)
.by_2p_line(self,p1:Vec,p2:Vec,l:Line)

弧的确定方法：

.by_circ_theta(self,circ:Circle, start,stop)
.by_2p_theta(self,p1:Vec,p2:Vec,theta, swing=True)
.by_2p_circ(self,p1:Vec,p2:Vec,circ:Circle)


不同图形的初始define：

Vec             False
VecSet          True
Line            False
Lines           True
Circle          False
Arc             False
Group           True


## 将来的变化

如果可能，将在未来的版本加入圆锥曲线等图形。