from ..base import Mol,Atom
from typing import *
import numpy as np
from ..data import Elements
elements=Elements()
from ..utils import printer
class Calculator:
    def __init__(self,mol:"Mol"):
        self.mol=mol
    
    def calculate(self,atoms:List[Atom])->List[float]:
        PM=self.mol.PM
        SM=self.mol.SM
        PS=PM*SM
        PS_=np.sum(PS,axis=0)
        if SM is None:
            return 0
        charges=[]
        if atoms is None:
            atoms=self.mol.atoms
        for atom in atoms:
            a_1,a_2=atom.obtRange
            charge=PS_[a_1:a_2]
            symbol=atom.symbol
            charges.append(elements[symbol].charge-charge.sum())
        return charges
            
    def print(self):
        res=self.calculate()
        atoms=self.mo.atoms
        for a,v in zip(atoms,res):
            printer.res(f'{a.idx:<2}{a.symbol:>2}{v:>15.8f}')
