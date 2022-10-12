"""
传入一堆位置点，计算在这些位置的各种函数数值
传入的数组大小为[n,3],一行分别是x,y,z
基组的种类是有限的吗？有没有通用的表达形式？为每一个基组都定义不同的计算类型
"""
import numpy as np
from numpy import sqrt,ndarray
π=np.pi
e=np.e
def s():
    ...

def px(c:float,a:float,x:float,R:ndarray)->ndarray:
    """
    c:收缩系数
    a:高斯指数
    x:坐标分量
    R:x**2+y**2+z**2
    """
    return c*(2*a/π)**(3/4)*2*sqrt(a)*x*e**(-1*a*R)

def py():
    ...

def pz():
    ...

def gto(gridPos,centPos,cs,as_):
    """
    gridPos,[n,3]
    centPos,[1,3]
    """
    x,y,z=(gridPos-centPos).T
    R=np.sum((gridPos-centPos)**2,axis=1,keepdims=True) # 每个点到中心点的距离[n,1]

