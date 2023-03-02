"""
轨道分解法+Mayer计算π键级
根据投影计算新的分子轨道系数矩阵,然后重构密度矩阵
"""
from pywfn import setting

from pywfn.maths import vector_angle
from ..base import Mol,Atom
from typing import *
import numpy as np
from .utils import CM2PM,CM2PMs
from .utils import printOrders
from colorama import Fore
import multiprocessing as mp
from tqdm import tqdm
from . import Caler

class Calculator(Caler):
    def __init__(self,mol:Mol) -> None:
        self.mol=mol
        """计算某个方向的"""

    def calculate(self,idx1:int,idx2:int)->float:
        centerAtom=self.mol.atom(idx1)
        aroundAtom=self.mol.atom(idx2)
        if centerAtom.symbol=='H' or aroundAtom.symbol=='H':
            # print(Fore.YELLOW+'不能计算含有H的键')
            return 0
        # CM_=np.zeros_like(self.mol.CM,dtype=np.float32) #新的系数矩阵
        obts=self.mol.O_obts #占据轨道的索引

        normal=centerAtom.get_Normal(aroundAtom.idx)
        
        if normal is not None:
            return self.calerWay(idx1,idx2,obts,normal)
        else:
            print(Fore.RED+'中心原子没有法向量')
            bondVector=aroundAtom.coord-centerAtom.coord
            for orbital in obts[::-1]: #从HOMO轨道开始寻找与键轴夹角最小的方向作为法向量方向
                direction=centerAtom.get_obtWay(orbital)
                if vector_angle(direction,bondVector,trans=True)>0.4:
                    normal=direction
                    break
            if normal is None:return 0
            crossVector=np.cross(bondVector,normal)
            return self.calerWay(idx1,idx2,obts,normal),self.calerWay(idx1,idx2,obts,crossVector)
        
        

    def calerWay(self,idx1:int,idx2:int,obts,norm):
        centerAtom=self.mol.atom(idx1)
        aroundAtom=self.mol.atom(idx2)
        a_1,a_2=centerAtom.obtRange
        b_1,b_2=aroundAtom.obtRange
        CM_=self.mol.projCM(atoms=[centerAtom,aroundAtom],obts=obts,norm=norm)

        oe=1 if self.mol.isOpenShell else 2
        # n=[oe if 'O' in o else 0 for o in self.mol.obtStr]
        SM=self.mol.SM
        

        self.centerAtom=centerAtom
        self.aroundAtom=aroundAtom
        
        # if setting.IF_ORBITAL_ORDER: # 是否拆分轨道键级成分
        #     self.PMs_=CM2PMs(CM_,obts,oe) #三维数组
        #     self.PSs=self.PMs_@SM
        #     OM=self.get_OM() # 键级矩阵
        #     orders=OM.sum(axis=0)
        #     order=np.sqrt(np.abs(np.sum(orders)))
        #     ratios=orders/np.sum(orders)*order
        #     printOrders(ratios,self.mol.orbital_symbols)
        #     return order
        # else:
        PM_=CM2PM(CM_,obts,oe)
        PS=PM_@SM
        order=np.sum(PS[a_1:a_2,b_1:b_2]*PS[b_1:b_2,a_1:a_2].T)
        print(order)
        # return order
        return np.sqrt(np.abs(order))
    
    def get_OMi(self,idx): #计算一个矩阵元
        i,j=idx
        a1,a2=self.centerAtom.obtRange
        b1,b2=self.aroundAtom.obtRange
        PSi=self.PSs[i,:,:]
        PSj=self.PSs[j,:,:]
        res=np.sum(PSi[a1:a2,b1:b2]*PSj[b1:b2,a1:a2].T)
        return res

    def get_OM(self): # 计算键级矩阵,每两个原子轨道之间有一个键级
        obtNum=self.obtNum # 占据轨道的数量
        OM=np.zeros(shape=(obtNum,obtNum)) # 轨道键级矩阵，是一个对称矩阵
        idxs=get_idxs(obtNum)
        for i,j in tqdm(idxs,total=len(idxs),desc='构建键级矩阵'):
            v=self.get_OMi((i,j))
            OM[i,j]=v
        # OM是一个下三角矩阵,将其转为对角矩阵
        OM+=np.tril(OM.T,-1)
        return OM


def get_idxs(n):
    """返回下三角矩阵的索引"""
    return [[i,j] for j in range(n) for i in range(n) if j<=i]