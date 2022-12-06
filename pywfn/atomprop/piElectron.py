"""
该脚本计算指定原子的pi电子数
"""
from ..base import Mol,Atom
from typing import *
import numpy as np
from ..maths import CM2PM
from ..utils import printer

class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol

        
    def calculate(self,atoms:List[Atom]=None):
        """计算π电子数量,如果不指定则计算所有的π电子"""
        SM=self.mol.SM #重叠矩阵
        if SM is None:
            return 0
        # 重构系数矩阵
        CM_=np.zeros_like(self.mol.CM,dtype=np.float32)
        if atoms is None:
            atoms=[atom for atom in self.mol.atoms if atom.symbol!='H']
        
        self.mol.createAtomOrbitalRange()
        orbitals=self.mol.O_obts
        for atom in atoms:
            if atom.symbol=='H': #氢原子没有p轨道所以没有π电子
                continue
            normal=atom.get_Normal()
             # 占据轨道
            a_1,a_2=atom.obtMatrixRange
            pIndex=[i for i,l in enumerate(atom.layers) if 'P' in l]
            for i,orbital in enumerate(orbitals):
                Cop=atom.get_pProj(normal,orbital)
                Co=np.zeros(len(atom.layers))
                Co[pIndex]=np.concatenate(Cop)
                CM_[a_1:a_2,orbital]=Co

        # 计算密度矩阵
        PM_=CM2PM(CM_,orbitals,self.mol.oE)
        PS=PM_*SM
        PSS=PS.sum(axis=0)
        electrons=[]
        for atom in atoms:
            a_1,a_2=atom.obtMatrixRange
            electron=np.sum(PSS[a_1:a_2])
            printer.res(f'{atom.idx:<2}{atom.symbol:>2}{electron:>15.8f}')
            electrons.append(electron)
        return electrons

