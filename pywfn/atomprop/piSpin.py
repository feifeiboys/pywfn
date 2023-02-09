"""
此脚本用来计算pi-Mulliken电子自旋
"""
import numpy as np
from ..base import Mol,Atom
from typing import *
from ..maths import CM2PM
from ..utils import printer

class Calculator:
    def __init__(self,mol:"Mol") -> None:
        self.mol=mol
    
    def get_PM(self,CM,obts:List[int]):
        """计算密度矩阵(其实可以读的,但是感觉读的没有计算的快,因为可以直接根据系数矩阵计算)"""
        A=(CM[:,obts].T)[:,:,np.newaxis]
        B=(CM[:,obts].T)[:,np.newaxis,:]
        PM=np.sum(A@B*self.mol.oE,axis=0) # 重叠矩阵
        return PM
    
    
    def get_Es(self,obts:List[int]):
        """计算π电子数量,如果不指定则计算所有的π电子"""
        # 重构系数矩阵
        CM_=np.zeros_like(self.mol.CM,dtype=np.float32)
        SM=self.mol.SM

        atoms=[atom for atom in self.mol.atoms if atom.symbol!='H']
        
        orbitals=self.mol.O_obts
        for atom in atoms:
            if atom.symbol=='H': #氢原子没有p轨道所以没有π电子
                continue
            normal=atom.get_Normal()
             # 占据轨道
            a_1,a_2=atom.obtRange
            pIndex=[i for i,l in enumerate(atom.layers) if 'P' in l]
            for i,orbital in enumerate(orbitals):
                Cop=atom.get_pProj(normal,orbital)
                Co=np.zeros(len(atom.layers))
                Co[pIndex]=np.concatenate(Cop)
                CM_[a_1:a_2,orbital]=Co

        # 计算密度矩阵
        PM_=self.get_PM(CM_,obts)
        PS=PM_*SM
        PSS=PS.sum(axis=0)
        Es=[]
        for atom in atoms:
            a_1,a_2=atom.obtRange
            electron=np.sum(PSS[a_1:a_2])
            # printer.res(f'{atom.idx:<2}{atom.symbol:>2}{electron:>15.8f}')
            Es.append(electron)
        return Es

    def calculate(self):
        """计算所有原子的自旋"""
        if not self.mol.isOpenShell:
            # print('非开窍层无法计算自旋')
            return
        # 首先要有alpha电子和beta电子对应的轨道系数
        obtNum=self.mol.CM.shape[0] # 系数矩阵行数，基函数数量
        a_obt=[i for i,e in enumerate(self.mol.obtElcts) if (e!=0 and i<obtNum)]
        b_obt=[i for i,e in enumerate(self.mol.obtElcts) if (e!=0 and i>=obtNum)]
        aEs=np.array(self.get_Es(a_obt))
        bEs=np.array(self.get_Es(b_obt))
        return aEs-bEs
        
    def print(self,resStr:str):
        printer.info('所有非H原子的pi电子自旋:')
        printer.res(resStr)
        printer.bar()
        
    
    def resStr(self):
        resStr=''
        res=self.calculate()
        if res is None:return '非开窍层无法计算自旋!!'
        atoms=[atom for atom in self.mol.atoms if atom.symbol!='H']
        for a,v in zip(atoms,res):
            resStr+=f'{a.idx:<2}{a.symbol:>2}{v:>15.8f}\n'
        return resStr
