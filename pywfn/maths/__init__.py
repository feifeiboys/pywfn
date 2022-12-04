import numpy as np
from typing import *
from .gto import Gto

def gridPos(range):
    """生成网格数据点,range:生成数据的范围"""
    ...

def CM2PM(CM,orbital:List[int],oe:int):
    """
    根据系数矩阵构建密度矩阵
    CM:系数矩阵,如果是开壳层的话,列数是行数的两倍[n,n]/[n,2n]
    n:分子轨道占据电子数
    """
    PMs=CM2PMs(CM,orbital,oe)
    return np.sum(PMs,axis=0)

def CM2PMs(CM,orbital:List[int],oe:int):
    """
    构建三维密度矩阵，不要空轨道，形状为[占据轨道数,原子轨道数,原子轨道数]
    """
    A=(CM[:,orbital].T)[:,:,np.newaxis]
    B=(CM[:,orbital].T)[:,np.newaxis,:]
    return A@B*oe #用矩阵乘法的形式直接构建矩阵可比逐元素计算多了