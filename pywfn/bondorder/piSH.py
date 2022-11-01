"""
轨道挑选法+HMO键级公式
"""
from ..base import Mol,Atom
from .utils import judgeOrbital
import numpy as np

class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol

    def calculate(self,centerAtom:Atom,aroundAtom:Atom):
        self.mol.create_bonds()
        orbitals=self.mol.O_obts
        As=self.mol.As[orbitals]
        piUnits=[judgeOrbital(centerAtom,aroundAtom,o,centerAtom.get_Normal()) for o in orbitals]
        centerRes=np.sum(centerAtom.OC[:,orbitals]**2,axis=0)/As
        aroundRes=np.sum(aroundAtom.OC[:,orbitals]**2,axis=0)/As
        orders=centerRes*aroundRes*piUnits
        return orders
