"""
传入一堆位置点，计算在这些位置的各种函数数值
传入的数组大小为[n,3],一行分别是x,y,z
基组的种类是有限的吗？有没有通用的表达形式？为每一个基组都定义不同的计算类型
"""
import numpy as np
from numpy import sqrt,ndarray
from typing import *
from ..base.basis import Basi
π=np.pi
e=np.e

def s(c:float,a:float,R:ndarray):
    return c*(2*a/π)**(3/4)*2*sqrt(a)*e**(-1*a*R)

def p(c:float,a:float,w:ndarray,R:ndarray):
    """
    p轨道系数
    c:收缩系数
    a:高斯指数
    w:坐标分量,x、y或z(向量形式表示)
    R:x**2+y**2+z**2, [n]
    """
    v=c*(2*a/π)**(3/4)*2*sqrt(a)*w*e**(-1*a*R)
    return v

def lgto(pos:ndarray,cs:List[float],as_:List[float],obType:str):
    """
    layer,计算一个收缩的(一层)原子轨道波函数
    pos,[n,3] 需要计算的点的坐标
    cs:收缩系数
    as_:高斯指数
    """
    x,y,z=pos.T
    R=np.sum(pos**2,axis=1) # 每个点到中心点的距离[n]
    vs=np.zeros(pos.shape[0])
    for a,c in zip(as_,cs):
        if obType=='S': # 2S和3S
            # v=s(c,a,R)
            v=0
        elif obType=='PX':
            v=p(c,a,x,R)
        elif obType=='PY':
            v=p(c,a,y,R)
        elif obType=='PZ':
            v=p(c,a,z,R)
        else:
            raise
        vs+=v
    return vs

def agto(pos:ndarray,basi:Basi,OCi:ndarray,layers:List[str]):
    """
    atom,计算一个原子的轨道波函数(所有层的轨道波函数之和)
    pos:要计算的点相对于原子(原子作为坐标原点)的坐标[n,3]
    basi:基组信息
    OCs:原子轨道组合系数信息
    layers:原子的轨道数据
    """
    lbasis=basi.get()
    vs=np.zeros(pos.shape[0])
    # print(f'{OCi=}')
    for l,C in zip(layers,OCi):
        lNum=int(l[0]) #所在的层数
        lbasi=lbasis[lNum-1][1]
        as_=lbasi[:,0] # 不管有几列，第一列都是高斯指数
        if lbasi.shape[1]==2: #没有p轨道的
            ...
        elif lbasi.shape[1]==3: #如果有三列,对应的有两种情况,2S和2PXYZ
            css=lbasi[:,1] # s轨道
            cps=lbasi[:,2] # p轨道
            # vs+=C*lgto(pos,css,as_,'s') #不要s
            vs+=C*lgto(pos,cps,as_,l[1:])
            # print(f'{C=}')
    return vs


if __name__=='__main__':
    pos=np.random.rand(100,3)
    cs=[1.,2.,3.]
    res=lgto(pos,cs)
    print(res)