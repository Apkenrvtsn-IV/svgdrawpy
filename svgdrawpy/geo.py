from __future__ import annotations
from math import *
from typing import Iterable,Callable,Self,Literal,Any,Type

from .tools import *

distance_eps=1e-5
theta_eps=1e-5

def init_deco(cls_name):
    def wrapp(func):
        def wrap(self,*arg,**kwds):
            if hasattr(self,'init_done'):
                if cls_name in self.init_done:
                    return None
            else:
                self.init_done=[]
            self.init_done.append(cls_name)
            return func(self,*arg,**kwds)
        return wrap
    return wrapp


def should_define(func):
    '''后定义协议
    一个类允许在初始化时不做行为，而是通过一些方法之后定义，
    在实质的定义行为之前，对象不能使用他的一些需要定义的方法，例如
    一条直线必须定义才能求某一点到他的距离
    对于这些方法，使用该函数做装饰器，在调用方法时检查对象的define属性（布尔值）
    经定义才可调用
    '''
    def wrap(self:LineGeo,*arg,**kwds):
        if self.define:
            return func(self,*arg,**kwds)
        else:
            raise UndefinedError(
                f'{type(self)}对象没有定义，不能使用{func.__name__}方法'
            )
    return wrap


class LineGeo:
    obj:dict[str,LineGeo]={}
    default_style=dict()

    def __new__(cls,name:str|None=None):
        if name is not None:
            if f"{cls.__name__}:{name}" in cls.obj:
                return cls.obj[f"{cls.__name__}:{name}"]
        return super().__new__(cls)

    
    @init_deco(__qualname__)
    def __init__(self,name:str|None=None):
        self.name=name
        if name:
            self.obj[f"{type(self).__name__}:{name}"]=self
        self.define=False
        self.style=type(self).default_style.copy()

    # region
    def __repr__(self):
        if self.define:
            return (
                f"{type(self).__name__} {'未命名' if self.name is None else self.name}: "
            )
        else:
            return f"undefined {type(self).__name__} {self.name}"
        
    def set_style(self,dict:dict[str,str|None])->Self:
        self.style|=dict
        self.style={k:v for k,v in self.style.items() if v is not None}
        return self

    def clear_style(self)->Self:
        self.style=type(self).default_style.copy()
        return self
    
    def set_name(self,name:str)->Self:
        self.name=name
        self.obj[f"{type(self).__name__}:{name}"]=self
        return self

    @should_define
    def __and__(self, other):
        return self

    @should_define
    def __or__(self, other):
        return NotImplemented
    
    def __rand__(self, other):
        return self.__and__(other)
    def __ror__(self, value):
        return self.__or__(value)

    def print(self)->Self:
        print(self)
        return self
    def out(self)->None:
        return None

    def filter(self,func:Callable[[Type[Self]],bool])->Self|None:
        if func(self):
            return self
        else:
            return None
    '''
    LineGeo 的子类要实现三个基本变换方法：
    move(self,vec)          平移
    rotate(self,theta,p)    旋转
    symm_line(self,l)       对称（关于直线）

    这三个方法都默认对象已定义，
    '''
    # endregion

# 时间：2026 年 11 月 13 日 19:57:35
class Vec(LineGeo):
    default_style={
        "fill":"white",
        "r":2
    }
    
    def __new__(cls,x:float|str=None,y:float=None)->Vec:
        if y is None:
            return super().__new__(cls,x)
        else:
            return object.__new__(cls)

    @init_deco(__qualname__)
    def __init__(self,x:float|str=None,y:float=None):
        if y is None:
            if isinstance(x,str):
                super().__init__(x)
            else:
                super().__init__()
        else:
            super().__init__()
            self.by_xy(x,y)

    # region
    def __eq__(self, value):
        if isinstance(value,Vec):
            return abs(self-value)<distance_eps
        else:
            return False

    def __repr__(self):
        return 'Vec(%d,%d)'%(self.x,self.y)

    @property
    @should_define
    def r(self):
        return sqrt((self.x)**2+(self.y)**2)

    @property
    @should_define
    def arc(self):
        # 返回 角，0 到 2pi
        if self.y>=0:
            return acos(self.x/self.r)
        else:
            return 2*pi-acos(self.x/self.r)

    @should_define
    def __add__(self, other:Vec)->Vec:
        return Vec(self.x+other.x,self.y+other.y)

    @should_define
    def __sub__(self, other:Vec)->Vec:
        return self+(-other)

    @should_define
    def __pos__(self)->Vec:
        return Vec(self.x,self.y)

    @should_define
    def __neg__(self)->Vec:
        return Vec(-self.x,-self.y)

    @should_define
    def __mul__(self, other:float)->Vec:
        return Vec(self.x*other,self.y*other)

    @should_define
    def __rmul__(self, other:float)->Vec:
        return self*other

    @should_define
    def __truediv__(self, other:float)->Vec:
        return self*(1/other)

    @should_define
    def __abs__(self):
        return self.r

    @should_define
    def copy(self):
        return +self

    @should_define
    def mul_in(self,other:Vec):
        # 内积，即点乘积
        return self.x*other.x+self.y*other.y

    @should_define
    def mul_out(self,other:Vec):
        # 外积，即叉乘积
        return self.x*other.y-self.y*other.x

    @should_define
    def theta(self,other:Vec):
        # 求夹角，返回 0到pi 的弧度制角度
        return acos(self.mul_in(other)/(abs(self)*abs(other)))

    @should_define
    def is_para(self,other:Vec):
        # 判断两向量是否平行，返回 True 则为平行
        return (
            self.theta(other)<theta_eps
            or abs(pi-self.theta(other))<theta_eps
        )

    @should_define
    def unit(self):
        # 单位化
        return Vec(
            self.x/self.r,self.y/self.r
        )

    
    @should_define
    def distance(self,other:Vec):
        if isinstance(other,Vec):
            return sqrt((self.x-other.x)**2+(self.y-other.y)**2)
        return NotImplemented

    @should_define
    def rotate(self,theta=pi/2,p:Vec=None)->Vec:
        # 应用于点的旋转
        if p is None:
            return Vec(
                self.x*cos(theta)-self.y*sin(theta),
                self.x*sin(theta)+self.y*cos(theta)
            )
        
        else:
            return (self-p).rotate(theta)+p



    @should_define
    def mid_line(self,p:Vec)->Line:
        # 中垂线
        return (
            Line().by_vec_p(
                self-p,(self+p)/2
            )
        )

    @should_define
    def symm_line(self,l:Line):
        # 返回关于直线对称的点
        return (
            self-2*l.uVec.unit()*sgn(l.W(self))*l.distance(self)
        )

    @should_define
    def projVec(self,vec:Vec)->Vec:
        # 投影向量
        # self投影到向量 Vec上
        return self.proj(vec)*vec.unit()

    @should_define
    def proj(self,vec:Vec)->float:
        return self.mul_in(vec)/abs(vec)

    @should_define
    def move(self,vec:Vec)->Vec:
        return self+vec

    def by_xy(self,x,y)->Self:
        self.x=x
        self.y=y
        self.define=True
        return self

    def by_2p_theta(self,p1:Vec,p2:Vec,theta)->Vec:
        x= (
            (p1+p2)/2+(p2-p1).rotate().unit()*distance(p1,p2)/(2*tan(theta/2))
        )
        return self.by_xy(x.x,x.y)

    @staticmethod
    def check_para(*p:Vec,mode='all')->bool:
        '注意，p应理解成点'
        # 检查点是否共线
        # 所有点都共线时才返回True
        for i in range(2,len(p)):
            if not (p[i]-p[0]).is_para(p[1]-p[0]):
                return False
        else:
            return True

    # endregion

def rVec(r,theta):
    return Vec(r*cos(theta),r*sin(theta))
    
ORIG=Vec(0,0) #原点



class VecSet(LineGeo,list[Vec]):
    default_style=dict()


    def __new__(cls,iterable:Iterable[Vec]|str)->VecSet|Vec|None:
        if isinstance(iterable,str):
            return super().__new__(cls,iterable)
        x=list.__new__(cls)
        x.__init__(iterable)

        if len(x)==0:
            return None
        if len(x)==1:
            return x[0]
        else:
            return x

    @init_deco(__qualname__)
    def __init__(self, iterable:Iterable[Vec]|str):
        # VecSet被设计成只读，应在实例化时传参
        # 未定义 include 方法
        if isinstance(iterable,str):
            super().__init__(iterable)
            iterable=[]
        else:
            super().__init__()
        list.__init__(self,[])

        for i in iterable:
            if isinstance(i,Vec):
                if i not in self:
                    self.append(i)
            elif i is None:
                continue
            else:
                raise TypeError(
                    f'VecSet只能包含Vec对象，但你传入了{i}，它是{type(i)}'
                )
        self.define=True

    def __repr__(self):
        return super().__repr__()+f'have {len(self)} LineGeo(s)'
    
    def copy(self):
        return VecSet(self)

    def __and__(self, value):
        if isinstance(value,VecSet):
            l=[]
            for i in self:
                if i in value:
                    l.append(i)
            return VecSet(l)
        else:
            return NotImplemented
    
    def __or__(self, value):
        if isinstance(value,VecSet):
            l=list(self)
            l.extend(value)
            return VecSet(l)
        else:
            return NotImplemented

    def filter(self,func:Callable[[Vec],bool])->VecSet|Vec|None:
        l=[]
        for i in self:
            if func(i):
                l.append(i)
        return VecSet(l)

    def __sub__(self, other):
        if isinstance(other,VecSet):
            l=[]
            for i in self:
                if i not in other:
                    l.append(i)
            return VecSet(l)
        else:
            return NotImplemented
    
    def set_style(self, dict):
        for i in self:
            i.set_style(dict)
        return self

    def clear_style(self):
        for i in self:
            i.clear_style()
        return self

    def move(self,vec:Vec):
        l=[]
        for i in self:
            l.append(i.move(vec))
        return VecSet(l)

    def rotate(self,theta:float,p:Vec=ORIG):
        l=[]
        for i in self:
            l.append(i.rotate(theta,p))
        return VecSet(l)

    def symm_line(self,l:Line):
        l_=[]
        for i in self:
            l_.append(i.symm_line(l))
        return VecSet(l_)
    

class UndefinedError(Exception):
    pass

class GeoError(Exception):
    '几何错误'


class Line(LineGeo):
    # 直线
    default_style={
        "fill":"none",
        "stroke":"red"
    }
    def __repr__(self):
        if self.define:
            return super().__repr__()+"%.2f*x+%.2f*y+%.2f=0"%(self.A,self.B,self.C)
        else:
            return super().__repr__()
    @should_define
    def copy(self):
        return (
            Line().set_style(
                self.style
            ).by_ABC(
                self.A,self.B,self.C
            )
        )
        
    def by_ABC(self,A:float,B:float,C:float):
        # 由一般式方程中的系数确定一条直线
        self.A=A
        self.B=B
        self.C=C
        self.epsl=sqrt(self.A**2+self.B**2)
        # uVec 表示法向量
        if self.epsl==0:
            raise GeoError(
                f'直线的法向量不能为零向量，但你传入了A={A},B={B},C={C}'
            )
        self.uVec=Vec(self.A,self.B)
        self.define=True

        return self
    
    def by_2p(self,p1:Vec,p2:Vec):
        # 由被穿过的两个点确定一条直线
        if p1==p2:
            raise GeoError('直线的两个点不能重合，但你传入了%s和%s'%(p1,p2))
        x= (p1-p2).rotate()
        A,B=x.x,x.y
        C=-(A*p1.x+B*p1.y)
        return self.by_ABC(A,B,C)

    def by_vec_p(self,uVec:Vec,p:Vec):
        # 由法向量和被穿过的点确定一条直线
        if uVec==ORIG:
            raise GeoError(
                f'直线的法向量不能为零向量，但你传入了{uVec}'
            )
        return self.by_2p(p+uVec.rotate(),p)
    
    def by_theta_p(self,theta,p:Vec):
        # 由倾斜角和被穿过的点确定一条直线
        return self.by_2p(p,p+rVec(100,theta))


    @should_define
    def W(self,p:Vec):
        # W值，
        return self.A*p.x+self.B*p.y+self.C

    @should_define
    def near_point(self,p:Vec):
        # 直线上到p点最近的点
        return p-distance(p,self)*self.uVec.unit()*sgn(self.W(p))
    
    @should_define
    def is_para(self,other:Line)->bool:
        return self.uVec.is_para(other.uVec)

    @should_define
    def distance(self,other:Vec|Line):
        if isinstance(other,Vec):
            return abs(self.W(other))/self.epsl
        elif isinstance(other,Line):
            if self.is_para(other)==False:
                # 即使判断平行也不能求距，直线距离的误差无法估计
                # ，可能会造成难以想象的后果
                return NotImplemented
        return NotImplemented


    @should_define
    def __and__(self, other:LineGeo)->Vec|None|VecSet:
        if isinstance(other,Line):
            # 求两直线交点
            if self.is_para(other):
                return None
            return Vec(
                -(self.C*other.B-self.B*other.C)/self.uVec.mul_out(other.uVec),
                -(self.A*other.C-self.C*other.A)/self.uVec.mul_out(other.uVec)
            )
        else:
            return NotImplemented

    @should_define
    def __contains__(self, item):
        if isinstance(item,Vec):
            return distance(item,self)<distance_eps
        else:
            return NotImplemented

    @should_define
    def symm_line(self,l:Line):
        return Line().by_theta_p(
            2*es(l.uVec.arc)-es(self.uVec.arc)+pi/2,self&l
        )

    @should_define
    def mid_line(self,l:Line,p:Vec)->Line:
        # 求两直线夹角的角平分线，返回的直线使得
        # 直线和点p在两直线的同一区域
        if p in l or p in self:
            raise GeoError(
                f'mid_line的点不能在两条直线上，但{p}在直线' \
                f'{str(self) if p in self else ""}'\
                f'{str(l) if p in l else ""}'\
                '上'
            )
        return self.mid_lines(l).filter(
            lambda x:Line.sgnWs(p,self,l)
                ==Line.sgnWs(p.symm_line(x),self,l)
        )
    
    @should_define
    def mid_lines(self,l:Line)->Group:
        # 求两直线夹角的角平分线，返回值使得
        # 由self逆时针旋转到l过程中可与返回值直线重合
        return Group().include(
            Line().by_theta_p(
                (es(self.uVec.arc)+es(l.uVec.arc))/2-pi/2,
                self&l
            ),
            Line().by_theta_p(
                (es(self.uVec.arc)+es(l.uVec.arc))/2,
                self&l
            )
        )
    
    @should_define
    def rotate(self,theta:float,p:Vec)->Line:
        # 绕点旋转
        return Line().by_vec_p(
            self.uVec.rotate(theta),
            self.near_point(p).rotate(theta,p)
        )

    @should_define
    def clip_x(self,x1,x2)->Lines:
        # 裁剪成线段
        if self.uVec.is_para(Vec(100,0)):
            raise GeoError(
                '直线%s是铅直线，不能裁剪成x区间[%d,%d]的线段'%(self,x1,x2)
            )
        return (
            Lines().include(
                Vec(x1,-(self.A*x1+self.C)/self.B),
                Vec(x2,-(self.A*x2+self.C)/self.B)
            )
        )

    @should_define
    def clip_y(self,y1,y2)->Lines:
        # 裁剪成线段
        if self.uVec.is_para(Vec(0,100)):
            raise GeoError(
                '直线%s是水平线，不能裁剪成y区间[%d,%d]的线段'%(self,y1,y2)
            )
        return (
            Lines().include(
                Vec(-(self.B*y1+self.C)/self.A, y1),
                Vec(-(self.B*y2+self.C)/self.A, y2)
            )
        )

    @should_define
    def move(self,v:Vec):
        d=v.proj(self.uVec)
        temp=self.copy()
        temp.C=self.C-d*self.epsl
        temp.define=True
        return temp

    @staticmethod
    def check_para(*l:Line)->bool:
        # 检查是否平行
        # 共线时，或有几个点重合时，返回True
        # 否则返回False
        return Vec.check_para(
            *[ORIG,*map(lambda x:x.uVec,l)]
        )

    @staticmethod
    def sgnWs(p:Vec,*l:Line)->list[Literal[-1,1,0]]:
        return [sgn(i.W(p)) for i in l]

    

class Lines(LineGeo):
    # 折线组
    default_style={
        "fill":"none",
        "stroke":"red"
    }
    @init_deco(__qualname__)
    def __init__(self,name=None):
        super().__init__(name)
        self.points:list[Vec]=[]
        self.define=True
        self.is_close=False # 是否闭合

    def __repr__(self):
        if self.define:
            return super().__repr__()+f"have {len(self.points)} Vec(s) {"closed" if self.is_close else "" }"
        else:
            return super().__repr__()

    @should_define
    def copy(self):
        return (
            Lines().set_style(
                self.style
            ).extend(
                self.points
            ).set_is_close(
                self.is_close
            )
        )

    @should_define
    def move(self,mov:Vec):
        l=Lines()
        for i in range(len(self.points)):
            l.points.append(self.points[i]+mov)
        l.is_close=self.is_close
        return l

    @should_define
    def rotate(self,theta,p):
        l=Lines()
        for i in range(len(self.points)):
            l.points.append(self.points[i].rotate(theta,p))
        l.is_close=self.is_close
        return l

    def extend(self,l:Iterable[Vec]):
        self.points.extend(l)
        return self

    def include(self,*sth):
        return self.extend(sth)

    @should_define
    def symm_line(self,line:Line):
        l=Lines()
        for i in range(len(self.points)):
            l.points.append(self.points[i].symm_line(line))
        l.is_close=self.is_close
        return l
        

    def set_is_close(self,z:bool)->Self:
        self.is_close=z
        return self

    @should_define
    def to_line(self,i:int,j=None):
        # 将某条线段连成直线
        # 使用索引为i和j的点，j默认为i+1
        if j is None:
            j=i+1
            if j==len(self.points):
                j=0
        return (
            Line().by_2p(
                self.points[i],self.points[j]
            )
        )

    @staticmethod
    def _in_line(p_c:Vec,p1:Vec,p2:Vec)->bool:
        return (
            distance(p_c,p1)+distance(p_c,p2)-distance(p1,p2)
            <distance_eps
        )

    @should_define
    def __contains__(self, item):
        if isinstance(item,Vec):
            for i in range(len(self.points)-1):
                if Lines._in_line(item,self.points[i],self.points[i+1]):
                    return True
            else:
                return False
        else:
            return NotImplemented

    @should_define
    def __and__(self, other)->Vec|VecSet|None:
        if isinstance(other,LineGeo):
            points=list()

            for i in range(len(self.points)):
                if i==len(self.points)-1:
                    if not self.is_close:
                        break
                l_=Line().by_2p(
                    self.points[i],self.points[(i+1)%len(self.points)]
                )

                p=l_&other
                if p is None:
                    continue
                if isinstance(p,Vec):
                    p=[p]
                
                if isinstance(p,(VecSet,list)):
                    for x in p:
                        if Lines._in_line(x,self.points[i],
                        self.points[(i+1)%len(self.points)]):
                            points.append(x)

            return VecSet(points)
        else:
            return NotImplemented


    def by_rect(self,p1:Vec,p2:Vec)->Self:
        minx,maxx=min(p1.x,p2.x),max(p1.x,p2.x)
        miny,maxy=min(p1.y,p2.y),max(p1.y,p2.y)
        return self.include(
            Vec(minx,miny),
            Vec(maxx,miny),
            Vec(maxx,maxy),
            Vec(minx,maxy),
        ).set_is_close(True)
    

    def by_npoly_2p(self,n:int,p0:Vec,p1:Vec):
        # 返回正n边形，p0是中心的坐标，p1是
        # 中心指向第一个顶点的向量
        d_theta=2*pi/n
        return self.include(
            *[
                p0+p1.rotate(i*d_theta)
                for i in range(int(n))
            ]
        ).set_is_close(True)

    def by_npoly_a_p_theta(self,n:int,a:float,p1:Vec,theta=0,swing=True):
        # 返回正n边形，a是边长，p1是第一个顶点的位置，theta是
        # 第一个顶点指向第二个顶点的向量的角度
        # swing为True为逆时针绕向，否则为顺时针绕向
        swing=(1 if swing else -1)
        v=-rVec(a/(2*sin(pi/n)),theta+swing*(pi/2-pi/n))
        return self.by_npoly_2p(
            n,p1-v,v
        )


class Circle(LineGeo):
    default_style={
        "fill":"none",
        "stroke":"red"
    }
    def __repr__(self):
        if self.define:
            return (
                super().__repr__()+
                '(%d,%d), r=%d'%(
                    self.c.x,self.c.y,self.r
                )
            )
    
    @should_define
    def copy(self):
        return (
            Circle().set_style(
                self.style
            ).by_c_r(
                self.c,self.r
            )
        )


    def by_c_r(self,c:Vec,r)->Self:
        # 通过圆心和半径确定一个圆
        self.c=c
        self.r=r
        self.define=True
        return self
    
    def by_c_p(self,c:Vec,p:Vec)->Self:
        # 通过圆心和圆上的一点来确定一个圆
        return self.by_c_r(c,distance(c,p))
    
    def by_3p(self,p1:Vec,p2:Vec,p3:Vec)->Self:
        # 通过圆上的三个点来确定一个圆
        if Vec.check_para(p1,p2,p3):
            raise GeoError(
                '用以确定圆的三个点不能共线' \
                f'但{p1}，{p2}和{p3}共线了'
            )
        A=(p2-p1).theta(p3-p1)
        B=(p1-p2).theta(p3-p2)
        C=(p2-p3).theta(p1-p3)
        r=(
            (sin(2*A)*p1+sin(2*B)*p2+sin(2*C)*p3)/
            (sin(2*A)+sin(2*B)+sin(2*C))
        )
        return self.by_c_p(r, p2)
    
    def by_2p(self,p1:Vec,p2:Vec)->Self:
        # 通过直径上的两个端点来确定
        return self.by_c_p((p1+p2)/2,p1)

    def by_3line(self,l1:Line,l2:Line,l3:Line)->Self:
        # 通过三条切线确定一个圆
        # 事实上，三条切线一般可以确定四个圆
        # 这个方法确定的圆相当于直线交点构成三角形的内切圆
        if l1.is_para(l2) or l1.is_para(l3) or l3.is_para(l2):
            raise GeoError(
                '通过三条切线确定一个圆，并使圆在直线交点组成的'\
                '三角形内时，三条直线应互不平行，但直线' \
                f'{l1},{l2},{l3}其中有平行线'
            )
        p1,p2,p3=l2&l3,l1&l3,l2&l1
        if p1==p2:
            raise GeoError(
                '通过三条切线确定一个圆，并使圆在直线交点组成的'\
                '三角形内时，三条直线不能交于同一点，但直线' \
                f'{l1}，{l2}和{l3}相交于同一点{p1}'
            )

        d1,d2,d3=distance(p2,p3),distance(p1,p3),distance(p1,p2)
        return self.by_c_r(
            (d1*p1+d2*p2+d3*p3)/(d1+d2+d3),
            abs((p2-p1).mul_out(p3-p1))/(d1+d2+d3)
        )

    def by_2line_line(self,l1:Line,l2:Line,*,ls:Line)->Self:
        # 这个方法确定的圆的圆心和三角形的重心
        # 在l1,l2同侧，在ls异侧
        if l1.is_para(l2) or l1.is_para(ls) or ls.is_para(l2):
            raise GeoError(
                '通过三条切线确定一个圆，并使圆在直线交点组成的'\
                '三角形外时，三条直线应互不平行，但直线' \
                f'{l1},{l2},{ls}其中有平行线'
            )
        p2,p1,ps=l2&ls,l1&ls,l2&l1
        if p1==p2:
            raise GeoError(
                '通过三条切线确定一个圆，并使圆在直线交点组成的'\
                '三角形内时，三条直线不能交于同一点，但直线' \
                f'{l1}，{l2}和{ls}相交于同一点{p1}'
            )

        W_sgn=Line.sgnWs((p1+p2+ps)/3,l1,l2,ls)
        W_sgn[-1]=-W_sgn[-1]
        for i in l1.mid_lines(ls).group:
            for j in l2.mid_lines(ls).group:
                p=i&j
                if Line.sgnWs(p,l1,l2,ls)==W_sgn:
                    return self.by_c_r(
                        p,distance(p,ls)
                    )

    def by_3lines(self,l1:Line,l2:Line,l3:Line):
        if Line.check_para(l1,l2,l3):
            raise GeoError(
                '通过三条切线确定一个圆，三条直线不应都平行，但直线' \
                f'{l1},{l2},{l3}都平行'
            )
        spl=None
        if l1.is_para(l2):
            spl=l3
            pl1,pl2=l1,l2
        elif l1.is_para(l3):
            spl=l2
            pl1,pl2=l1,l3
        elif l2.is_para(l3):
            spl=l1
            pl1,pl2=l2,l3
        if spl is None:
            # 都不平行的情况
            return Group().include(
                Circle().by_3line(l1,l2,l3),
                Circle().by_2line_line(l1,l2,ls=l3),
                Circle().by_2line_line(l1,l3,ls=l2),
                Circle().by_2line_line(l3,l2,ls=l1),
            )
        else:
            # 有一组平行线
            li=[]
            for l_1 in spl.mid_lines(pl1).group:
                for l_2 in spl.mid_lines(pl2).group:
                    l_1:Line
                    if l_1.is_para(l_2):
                        continue
                    li.append(l_1&l_2)

            return Group().include(
                Circle().by_c_r(
                    li[0], distance(li[0],spl)
                ),
                Circle().by_c_r(
                    li[1], distance(li[1],spl)
                )
            )

    def by_p_2line(self,p:Vec,l1:Line,l2:Line)->Self:
        # 通过一个在圆上的点和两条切线确定一个圆
        p2=p.symm_line(l1.mid_line(l2))
        if (sgn(l1.W(p2)),sgn(l1.W(p2)))!=(sgn(l1.W(p)),sgn(l1.W(p))):
            p2=2*(l1&l2)-p2
        if p==p2:
            # 点刚好在角平分线上
            return Group().include(
                Circle().by_3line(
                    l1,l2,Line().by_2p(
                        l1&l2,p
                    ).rotate(pi/2,p)
                ),
                Circle().by_2line_line(
                    l1,l2,ls=Line().by_2p(
                        l1&l2,p
                    ).rotate(pi/2,p)
                )
            )
        
        return self.by_2p_line(
            p,p2,l1
        )

    def by_2p_line(self,p1:Vec,p2:Vec,l:Line)->Self:
        # 通过两个在圆上的点和一条切线确定一个圆
        if l.W(p1)*l.W(p2)<0:
            raise GeoError(
                '通过两个点和切线确定圆时，两个点应在直线同侧' \
                f'但{p1}和{p2}在直线{l}异侧'
            )
        elif (p1 in l) and (p2 in l):
            raise GeoError(
                '通过两个点和切线确定圆时，两个点至少有一个在直线外' \
                f'但{p1}和{p2}都在直线{l}上'
            )

        l2=Line().by_2p(p1,p2)
        

        if l2.is_para(l):
            # 两点连线和l平行，单独讨论，解唯一
            return self.by_3p(
                p1,p2,(p1.mid_line(p2)&l)
            )
        else:
            p_cross=l2&l
            d=(
                sqrt(distance(p_cross,p1)*distance(p_cross,p2))
                *l.uVec.unit().rotate()
            )   # d是p1,p2连线与l交点p_crose 指向切点的向量，他有两个，此处为其中一个

            return Group().include(
                Circle().by_3p(
                    p1,p2,p_cross+d
                ),
                Circle().by_3p(
                    p1,p2,p_cross-d
                )
            )

    @should_define
    def __contains__(self, item:Vec):
        if isinstance(item,Vec):
            return abs(distance(self.c,item)-self.r)<distance_eps
        else:
            return NotImplemented

    @should_define
    def W(self,p):
        # 特征值，相当于到圆心距离的平方减半径的平方 d^2-r^2
        return distance(p,self.c)**2-self.r**2

    @should_define
    def __and__(self, other)->VecSet|Vec|None:
        if isinstance(other,Line):
            d=distance(self.c,other)
            if d>self.r:
                return None
            temp=self.c+sgn(-other.W(self.c))*other.uVec.unit()*d
            return VecSet(
                (
                    temp+other.uVec.rotate().unit()*sqrt(-self.W(temp)),
                    temp-other.uVec.rotate().unit()*sqrt(-self.W(temp))
                )
            )
        elif isinstance(other,Circle):
            if self.r+other.r<distance(self.c,other.c):
                return None
            elif abs(self.r-other.r)>distance(self.c,other.c):
                return None
            else:
                return self&Line().by_ABC(
                    -2*(self.c.x-other.c.x),
                    -2*(self.c.y-other.c.y),
                    self.c.r**2-other.c.r**2-
                    (self.r**2-other.r**2)
                )
        else:
            return NotImplemented

    @should_define
    def near_point(self,p:Vec)->Vec:
        # 圆上到p点最近的点
        if p==self.c:
            raise GeoError(
                '圆上到点%s最近的点不存在，因为点%s是圆心'%(p,p)
            )
        return self.c+(p-self.c).unit()*self.r

    @should_define
    def theta_to_Vec(self,theta):
        # 圆上某个角度对应的点
        return self.c+rVec(self.r,theta)

    @should_define
    def move(self,vec:Vec):
        temp=self.copy()
        temp.c=temp.c+vec
        return temp

    @should_define
    def rotate(self,theta,p:Vec):
        temp=self.copy()
        temp.c=temp.c.rotate(theta,p)
        return temp

    @should_define
    def symm_line(self,l:Line):
        return Circle().by_c_r(
            self.c.symm_line(l),self.r
        )

    
class Arc(LineGeo):
    # 圆弧
    default_style={
        "fill":"none",
        "stroke":"red"
    }

    def __repr__(self):
        if self.define:
            return (
                super().__repr__()+
                'c=%s start=%d° stop=%d°'%(
                    self.circle.c,
                    degrees(es(self.start)),
                    degrees(es(self.stop))
                )   
            )
        return super().__repr__()

    @should_define
    def copy(self):
        return (
            Arc().set_style(
                self.style
            ).by_circ_theta(
                self.circle,
                self.start,
                self.stop
            )
        )
        
    def by_circ_theta(self,circ:Circle, start,stop):
        # 通过圆和角度来确定一个圆弧
        # 规定总是由 起点到终点 逆时针绕行
        # 终点角度减起点角度的主值为绕行角度(圆心角)
        self.circle=circ.copy()
        self.start=start
        self.stop=stop
        self.start_Vec=self.circle.theta_to_Vec(self.start)
        self.stop_Vec=self.circle.theta_to_Vec(self.stop)
        self.theta=(self.stop-self.start)%(2*pi)    # 绕行角度
        
        self.define=True
        return self
    
    def by_2p_theta(self,p1:Vec,p2:Vec,theta, swing=True):
        # 通过弧的两个端点和圆心角确定一个圆弧，swing为True时，由p1逆时针向p2，否则顺时针
        if swing is False:
            return self.by_2p_theta(p2,p1,theta,True)
        circ=Circle().by_c_p(   
            Vec().by_2p_theta(
                p1,p2,theta
            ),
            p1
        )
        self.by_circ_theta(
            circ,
            (p1-circ.c).arc,
            (p2-circ.c).arc
        )
        return self

    def by_2p_circ(self,p1:Vec,p2:Vec,circ:Circle):
        # 通过圆心-弧端点连线延长线上的两点和圆来确定一段弧
        return self.by_circ_theta(
            circ,(p1-circ.c).arc,(p2-circ.c).arc
        )


    @should_define
    def move(self,vec:Vec):
        temp=self.copy()
        temp.circle=(temp.circle).move(vec)
        return temp
    
    @should_define
    def rotate(self,theta,p:Vec):
        return (
            self.copy().by_circ_theta(
                (self.circle).rotate(theta,p),
                self.start+theta,
                self.stop+theta
            )
        )

    @should_define
    def symm_line(self,l:Line):
        return Arc().by_circ_theta(
            self.circle.symm_line(l),
            2*es(l.uVec.arc+pi/2)-es(self.stop),
            2*es(l.uVec.arc+pi/2)-es(self.start)
        )

    @should_define
    def __contains__(self, item:Vec):
        if item in self.circle:
            return inside(
                self.start,self.stop,
                (item-self.circle.c).arc
            )
        else:
            return False

    @should_define
    def __and__(self, other):
        x=self.circle&other
        if x is None:
            return None
        elif isinstance(x,(Vec,VecSet)):
            return x.filter(
                lambda x:x in self
            )
        else:
            return NotImplemented

    @should_define
    def oppo_arc(self)->Arc:
        # 返回与当前圆弧互补的圆弧
        # 返回值与当前圆弧组成一个完整的圆
        
        return Arc().by_circ_theta(
            self.circle,
            self.stop,
            self.start
        )
# 更多圆锥曲线

class Eclipse(LineGeo):
    def by_ab_p_theta(self,a,b,center:Vec,theta=0):
        # 通过半长轴，半短轴，椭圆中心和长轴所在直线倾斜角来确定一条直线
        self.center=center
        self.a=a
        self.b=b
        self.c=sqrt(a**2-b**2)
        self.e=self.c/self.a
        self.define=True
        return self
    
    def by_circ_vec(self,circ:Circle,vec:Vec):
        # 由一个圆和代表伸缩量的向量通过伸缩变换来确定一个椭圆
        a,b=max(abs(vec)*circ.r,circ.r),min(abs(vec)*circ.r,circ.r)
        if sgn(abs(vec)-1)==1:
            theta=vec.arc
        else:
            theta=vec.arc+pi/2

        return self.by_ab_p_theta(
            a,b,circ.c,theta
        )

    def by_xryr(self,xr,yr,center,theta=0):
        # 由椭圆在x轴和y轴上的 半 轴长,中心和角度确定一个椭圆
        
        return self.by_ab_p_theta(
            sqrt(
                cos(2*theta)/(
                    cos(theta)**2/xr**2-sin(theta)**2/yr**2
                )
            ),
            sqrt(
                cos(2*theta)/(
                    cos(theta)**2/yr**2-sin(theta)**2/xr**2
                )
            ),
            center,
            theta
        )
        


class Group(LineGeo):
    default_style=dict()

    @init_deco(__qualname__)
    def __init__(self, name = None):
        self.group:list[LineGeo]=[]
        super().__init__(name)
        self.define=True

    def __repr__(self):
        return super().__repr__()+f'have {len(self.group)} LineGeo(s)'

    @should_define
    def copy(self):
        return (
            Group().set_style(
                self.style
            ).extend(
                self.group
            )
        )
    
    def include(self,*sth:LineGeo):
        return self.extend(sth)
    
    def extend(self,groups:Iterable[LineGeo]):
        self.group.extend(
            filter(lambda x:isinstance(x,LineGeo),groups)
        )
        return self

    def move(self,vec:Vec):
        temp=Group()
        for i in self.group:
            temp.group.append(i.move(vec))
        return temp
    
    def rotate(self,theta,p:Vec):
        temp=Group()
        for i in self.group:
            temp.group.append(i.rotate(theta,p))
        return temp

    def symm_line(self,l:Line):
        temp=Group()
        for i in self.group:
            temp.group.append(i.symm_line(l))
        return temp

    def filter(self,func:Callable[[Vec],bool])->Group:
        return Group().extend(
            filter(
                func,self.group
            )
        )

    def set_style(self, dict):
        for i in self.group:
            i.set_style(dict)
        return self

    def clear_style(self):
        for i in self.group:
            i.clear_style()
        return self

    

xyLine=Group('主坐标线').include(
    Line().by_2p(
        ORIG,Vec(100,0)
    ),
    Line().by_2p(
        ORIG,Vec(0,100)
    )
).set_style({'stroke':'green'})

xyLines=Group('次坐标线').include(
    *[
        Group().include(
            Line().by_ABC(
                -1,0,50*i
            ),
            Line().by_ABC(
                1,0,50*i
            ),
            Line().by_ABC(
                0,-1,50*i
            ),
            Line().by_ABC(
                0,1,50*i
            )
        ).set_style({'stroke':"#033F03"})
        for i in range(1,12)
    ]
)


deg=pi/180

tab=' '*4

def distance(a,b):
    if hasattr(a,'distance'):
        x=a.distance(b)
        if x is not NotImplemented:
            return x
    if hasattr(b,'distance'):
        x=b.distance(a)
        if x is not NotImplemented:
            return x
    raise GeoError(f'未定义{type(a)}和{type(b)}的距离')


