"""
计算mayer键级
mayer键级计算公式为: 
$\sum_{a\in A}\sum_{b\in B}PS$
"""
import numpy as np
import pandas as pd
from colorama import Fore

class Caculater:
    def __init__(self,mol:"Mol"):
        self.mol=mol

    def get_P(self,a1:"Atom",a2:"Atom",orbital:int):
        As = self.As[orbital]
        direction=a1.get_Normal(a2)
        OC1=a1.OC.to_numpy()[:,orbital]#/As**0.5
        OC2=a2.OC.to_numpy()[:,orbital]#/As**0.5
        ts1=OC1[np.newaxis,:] # 列向量
        ts2=OC2[:,np.newaxis] # 行向量
        return ts1*ts2

    def calculate(self,a1:"Atom",a2:"Atom"):
        """计算两原子之间的mayer键级"""
        self.mol.createAtomOrbitalRange() # 为每个原子分配其在轨道矩阵中的序数范围
        # 获取密度矩阵 C
        CM=self.mol.CM
        PM=self.mol.PM
        # 获取重叠矩阵
        SM=self.mol.SM
        if SM is None:
            print(Fore.RED+'缺少重叠矩阵！')
            return 'None'

        PS=PM@SM

        
        a1_1,a1_2=a1.orbitalMatrixRange
        a2_1,a2_2=a2.orbitalMatrixRange
        # print(a1_1,a1_2,a2_1,a2_2)
        order=np.sum(PS[a1_1:a1_2,a2_1:a2_2]*PS[a2_1:a2_2,a1_1:a1_2].T)
        # S=self.mol.overlapMatrix[a1_1:a1_2,a2_1:a2_2]
        return order

        















from ..base import Mol,Atom