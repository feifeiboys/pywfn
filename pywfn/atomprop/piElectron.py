"""
该脚本计算指定原子的pi电子数
"""
from ..base import Mol,Atom
from typing import *
import numpy as np
import pandas as pd

class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol

    def get_pIndex(self,layers:List[str]):
        return [i for i,l in enumerate(layers) if 'P' in l]
    
    def transts(self,atom:Atom,normal,orbital):
        """将系数转为多个向量"""
        nvecs=[]
        ts_=atom.get_pLayersProjection(normal,orbital)
        ts_=np.concatenate(ts_)
        ts=atom.OC.iloc[:,orbital].to_numpy()
        # print(ts_)
        return ts_
            
            

    
    def calculate(self,atoms:List[Atom]=None):
        """计算π电子数量,如果不指定则计算所有的π电子"""
        self.mol.create_bonds()
        SM=self.mol.SM #重叠矩阵
        # 重构系数矩阵
        CM_=np.zeros_like(self.mol.CM)
        if atoms is None:
            atoms=self.mol.atoms()
        else:
            atoms=[self.mol.atom(i) for i in atoms]
        
        self.mol.createAtomOrbitalRange()
        orbitals=self.mol.O_orbitals
        for atom in atoms:
            if atom.symbol=='H': #氢原子没有p轨道所以没有π电子
                continue
            normal=atom.get_Normal()
             # 占据轨道
            a_1,a_2=atom.orbitalMatrixRange
            AC=atom.OC
            AC_=np.zeros_like(AC)
            idxs=self.get_pIndex(atom.layers)
            for orbital in orbitals:
                 # 具有n*3个数据，将这些作为n个向量投影到法向量上
                ps_=self.transts(atom,normal,orbital)
                AC_[idxs,orbital]=ps_
            CM_[a_1:a_2,:]=AC_
        # 计算密度矩阵
        PM_=np.zeros_like(self.mol.PM)
        Oe=1 if self.mol.isSplitOrbital else 2
        n=np.array([Oe if 'O' in o else 0 for o in self.mol.orbitals])
        for j in range(CM_.shape[1]):
            ci=CM_[:,j].copy().reshape(-1,1)
            cj=CM_[:,j].copy().reshape(1,-1)
            PM_+=ci@cj*n[j]
        PS=PM_*SM
        PSS=PS.sum(axis=0)
        electrons=[]
        for atom in atoms:
            a_1,a_2=atom.orbitalMatrixRange
            electrons.append(np.sum(PSS[a_1:a_2]))
        # print(electrons,sum(electrons))
        pd.DataFrame(CM_).to_csv('CM_.csv')
        pd.DataFrame(PM_).to_csv('PM_.csv')
        return electrons

