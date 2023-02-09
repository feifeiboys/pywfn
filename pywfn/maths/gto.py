"""
传入一堆位置点，计算在这些位置的各种函数数值
传入的数组大小为[n,3],一行分别是x,y,z
基组的种类是有限的吗？有没有通用的表达形式？为每一个基组都定义不同的计算类型
"""
import numpy as np
from numpy import sqrt,ndarray
from typing import *

π=np.pi
e=np.e

def gto(c:float,a:float,R:ndarray,pos:ndarray,lmn:Tuple[int]):
    """
    计算一系列gto函数的值
    c:收缩系数
    a:高斯指数
    pos:坐标
    R:坐标到原点距离平方
    lmn:角动量决定的x,y,z指数
    """
    l,m,n=lmn
    x,y,z=pos.T
    v=c*(2*a/π)**(3/4)*2*sqrt(a)* x**l * y**m * z**n *e**(-1*a*R)
    return v

def lgto(pos:ndarray,cs:List[float],as_:List[float],lmn):
    """
    layer gto,计算一个收缩的(一层)原子轨道波函数，1S,2PX,2PY等，由多个简单gto加和(收缩)得到
    pos,[n,3] 需要计算的点的坐标
    cs:收缩系数
    as_:高斯指数
    """
    R=np.sum(pos**2,axis=1) # 每个点到中心点的距离[n]
    vs=np.zeros(len(pos))
    if len(cs)!=len(as_):raise
    for a,c in zip(as_,cs):
        v=gto(c,a,R,pos,lmn)
        vs+=v
    return vs

from .. import data
class Gto:
    def __init__(self,basis:"data.Basis"):
        self.basis=basis
    def agto(self,pos:ndarray,OCi:ndarray,atomic:int,angs=[1]):
        """
        atom gto,计算一个原子的轨道波函数(所有层的轨道波函数之和)
        pos:要计算的点相对于原子(原子作为坐标原点)的坐标[n,3]
        OCs:原子轨道组合系数信息
        angs:要显示轨道的角动量,默认只计算p轨道

        1. 对每一个价层循环
        2. 对每个角动量循环
        3. 对角动量展开的lmn循环
        """
        base=self.basis.get(atomic)
        vs=np.zeros(len(pos)) # 波函数值，初始为0
        idx=0
        for i,shell in enumerate(base): # 首先对shell循环
            exps=shell['exp']
            for j,ang in enumerate(shell['ang']): # 然后对角动量循环
                show = True if ang in angs else False #控制需要计算的角动量
                coes=shell['coe'][j] #收缩系数是二维数组
                for k,lmn in enumerate(self.basis.lmn(ang)):
                    Ci=OCi[idx]
                    if show:
                        vs+=Ci*lgto(pos=pos,cs=coes,as_=exps,lmn=lmn)
                    idx+=1
        if idx!=len(OCi):raise #所有的系数必须都走完
        return vs

if __name__=='__main__':
    pos=np.random.rand(100,3)
    cs=[1.,2.,3.]
    res=lgto(pos,cs)
    print(res)