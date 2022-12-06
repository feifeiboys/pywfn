"""
计算mayer键级
mayer键级计算公式为: 
$\sum_{a\in A}\sum_{b\in B}PS$
"""
import numpy as np
from colorama import Fore
from typing import *
from ..base import Atom,Mol

class Calculator:
    def __init__(self,mol:"Mol"):
        self.mol=mol

    def calculate(self,centerAtom:Atom,aroundAtom:Atom):
        """计算两原子之间的mayer键级"""
        self.mol.createAtomOrbitalRange() # 为每个原子分配其在轨道矩阵中的序数范围
        # 获取密度矩阵 P
        PM=self.mol.PM
        # 获取重叠矩阵
        SM=self.mol.SM
        PS=PM@SM

        a1_1,a1_2=centerAtom.obtMatrixRange
        a2_1,a2_2=aroundAtom.obtMatrixRange
        order=np.sum(PS[a1_1:a1_2,a2_1:a2_2]*PS[a2_1:a2_2,a1_1:a1_2].T)

        return order