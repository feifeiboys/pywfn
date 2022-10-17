"""
轨道挑选法+mayer键级公式
mayer键级需要重叠矩阵,可一次性计算所有键级(此时原子的法向量由三个原子决定,而不是垂直于键轴)
"""
from sympy import im
from ..base import Mol,Atom
from ..utils import vector_angle
from .utils import CM2PM
import numpy as np
import pandas as pd


class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol

    def judgeOrbital(self,orbital:int)->int:
        """判断一个轨道是否为π轨道,几何方法"""
        if self.aroundAtom.symbol=='H' or self.centerAtom.symbol=='H':
            return 0
        # 1. 根据s轨道和p轨道的贡献
        sContCenter=self.centerAtom.get_sCont(orbital)
        sContAround=self.aroundAtom.get_sCont(orbital)
        if sContCenter>0.1 or sContAround>0.1:
            return 0
        # 2. p轨道的方向要处在垂直分子平面方向
        cenDir=self.centerAtom.get_orbitalDirection(orbital)
        aroDir=self.aroundAtom.get_orbitalDirection(orbital)
        if vector_angle(cenDir,self.normal)>0.2:
            return 0
        if vector_angle(aroDir,self.normal)>0.2:
            return 0
        # 以上两个条件都满足的可以认为是π轨道
        return 1

    def calculate(self,centerAtom:Atom,aroundAtom:Atom):
        """指定两个原子,计算π键键级"""
        self.mol.create_bonds()
        self.mol.createAtomOrbitalRange()
        self.centerAtom=centerAtom
        self.aroundAtom=aroundAtom
        self.normal=centerAtom.get_Normal()
        orbitals=self.mol.O_orbitals
        CM_=np.zeros_like(self.mol.CM) # 拷贝一份，然后将不是π轨道的那些变成0
        atoms=[centerAtom,aroundAtom]
        for atom in atoms: # 修改每个原子对应的系数矩阵
            if atom.symbol=='H':continue
            a_1,a_2=atom.orbitalMatrixRange
            for orbital in orbitals:
                if self.judgeOrbital(orbital): # 如果是π轨道
                    print(orbital)
                    CM_[a_1:a_2,orbital]=self.mol.CM[a_1:a_2,orbital]
        pd.DataFrame(CM_).to_csv('CM_.csv')
        oe=1 if self.mol.isSplitOrbital else 2
        n=[oe if 'O' in o else 0 for o in self.mol.orbitals]
        PM_=CM2PM(CM_,n)
        SM=self.mol.SM
        PS=PM_@SM
        orders=[]
        for i in range(len(atoms)-1): # 输入的每两个原子之间计算键级
            for j in range(i+1,len(atoms)):
                a1_1,a1_2=atoms[i].orbitalMatrixRange
                a2_1,a2_2=atoms[j].orbitalMatrixRange
                order=np.sum(PS[a1_1:a1_2,a2_1:a2_2]*PS[a2_1:a2_2,a1_1:a1_2].T)
                orders.append([atoms[i].idx,atoms[j].idx,order])
        return orders

        
                    