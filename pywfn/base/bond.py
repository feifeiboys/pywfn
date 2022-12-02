from .atom import Atom
import numpy as np
# 如何获取一个键？
# Mol.getBond(a1,a2)
# Mol应该有bonds属性，是一个字典，索引是'a1-a2'和'a2-a1'都指向该键
from functools import cached_property
class Bond:
    def __init__(self,a1:Atom,a2:Atom) -> None:
        self.a1=a1
        self.a2=a2
        self._length:float=None
        self.idx=f'{a1.idx}-{a2.idx}'
    
    @cached_property
    def length(self):
        """获取键长"""
        return np.linalg.norm(self.a2.coord-self.a1.coord)

    @cached_property
    def vector(self):
        """获取键向"""
        return self.a2.coord-self.a1.coord
    
    def __repr__(self) -> str:
        return f'length={self.length}'