"""
一个原子的基组应该有一下层级

不同价层
    指数(一维数组)
    系数(二维数组)
不同角动量对应不同的mnl
所有可能的m+n+l=角动量决定了基函数的数量

"""
# from ..utils import printer
from .. import utils
printer=utils.Printer()
import json
from functools import lru_cache
from itertools import product
from typing import *
from pathlib import Path
class Basis:
    """
    所有提前准备的基组数据
    """
    def __init__(self,name:str) -> None:
        """根据基组名实例化基组信息"""
        self.name=name
    
    def setDefault(self):
        """使用默认数据"""
        if self.name is None:return
        with open(Path(__file__).parent/'basis.json','r') as f:
            self.allBasis:dict=json.loads(f.read())
        
        self.names=list(self.allBasis.keys())
        transDict={
            '6-31G(d)':'6-31G*'
        }
        if name in transDict.keys():name=transDict[name]
        if name not in self.names:
            printer.wrong(f'不支持的基组{name}!!')
        self.setData(self.allBasis[name])
    
    def setData(self,basis):
        """设置数据,既可以是默认的,也可以是指定的"""
        self.basis=basis
    
    @lru_cache
    def get(self,atomic)->List:
        """根据原子序号获得基组"""
        return self.basis[str(atomic)]
    
    @lru_cache
    def lmn(self,ang:int)->list:
        """
        根据角动量获取l,m,n
        基函数中包含 x^l.y^m.z^n
        """
        res=[]
        Rs=range(ang+1)
        for l,m,n in product(Rs,Rs,Rs):
            if l+m+n==ang:res.append([l,m,n])
        return res

    def num(self,atomic:int):
        """获取基组原子对应的基函数数量"""
        shells=self.get(atomic)
        number=0
        for shell in shells:
            for ang in shell['ang']:
                lmn=self.lmn(ang)
                number+=len(lmn)
                # print(len(lmn))
        return number