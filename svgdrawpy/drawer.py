from __future__ import annotations

from .geo import *
from .tools import process_comm
import time



class Comm:
    def __init__(self,string):
        self.string=string
    def __repr__(self):
        return f'# {self.string}'

def write_point(x:Vec,sep=' '):
    # 格式化点的坐标
    return f"{x.x}{sep}{-x.y}"

                
def write_comm(string:str,tab_size=0):
    # 格式化注释
    return f'{tab_size*4*' '}<!--{process_comm(string)}-->\n'



def write_a_tag(tag,args,tab_size=0):
    # 格式化单标签
    paraments=(
        " ".join(
            [f"{key}=\"{value}\"" for (key,value) in args.items()]
        )
    )
    return f'{tab_size*4*' '}<{tag} {paraments} />\n'


def write_ab_tag(tag,args,tab_size=0):
    # 格式化双标签
    paraments=(
        " ".join(
            [f"{key}=\"{value}\"" for (key,value) in args.items()]
        )
    )
    return [
        f'{tab_size*4*' '}<{tag} {paraments}>\n',
        None,
        f'{tab_size*4*' '}</{tag}>\n'
    ]


def write_geo(obj:LineGeo|Comm|None|Any,tab_size=1)->list[str]:
    # 格式化图形对象
    # 编译一个图形对象
    '''返回一个列表 COMMAND，每一项代表一行
    不能编译时返回空列表
    x标识单标签(a)还是双标签(ab)
    编译双标签时，将需要编译在标签之内的内容赋给include
    include:list[LineGeo]
    '''
    COMMAND=[]

    args={}
    x=None

    if type(obj)==Lines:
        x='a'
        tag=("polygon" if obj.is_close else "polyline")
        args["points"]=(
            " ".join(
                [write_point(p,',') for p in obj.points]
            )
        )
        
    elif type(obj)==Line:
        x='a'
        tag="line"
        p_2=obj&screen_circ
        if type(p_2)==VecSet and len(p_2)==2:
            p_2:tuple[Vec]=tuple(p_2)
            args["x1"],args["y1"]=p_2[0].x, -p_2[0].y
            args["x2"],args["y2"]=p_2[1].x, -p_2[1].y
        else:
            # 直线不在画布内，不再编译
            COMMAND.append(
                write_comm(f'直线{obj.name}不在画布内')
            )
            return COMMAND
        
    elif type(obj)==Circle:
        x='a'
        tag="circle"
        args["cx"]=obj.c.x
        args["cy"]=-obj.c.y
        args["r"]=obj.r
        

    elif type(obj)==Arc:
        tag="path"
        args['d']=(
            f'M{write_point(obj.start_Vec)} '\
            f"A{obj.circle.r} {obj.circle.r} "\
            f'0 {0 if obj.theta<pi else 1} 0 '\
            f'{write_point(obj.stop_Vec)}'
        )
        x='a'

    elif type(obj)==Group:
        tag="g"
        include=obj.group
        x='ab'

    elif type(obj)==Comm:
        COMMAND.append(
            write_comm(obj.string,tab_size)
        )
        return COMMAND

    elif type(obj)==Vec:
        x='a'
        tag="circle"
        args["cx"]=obj.x
        args["cy"]=-obj.y

    elif type(obj)==VecSet:
        tag="g"
        include=obj
        x='ab'

    elif isinstance(obj,LineGeo):
        COMMAND.append(write_comm(obj.__repr__(),tab_size))
        COMMAND.append(write_comm(f'暂时无法编译的图形类: {type(obj).__name__}',tab_size))
        return COMMAND
    
    elif obj is None:
        COMMAND.append(write_comm('此处为被忽略的None',tab_size))
        return COMMAND

    else:
        COMMAND.append(
            write_comm(
                f'无法编译的类：{type(obj).__name__}，它不是LineGeo的子类', tab_size
            )
        )
        return COMMAND
    
    
    if obj.style is None:
        args|=obj.default_style
    else:
        args|=obj.style
    COMMAND.append(write_comm(obj.__repr__(),tab_size))

    if x=='a':
        COMMAND.append(
            write_a_tag(tag,args,tab_size)
        )
    elif x=='ab':
        temp=write_ab_tag(tag,args,tab_size)
        COMMAND.append(temp[0])
        COMMAND.append('\n')
        for i in include:
            COMMAND.extend(write_geo(i,tab_size+1))
        COMMAND.append(temp[2])

    COMMAND.append('\n')
    return COMMAND


def draw(elem:Iterable[LineGeo|Comm],filepath,viewbox:str):
    global screen_r,screen_circ
    # viewbox 格式：
    # <最小x> <最小y> <x跨度> <y跨度>
    with open(filepath,'w',encoding='utf-8') as file:

        file.write(
            '<svg xmlns="http://www.w3.org/2000/svg" '\
            f'{f"viewBox=\"{viewbox}\"" if viewbox else ""}>\n\n'
        )


        file.write('<!-- 由 svgdrawpy 编译 -->\n')
        t=time.localtime()
        file.write(f'<!-- {t.tm_year} 年 {t.tm_mon} 月 {t.tm_mday} 日 -->\n\n')

        viewbox=[int(i) for i in tuple(viewbox.split(' '))]
        screen_r=sqrt(viewbox[2]**2+viewbox[3]**2)/2
        screen_circ=Circle().by_c_r(
            Vec(
                viewbox[0]+viewbox[2]/2,viewbox[1]+viewbox[3]/2
            ),screen_r
        )
        
        for i in elem:
            for j in write_geo(i):
                file.write(j)
        file.write("</svg>\n")
    print('绘制完成')


