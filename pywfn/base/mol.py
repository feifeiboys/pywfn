"""
基础的分子对象，其属性应该是标准的，已知的
一个分子对象应该有哪些属性？基本属性(必须属性),计算属性(需要计算才能的到的属性)
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
from .atom import Atom,Atoms
from .bond import Bond
import numpy as np
from .. import setting
class Mol:
    def __init__(self) -> None:
        self._atoms=Atoms()
        self.bonds:Dict[str:Bond]={} # 所有键对象
        self.Eigenvalues:List[float]=[]
        self.isSplitOrbital:bool=None #轨道是否为劈裂的，值为0或1
        self.orbitals:List[str]=[] # 存储所有轨道时占据还是非占据
        self._orbitalNum:int=None
        # self.orbitalType:int=None
        self._O_orbitals:List[int]=None
        self._V_orbitals:List[int]=None
        self._heavyAtoms:List[Atom]=None
        self._CM:np.ndarray=None # 系数矩阵
        self._SM:np.ndarray=None # 重叠矩阵
        self._PM:np.ndarray=None # 密度矩阵
        self._As=None
        self.reader=None
        
    
    def add_atom(self,symbol:str,coord:List[float]):
        """添加一个原子"""
        idx=len(self._atoms)+1
        atom=Atom(symbol,coord,idx,self)
        # print(type(self._atoms),self._atoms,dir(self._atoms))
        self._atoms.add(atom)
    
    def atom(self,idx:int)->Atom:
        """根据原子编号获取一个原子,从1开始"""
        if not isinstance(idx,int):raise
        return self._atoms[idx-1]
    
    def atoms(self)->List[Atom]:
        """获取所有原子"""
        return self._atoms
    
    

    @property
    def orbitalNum(self):
        if self._orbitalNum is None:
            self._orbitalNum=len(self.orbitals)
        return self._orbitalNum

    @property
    def O_orbitals(self)->List[int]:
        if self._O_orbitals is None:
            self._O_orbitals=[orbital for orbital in range(self.orbitalNum) if self.orbitals[orbital][-1]=='O']
        return self._O_orbitals
    
    @property
    def V_orbitals(self)->List[int]:
        if self._V_orbitals is None:
            self._V_orbitals=[orbital for orbital in range(self.orbitalNum) if self.orbitals[orbital][-1]=='V']
        return self._V_orbitals
    
    @property
    def heavyAtoms(self):
        if self._heavyAtoms is None:
            self._heavyAtoms=[atom for atom in self.atoms() if atom.symbol!='H']
        return self._heavyAtoms

    @property
    def CM(self)->np.ndarray:
        """分子轨道系数矩阵"""
        if self._CM is None:
            self._CM=np.concatenate([atom.OC.to_numpy() for atom in self.atoms()],axis=0)
        return self._CM
    
    @property
    def SM(self):
        """重叠矩阵"""
        if self._SM is None:
            if self.reader is not None:
                self.reader.read_SM()
        return self._SM

    @property
    def PM(self):
        """密度矩阵"""
        if self._PM is None:
            # 自己计算密度矩阵吧
            h,w=self.CM.shape # h行,w列
            PM=np.zeros(shape=(h,h)) # 重叠矩阵
            Oe=1 if self.isSplitOrbital else 2
            n=np.array([Oe if 'O' in o else 0 for o in self.orbitals])
            for i in range(w):
                C1=self.CM[:,i][:,np.newaxis]
                C2=self.CM[:,i][np.newaxis,:]
                PM+=C1*C2*n[i]
            self._PM=PM
        return self._PM

    @property
    def As(self):
        """# 所有原子所有轨道的平方和"""
        if self._As is None:
            self._As=np.array([np.sum(atom.spLayersData**2,axis=0) for atom in self.heavyAtoms]).sum(axis=0)
        return self._As

    def trans(self):
        self.As2=np.array([atom.squareSum for atom in self.atoms()]).sum(axis=0)
        self.orbitalElectron=1 if self.isSplitOrbital else 2
        self.squareSums=np.array([atom.squareSum for atom in self.atoms()])
        self.create_bonds()

    def create_bonds(self):
        """生成键对象"""
        for idx1,atom1 in enumerate(self.atoms()):
            for idx2,atom2 in enumerate(self.atoms()):
                if idx1<idx2:
                    distance=np.linalg.norm(atom1.coord-atom2.coord)
                    if distance<=setting.BOND_LIMIT:
                        bond=Bond(atom1,atom2)
                        bond.length=distance
                        self.bonds[f'{idx1+1}-{idx2+1}']=bond

    def add_bond(self,idx1:int,idx2:int):
        """添加一个键"""
        if idx2<idx1:idx1,idx2=idx2,idx1
        key=f'{idx1}-{idx2}'
        if key not in self.bonds.keys():
            self.bonds[key]=Bond(self.atom(idx1), self.atom(idx2))

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
        for atom in self.atoms():
            atom.orbitalMatrixRange=[total,total+len(atom.OC)]
            total+=len(atom.OC)

    def __repr__(self):
        return f'atom number: {len(self.atoms)}'
    