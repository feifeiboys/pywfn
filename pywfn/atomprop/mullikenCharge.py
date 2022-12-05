from ..base import Mol,Atom
from typing import *
import numpy as np
from ..data import Elements
elements=Elements()
from ..utils import printer
class Calculator:
    def __init__(self,mol:"Mol"):
        self.mol=mol
    
    def calculate(self,atoms:List[Atom]):
        self.mol.createAtomOrbitalRange()
        PM=self.mol.PM
        SM=self.mol.SM
        PS=PM*SM
        PS_=np.sum(PS,axis=0)
        if SM is None:
            return 0
        charges=[]
        for atom in atoms:
            a_1,a_2=atom.obtMatrixRange
            charge=PS_[a_1:a_2]
            symbol=atom.symbol
            charges.append(elements[symbol].charge-charge.sum())
        return charges
            
            
