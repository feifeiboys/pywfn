"""
此脚本用来计算mulliken自旋
"""
import numpy as np
from ..base import Mol,Atom
from typing import *
from ..utils import printer

class Calculator:
    def __init__(self,mol:"Mol") -> None:
        self.mol=mol
    
    def get_PM(self,obts:List[int]):
        """计算密度矩阵(其实可以读的,但是感觉读的没有计算的快,因为可以直接根据系数矩阵计算)"""
        A=(self.mol.CM[:,obts].T)[:,:,np.newaxis]
        B=(self.mol.CM[:,obts].T)[:,np.newaxis,:]
        PM=np.sum(A@B*self.mol.oE,axis=0) # 重叠矩阵
        return PM
    
    def get_Es(self,obts:List[int])->List[float]:
        PM=self.get_PM(obts)
        SM=self.mol.SM
        PS=PM*SM
        PS_=np.sum(PS,axis=0)
        Es=[]
        for atom in self.mol.atoms:
            a_1,a_2=atom.obtRange
            charge=PS_[a_1:a_2]
            Es.append(charge.sum())
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
        print(aEs-bEs)
        # print(aEs,bEs)

    def print(self,resStr:str):
        printer.info('mulliken 电子自旋分布:')
        printer.res(resStr)
        printer.bar()
        
    def resStr(self):
        resStr=''
        res=self.calculate()
        if res is None:return '非开窍层无法计算自旋!!'
        atoms=self.mol.atoms
        for a,v in zip(atoms,res):
            resStr+=f'{a.idx:<2}{a.symbol:>2}{v:>15.8f}\n'
        return resStr
            
