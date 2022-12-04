"""
轨道挑选法+mayer键级公式
mayer键级需要重叠矩阵,可一次性计算所有键级(此时原子的法向量由三个原子决定,而不是垂直于键轴)
"""
from ..base import Mol,Atom
from ..utils import vector_angle
from .utils import CM2PM,judgeOrbital
import numpy as np
import pandas as pd


class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol


    def calculate(self,centerAtom:Atom,aroundAtom:Atom):
        """指定两个原子,计算π键键级"""
        if self.mol.CM is None:
            print('没有重叠矩阵,无法计算')
            return 0
        self.mol.createAtomOrbitalRange()
        centerNormal=centerAtom.get_Normal()
        orbitals=self.mol.O_obts
        CM_=np.zeros_like(self.mol.CM) # 拷贝一份，然后将不是π轨道的那些变成0
        atoms=[centerAtom,aroundAtom]
        for atom in atoms: # 修改每个原子对应的系数矩阵
            if atom.symbol=='H':continue
            a_1,a_2=atom.obtMatrixRange
            for orbital in orbitals:
                if judgeOrbital(centerAtom,aroundAtom,orbital,centerNormal): # 如果是π轨道
                    # print(atom.idx,orbital)
                    CM_[a_1:a_2,orbital]=self.mol.CM[a_1:a_2,orbital]
        # pd.DataFrame(CM_).to_csv('CM_.csv')
        oe=1 if self.mol.isOpenShell else 2
        n=[oe if 'O' in o else 0 for o in self.mol.orbitals]
        PM_=CM2PM(CM_,orbitals,oe)
        # pd.DataFrame(PM_).to_csv('PM_.csv')
        SM=self.mol.SM
        PS=PM_@SM

        a1,a2=centerAtom.obtMatrixRange
        b1,b2=aroundAtom.obtMatrixRange
        order=np.sum(PS[a1:a2,b1:b2]**2)
        return order

        
                    