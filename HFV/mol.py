from typing import *
from .atom import Atom
from .bond import Bond
import numpy as np
class Mol:
    def __init__(self) -> None:
        self.atoms={}
        self.bonds={}

    def atomPos(self,idx:int):
        """返回指定序号原子的坐标"""
        return self.atoms[idx].pos
    
    def add_atom(self,symbol:str,coord:List[float]):
        atom=Atom(symbol,coord)
        idx=len(self.atoms)+1
        self.atoms[idx]=atom

    def create_bonds(self):
        """生成键对象"""
        for idx1,atom1 in self.atoms.items():
            for idx2,atom2 in self.atoms.items():
                if idx1!=idx2:
                    distance=np.linalg.norm(atom1.coord,atom2.coord)
                    if distance<=1.7:
                        bond=Bond(atom1,atom2)
                        bond.length=distance
                        self.bonds[f'{idx1}-{idx2}']=bond
