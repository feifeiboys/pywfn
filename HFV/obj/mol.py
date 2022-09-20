"""
基础的分子对象，其属性应该是标准的，已知的
一个分子对象应该有哪些属性？
结构相关
- 原子
- 键
- 法向量
- 重原子

分子轨道相关
轨道数量
轨道类型
是否分为α和β
占据轨道序数
非占据轨道序数
重叠矩阵

读取器
"""

from typing import *
from .atom import Atom
from .bond import Bond
import numpy as np
from .. import setting
class Mol:
    def __init__(self) -> None:
        self.atoms:Dict[int:Atom]={}
        self.bonds:Dict[str:Bond]={} # 所有键对象
        self.Eigenvalues:List[float]=[]
        self.isSplitOrbital:bool=None #轨道是否为劈裂的，值为0或1
        self.orbitals:List[str]=[] # 存储所有轨道时占据还是非占据
        self.orbitalNum:int
        self.orbitalType:int
        self.O_orbitals:List[int]
        self.V_orbitals:List[int]
        self.heavyAtoms:List[Atom]
        self.overlapMatrix:np.ndarray=None
        self.reader=None
        
    
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
                    if distance<=setting.BOND_LIMIT:
                        bond=Bond(atom1,atom2)
                        bond.length=distance
                        self.bonds[f'{idx1}-{idx2}']=bond

    def add_bond(self,idx1:int,idx2:int):
        """添加一个键"""
        if idx2<idx1:idx1,idx2=idx2,idx1
        self.bonds[f'{idx1}-{idx2}']=Bond(self.atoms[idx1], self.atoms[idx2])

    def get_bond(self,idx1:int,idx2:int)->Bond:
        """根据原子的索引获得键"""
        # 如果查询的键是存在的，则直接返回，否则生成一个新健
        if idx2<idx1:idx1,idx2=idx2,idx1
        bondID=f'{idx1}-{idx2}'
        if bondID not in self.bonds.keys():
            self.add_bond(idx1, idx2)    
        return self.bonds[f'{idx1}-{idx2}']

    def createAtomOrbitalRange(self):
        """令每个原子生成其在轨道矩阵中的范围"""
        total=0
        for atom in self.atoms.values():
            atom.orbitalMatrixRange=[total,total+len(atom.OC)]
            total+=len(atom.OC)

    def __repr__(self):
        return f'atom number: {len(self.atoms)}'
        


class Atoms:
    def __init__(self) -> None:
        self.atoms:Dict[int:Atom]={}
    
    def __getitem__(self,item:int):
        return self.atoms[item]

    def __setitem__(self,item,atom:Atom):
        self.atoms[item]=atom
    
    def __len__(self):
        return len(self.atoms)

    def __repr__(self):
        return '\n'.join([f'{atom}' for atom in self.atoms.values()])
    