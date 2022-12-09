"""
轨道分解法+Mayer计算π键级
根据投影计算新的分子轨道系数矩阵,然后重构密度矩阵
"""
from pywfn import setting

from pywfn.maths import vector_angle
from ..base import Mol,Atom
from typing import *
import numpy as np
from.utils import CM2PM,CM2PMs
from colorama import Fore
import multiprocessing as mp
from tqdm import tqdm

class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol

    
    def calculate(self,centerAtom:Atom,aroundAtom:Atom):
        if centerAtom.symbol=='H' or aroundAtom.symbol=='H':
            # print(Fore.YELLOW+'不能计算含有H的键')
            return 0
        self.mol.createAtomOrbitalRange()
        CM_=np.zeros_like(self.mol.CM,dtype=np.float32) #新的系数矩阵
        orbitals=self.mol.O_obts #占据轨道的索引

        normal=centerAtom.get_Normal(aroundAtom.idx)
        if normal is None:
            print(Fore.RED+'中心原子没有法向量')
            for orbital in orbitals[::-1]:
                direction=centerAtom.get_obtWay(orbital)
                if vector_angle(direction,aroundAtom.coord-centerAtom.coord,trans=True)<0.1:
                    normal=direction
                    break

        a1_1,a1_2=centerAtom.obtMatrixRange
        a2_1,a2_2=aroundAtom.obtMatrixRange
        centerPIndex=[i for i,l in enumerate(centerAtom.layers) if 'P' in l]
        aroundPIndex=[i for i,l in enumerate(aroundAtom.layers) if 'P' in l]
        for i,orbital in enumerate(orbitals):
            C1op=centerAtom.get_pProj(normal,orbital)
            C2op=aroundAtom.get_pProj(normal,orbital)
            C1o=np.zeros(len(centerAtom.layers))
            C2o=np.zeros(len(aroundAtom.layers))
            C1o[centerPIndex]=np.concatenate(C1op)
            C2o[aroundPIndex]=np.concatenate(C2op)
            CM_[a1_1:a1_2,orbital]=C1o
            CM_[a2_1:a2_2,orbital]=C2o
            # progress('重构密度矩阵',i+1,len(orbitals))
        oe=1 if self.mol.isOpenShell else 2
        n=[oe if 'O' in o else 0 for o in self.mol.orbitals]
        SM=self.mol.SM
        

        self.centerAtom=centerAtom
        self.aroundAtom=aroundAtom
        self.obtNum=obtNum=len(orbitals)
        
        if setting.IF_ORBITAL_ORDER: # 是否拆分轨道键级成分
            self.PMs_=CM2PMs(CM_,orbitals,oe) #三维数组
            self.PSs=self.PMs_@SM
            OM=self.get_OM() # 键级矩阵
            orders=OM.sum(axis=0)
            order=np.sqrt(np.abs(np.sum(orders)))
            ratios=orders/np.sum(orders)*order
            printOrders(ratios,self.mol.orbital_symbols)
            return order
        else:
            PM_=CM2PM(CM_,orbitals,oe)
            PS=PM_@SM
            order=np.sum(PS[a1_1:a1_2,a2_1:a2_2]*PS[a2_1:a2_2,a1_1:a1_2].T)
            return np.sqrt(np.abs(order))

    def get_OMi(self,idx): #计算一个矩阵元
        i,j=idx
        a1,a2=self.centerAtom.obtMatrixRange
        b1,b2=self.aroundAtom.obtMatrixRange
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

def printOrders(orders,orbitals):
    """将轨道根据大小排序后输出"""
    orders_=[f'{order:.4f}' for order in orders]
    sortedRes=sorted(list(zip(orbitals,orders_)),key=lambda e:abs(float(e[1])),reverse=True)
    sortedRes=[e for e in sortedRes if abs(float(e[1]))>=0.01]
    sortedRes=list(zip(*sortedRes))    
    formPrint(sortedRes,8,10)

def formPrint(contents:List[List[str]],eachLength:int,lineNum:int):
    """格式化打印列表内容，contents是一个列表，其中的每一项是一个包含字符串的列表，每个字符串列表长度必须相同"""
    logs=[]
    for content in contents:
        logs.append([])
        for i in range(0,len(content),lineNum):
            text=''.join([f'{each}'.rjust(eachLength,' ') for each in content[i:i+lineNum]])
            logs[-1].append(text)
    if len(logs)==0:
        return
    for i in range(len(logs[0])):
        for log in logs:
            print(log[i])
