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
from ..maths import vector_angle
from .atom import Atom,Atoms
from .bond import Bond
# from .basis import Basis
from .. import data
import numpy as np
from .. import setting
from functools import cached_property, lru_cache
from .. import utils
printer=utils.Printer()
from ..maths import gto

class Mol:
    def __init__(self) -> None:
        self._atoms:Atoms=Atoms()
        self.Eigenvalues:List[float]=[]
        self.isOpenShell:bool=None #轨道是否为开壳层，值为0或1
        self.obtElcts:List[int]=None # 存储每个分子轨道占据的电子数量(包含占据信息)
        self._heavyAtoms:List[Atom]=None
        self._CM:np.ndarray=None # 系数矩阵
        self._SM:np.ndarray=None # 重叠矩阵
        self.reader=None
        self.basis:"data.Basis"=None
        self.gto:"gto.Gto"=None
    
    @cached_property
    def obtStr(self)->List[str]:
        """返回轨道符号"""
        strs=[]
        for i,e in enumerate(self.obtElcts):
            symbol='V' if e==0 else 'O'
            if self.isOpenShell and i>=self._CM.shape[1]:
                i-=self._CM.shape[1]
            strs.append(f'{i+1:<3}{symbol}')
        return strs
    
    @cached_property
    def obtRanges(self): #获取每一个原子在系数矩阵中的范围
        atomics=[atom.atomic for atom in self.atoms]
        return [self.basis.num(atomic) for atomic in atomics]
    
    def obtRange(self,idx:int):
        """获取指定原子在系数矩阵中的范围"""
        start=sum(self.obtRanges[:idx-1]) #索引不包括
        length=self.obtRanges[idx-1]
        return [start,start+length]
    
    def add_atom(self,symbol:str,coord:List[float]):
        """添加一个原子"""
        idx=len(self._atoms)+1
        atom=Atom(symbol,coord,idx,self)
        self._atoms.append(atom)
    
    def atom(self,idx:int)->Atom:
        """根据原子编号获取一个原子,从1开始"""
        if not isinstance(idx,int):raise
        return self._atoms[idx-1]
    
    @property
    def atoms(self)->List[Atom]:
        """获取所有原子"""
        return self._atoms
    
    @cached_property
    def coords(self)->np.ndarray:
        """返回原子坐标矩阵[n,3]"""
        return np.array([atom.coord for atom in self.atoms])

    @cached_property
    def orbital_symbols(self)->List[str]:
        n=len(self.obtStr)
        if self.isOpenShell:
            return [f'α{e+1}' if e<n/2 else f'β{int(e-n/2+1)}' for e in range(n)]
        else:
            return [f'{e+1}' for e in range(n)]

    @cached_property
    def O_obts(self)->List[int]:
        return [i for i,e in enumerate(self.obtElcts) if e!=0]
    
    @cached_property
    def V_obts(self)->List[int]:
        return [i for i,e in enumerate(self.obtElcts) if e==0]
    
    @cached_property
    def heavyAtoms(self):
        return [atom for atom in self.atoms if atom.symbol!='H']

    @cached_property
    def CM(self)->np.ndarray:
        """分子轨道系数矩阵"""
        return np.concatenate([atom.OC for atom in self.atoms],axis=0)
    
    @property
    def SM(self):
        """重叠矩阵"""
        if self._SM is None:
            printer.wrong('没有重叠矩阵,将使用单位矩阵作为重叠矩阵!!!')
            self._SM=np.eye(self.CM.shape[0])
        return self._SM

    @cached_property
    def PM(self):
        """计算密度矩阵(其实可以读的,但是感觉读的没有计算的快,因为可以直接根据系数矩阵计算)"""
        A=(self.CM[:,self.O_obts].T)[:,:,np.newaxis]
        B=(self.CM[:,self.O_obts].T)[:,np.newaxis,:]
        PM=np.sum(A@B*self.oE,axis=0) # 重叠矩阵
        return PM
    
    @property
    def oE(self):
        """轨道电子数"""
        return 1 if self.isOpenShell else 2

    @cached_property
    def As(self):
        """所有原子所有轨道的平方和再开根号"""
        CM=self.CM.copy() #分子轨道矩阵
        return np.sqrt(np.sum(CM**2,axis=0)) #平方和再开根号

    @cached_property
    def bonds(self)->List[Bond]:
        atomNum=len(self.atoms)
        bonds=[]
        idxs=[(i+1,j+1) for i in range(atomNum) for j in range(atomNum) if i<j]
        for idx1,idx2 in idxs:
            r=np.linalg.norm(self.atom(idx2).coord-self.atom(idx1).coord)
            if r<1.8:
                bonds.append(self.bond(idx1,idx2))
        return bonds
    
    @lru_cache
    def bond(self,idx1:int,idx2:int)->Bond:
        """第一次调用是生成键,第二次调用时直接返回,秒啊"""
        if idx2<idx1:idx1,idx2=idx2,idx1
        return Bond(self.atom(idx1), self.atom(idx2))
    
    def get_dihedralAngle(self,idx1:int,idx2:int,idx3:int,idx4:int):
        """计算二面角"""
        a,b,c,d=self.atom(idx1),self.atom(idx2),self.atom(idx3),self.atom(idx4)
        vba=a.coord-b.coord
        vbc=c.coord-b.coord
        vcd=d.coord-c.coord
        vcb=b.coord-c.coord
        vi=np.cross(vba,vbc)
        vj=np.cross(vcb,vcd)
        angle=vector_angle(vi,vj)
        return angle
    def __repr__(self):
        return f'atom number: {len(self.atoms)}'
    