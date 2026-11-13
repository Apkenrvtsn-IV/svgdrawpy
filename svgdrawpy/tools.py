from __future__ import annotations

from math import *

def sgn(x):
    if x==0:
        return 0
    elif x>0:
        return 1
    else:
        return -1

def es(x,T=2*pi):
    # 类似%
    return x-floor(x/T)*T

ass=1
def inside(start,stop,theta):
    start=es(start)
    stop=es(stop)
    theta=es(theta)
    if stop>=start:
        return start<=theta<=stop
    else:
        return theta<=stop or theta>=start

def process_comm(s:str):
    # 处理一段文本，使其可以作为注释写入svg文件中
    s=s.replace('--','- -')
    s=s.replace(']]>','')
    return s

