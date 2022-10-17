"""
公用的工具函数
"""
import numpy as np
from typing import *
def CM2PM(CM,n:List[int]):
    """
    根据系数矩阵构建密度矩阵
    CM:系数矩阵,如果是开壳层的话,列数是行数的两倍[n,n]/[n,2n]
    n:分子轨道占据电子数
    """
    l,c=CM.shape # CM行数和列数
    PM=np.zeros(shape=(l,l)) #[n,n]
    for j in range(CM.shape[1]):
        ci=CM[:,j].reshape(-1,1) #[n,1]
        cj=CM[:,j].reshape(1,-1) #[1,n]
        e=n[j]
        PM+=ci@cj*e
    return PM