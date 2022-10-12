from ..base import Mol,Atom
from typing import *
import numpy as np

class Calculator:
    def __init__(self,mol:"Mol"):
        self.mol=mol
    
    def calculate(self,atoms:List[Atom]):
        PM=self.mol.PM
        SM=self.mol.SM
        PS=PM*SM
        PS_=np.sum(PS,axis=0)
        if SM is None:
            print('没有密度矩阵')
            return
        for atom in atoms:
            a_1,a_2=atom.orbitalMatrixRange
            
            
