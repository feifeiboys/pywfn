"""
计算mayer键级
mayer键级计算公式为: 
$\sum_{a\in A}\sum_{b\in B}PS$
"""
import numpy as np
import pandas as pd
from colorama import Fore
from typing import *
from ..base import Atom,Mol

class Calculator:
    def __init__(self,mol:"Mol"):
        self.mol=mol

    def calculate(self,atoms:List[Atom]=None):
        """计算两原子之间的mayer键级"""
        self.mol.create_bonds()
        self.mol.createAtomOrbitalRange() # 为每个原子分配其在轨道矩阵中的序数范围
        # 获取密度矩阵 P
        PM=self.mol.PM
        # 获取重叠矩阵
        SM=self.mol.SM
        if SM is None:
            print(Fore.RED+'缺少重叠矩阵！')
            return 'None'
        PS=PM@SM
        orders=[]
        if atoms is None:atoms=self.mol.atoms()
        for i in range(len(atoms)-1): # 输入的每两个原子之间计算键级
            for j in range(i+1,len(atoms)):
                a1_1,a1_2=atoms[i].orbitalMatrixRange
                a2_1,a2_2=atoms[j].orbitalMatrixRange
                order=np.sum(PS[a1_1:a1_2,a2_1:a2_2]*PS[a2_1:a2_2,a1_1:a1_2].T)
                orders.append([i,j,order])
        return orders