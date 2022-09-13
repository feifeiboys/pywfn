from typing import *
from .atom import Atom
from .bond import Bond
import numpy as np
class Mol:
    def __init__(self) -> None:
        self.atoms:Dict[int:Atom]={} # 所有原子对象
        self.bonds:Dict[str:Bond]={} # 所有键对象
        self.Eigenvalues:List[float]=[]
        self.isSplitOrbital:bool=None #轨道是否为劈裂的，值为0或1
        self.orbitals:List[str]=[] # 存储所有轨道时占据还是非占据
        self.orbitalNum:int
        self.orbitalType:int
        self.O_orbitals:List[int]
        self.V_orbitals:List[int]
        self.heavyAtoms:List[Atom]
        
    
    def add_atom(self,symbol:str,coord:List[float]):
        idx=len(self.atoms)+1
        atom=Atom(symbol,coord,idx,self)
        self.atoms[idx]=atom

    def trans(self):
        self.orbitalNum=len(self.orbitals)
        self.O_orbitals=[orbital for orbital in range(self.orbitalNum) if self.orbitals[orbital][-1]=='O']
        self.V_orbitals=[orbital for orbital in range(self.orbitalNum) if self.orbitals[orbital][-1]=='V']

        self.heavyAtoms=[atom for atom in self.atoms.values() if atom.symbol!='H']
        self.As=np.array([np.sum(atom.spLayersData**2,axis=0) for atom in self.heavyAtoms]).sum(axis=0) # 所有原子所有轨道的平方和
        self.As2=np.array([atom.squareSum for atom in self.atoms.values()]).sum(axis=0)
        self.orbitalElectron=1 if self.isSplitOrbital else 2
        self.squareSums=np.array([atom.squareSum for atom in self.atoms.values()])
        self.create_bonds()

    def create_bonds(self):
        """生成键对象"""
        for idx1,atom1 in self.atoms.items():
            for idx2,atom2 in self.atoms.items():
                if idx1<idx2:
                    distance=np.linalg.norm(atom1.coord-atom2.coord)
                    if distance<=1.7:
                        bond=Bond(atom1,atom2)
                        bond.length=distance
                        self.bonds[f'{idx1}-{idx2}']=bond

    def get_bond(self,idx1:int,idx2:int):
        """根据原子的索引获得键"""
        return self.bonds[f'{idx1}-{idx2}']

    # def __repr__(self) -> str:
    #     return f''

class Atoms:
    def __init__(self) -> None:
        self.atoms:List[Atom]=[]
    
    def __getitem__(self,item:int):
        return self.atoms[item-1]
    
    def add_atom(self,atom:Atom):
        self.atoms.append(atom)