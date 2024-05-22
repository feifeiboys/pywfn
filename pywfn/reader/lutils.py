"""
定义所有读取类的基类
默认读取的所有信息返回为空
不同类型的文件覆盖不同的读取函数

可以为每个分子对象分配一个Reader对象
用户可以自己分配分子属性，也可以从文件中读取
当调用分子属性且未分配时，会通过reader对象读取属性，若读取失败则报错
每一个方法都需要被子例覆盖

- 原子类型
- 原子坐标
- 轨道系数，[n,n]/[n,2n]
- 分子能量
- 原子轨道所属原子
- 原子轨道角动量类型
- 分子轨道能量
- 分子轨道占据类型 占据|非占据
- 重叠矩阵
- 波函数类型 开壳层/闭壳层
"""
from pywfn import base
from pywfn import data
import numpy as np
from pathlib import Path
from functools import cached_property
import linecache
from pywfn.utils import printer
from typing import Callable
import os

class Reader:
    def __init__(self,path:str) -> None:
        self.path:str=path
        fold=Path(path).parent/f'{Path(path).suffix}#{Path(path).stem}'
        if not fold.exists():
            os.mkdir(f'{fold}')
        self.dfold=f'{fold}' # 数据存储路径
    
    @cached_property
    def text(self)->str:
        """获取文件的所有文本，小文件可以这么干，大文件就算了"""
        return Path(self.path).read_text()

    @property
    def fname(self)->str:
        return Path(self.path).name
    
    @cached_property
    def lineNum(self)->int:
        """获取文件行数"""
        lineNum=0
        with open(self.path,'r') as file:
            for _ in file:
                lineNum+=1
        return lineNum
    
    def getline(self,idx:int,keepEnd:bool=True)->str:
        if keepEnd:
            return linecache.getline(self.path,idx+1)
        else:
            return linecache.getline(self.path,idx+1).replace('\n','')
    
    def getlines(self,idx1:int,idx2:int)->list[str]:
        lines=[]
        for i in range(idx1,idx2):
            lines.append(self.getline(i))
        return lines


    def get_coords(self)->np.ndarray:
        """原子坐标[n,3]"""
        raise ValueError("未继承的函数")

    def get_symbols(self)->list[str]:
        """原子符号[n]"""
        raise ValueError("未继承的函数")

    def get_energy(self)->float:
        """获取分子能量"""
        raise ValueError("未继承的函数")

    def get_charge(self)->int:
        """获取分子电荷"""
        raise ValueError("未继承的函数")

    def get_spin(self)->int:
        """获取分子自旋"""
        raise ValueError("未继承的函数")

    def get_CM(self)->np.ndarray:
        """获取系数矩阵[m,m]/[m,2m]"""
        raise ValueError("未继承的函数")

    def get_SM(self)->np.ndarray:
        """获取重叠矩阵[m,m]"""
        raise ValueError("未继承的函数")

    def get_obtEngs(self)->list[float]:
        """获取分子轨道能量[m]"""
        raise ValueError("未继承的函数")

    def get_obtOccs(self)->list[bool]:
        """获取轨道类型，占据|非占据[m]"""
        raise

    def get_obtAtms(self)->list[int]:
        """获取轨道系数每一行对应的原子[m]"""
        raise ValueError("未继承的函数")

    def get_obtShls(self)->list[int]:
        """获取轨道系数每一行对应的原子层[m]"""
        raise ValueError("未继承的函数")
    
    def get_obtSyms(self)->list[float]:
        """获取轨道系数每一行对应的轨道符号(S,PX,PY...)"""
        raise ValueError("未继承的函数")
    
    def get_basis(self)->"data.Basis":
        """获取基组数据[m,4]
        元素,层数,角动量,指数,系数
        """
        raise ValueError("未继承的函数")
    
    def load_fdata(self,name:str)->np.ndarray|list:
        """获取保存的数据"""
        path=Path(self.dfold)/name
        if not path.exists():return None
        return np.load(path)
    
    def save_fdata(self,name:str,data:np.ndarray|list):
        """保存数据"""
        path=Path(self.dfold)/name
        np.save(path,data)