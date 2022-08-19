import numpy as np
import math
from .. import utils
from typing import *
class Caculater:
    def __init__(self, program):
        self.program = program
        self.Data=self.program.Data
        self.Data.read() # 需要读取别的新的的时候再读取
        self.logger=program.logger
        self.normals={} # 计算每个原子的法向量
        self.pvectors={}
        self.pass_porbitals=[]
        self.p_vectors={} #记录p轨道方向
        self.units={} #记录成键还是反键
        self.planVectors={}
        self.samePlanes={}
        self.orders={}
        self.Batch:bool=False
        self.orbitalElectron=self.Data.orbitalElectron

    def get_Normal(self,atom_i,atom_j): #对获得标量函数的封装
        locNum=0.001
        if f'{atom_i}-{atom_j}' not in self.normals.keys(): # 每个原子的法向量应该只计算一次
            connections_i=self.Data.connections(atom_i)
            connections_j=self.Data.connections(atom_j)
            p1,p2,p3=[(self.Data.atomPos(each)-self.Data.atomPos(atom_i))*(1 if each==atom_j else locNum) for each in connections_i] #获取中心原子到三个相邻原子的法向量
            normal_vector_i=utils.get_normalVector(p1,p2,p3)
            if len(connections_j)==3:
                p1,p2,p3=[(self.Data.atomPos(each)-self.Data.atomPos(atom_j))*(1 if each==atom_j else locNum) for each in connections_j] #获取中心原子到三个相邻原子的法向量
                normal_vector_j=utils.get_normalVector(p1,p2,p3)
                if utils.vector_angle(normal_vector_i,normal_vector_j)>0.5:
                    normal_vector_j*=-1
            else:
                normal_vector_j=normal_vector_i
                self.normals[f'{atom_j}-{atom_i}']=normal_vector_j
            self.normals[f'{atom_i}-{atom_j}']=normal_vector_i
        return self.normals[f'{atom_i}-{atom_j}']


    def get_planVector(self,center,around,centerPos,aroundPos,point):
        '''计算两原子与法向量链接中点的三个点确定的平面的法向量'''
        key=f'{center}-{around}'
        if key not in self.planVectors.keys():
            normal=utils.get_normalVector(centerPos,aroundPos,point)
            self.planVectors[key]=normal
        return self.planVectors[key]
    
    def get_piOrbitals(self,center,around,orbitals):
        '''挑选出两个原子之间的Π轨道'''
        for orbital in orbitals:
            # 计算中心原子的贡献与相邻原子的贡献
            ...


    def get_orbitalOrder(self, center, around, orbital, direction): 
        '''计算两个原子间每个轨道的键级,中心原子，相邻原子，轨道，方向'''
        if self.Data.atoms[around].symbol=='H':
            return 0
        if np.linalg.norm(direction)==0:
            return 0

        self.logger.info(f'*'*70)
        self.logger.info(f'center:{center+1},around:{around+1},orbital:{orbital+1}')

        centerPos=self.Data.atomPos(center)
        aroundPos=self.Data.atomPos(around)
        bondVector=aroundPos-centerPos

        As = self.Data.As[orbital]
        centerTs=self.Data.atoms[center].pLayersTs(orbital)
        aroundTs=self.Data.atoms[around].pLayersTs(orbital)
        if np.linalg.norm(centerTs)==0 or np.linalg.norm(aroundTs)==0:
            return 0
        self.logger.info(f'{centerTs=},{aroundTs=}')
        centerTs__=utils.get_projection(centerTs,bondVector,direction)
        aroundTs__=utils.get_projection(aroundTs,bondVector,direction)
        # self.logger.info(f'{centerTs__=}\n{aroundTs__=}')
        centerPZs=[each[-1].item() for each in centerTs__]
        aroundPZs=[each[-1].item() for each in aroundTs__]
        self.logger.info(f'{centerPZs=}\n{aroundPZs=}')
        
        pOrder=sum([cpz*apz/As for cpz,apz in zip(centerPZs,aroundPZs)])*self.orbitalElectron
        orbitalOrder=pOrder
        self.logger.info(f'{As=},{center+1}-{around+1},{orbital+1},{pOrder=},electron={self.orbitalElectron}')
        self.orders[f'{center}-{around}-{orbital}']=orbitalOrder
        return orbitalOrder

    def get_order(self,center,around,orbitals,direction,fontTag):
        """计算每两个原子之间的键级"""
        orbitalNum = self.Data.orbitalNum
        orders=[self.get_orbitalOrder(center,around,orbital,direction) for orbital in orbitals] # 所有的占据轨道都计算键级

        sortRes=sorted(zip(orbitals,orders),key=lambda s:abs(s[1]),reverse=True) # 将计算出的键级与轨道根据键级绝对值大小进行排序
        orbitals=[each[0] for each in sortRes if abs(each[1])>9e-5]
        orders=[each[1].item() for each in sortRes if abs(each[1])>9e-5]
        # 打印轨道与键级
        orbitalStrs=[f'{orbital+1}' for orbital in orbitals]
        if self.Data.orbitalType==1:
            orbitalStrs=[(f'α{orbital+1}' if orbital<orbitalNum/2 else f'β{orbital+1-orbitalNum//2}') for orbital in orbitals]
        orderStrs=[f'{each:.4f}' for each in orders]
        self.formatPrint(orbitalStrs,10,8)
        self.formatPrint(orderStrs,10,8)

        bondOrder=np.sum(orders)
        bondLength=self.Data.bondLength(center,around)
        if bondOrder!=0:
            self.program.logWindow.insert('end',f'{center+1}-{around+1},BO:{bondOrder:.4f},BL:{bondLength:.4f}\n',fontTag)
        return bondOrder
    
    def calculate(self,centers:List[int]): #程序先进行自己的判断与选择
        orbitalNum = self.Data.orbitalNum
        O_orbitals=[orbital for orbital in range(orbitalNum) if self.Data.orbitals[orbital][-1]=='O']
        V_orbitals=[orbital for orbital in range(orbitalNum) if self.Data.orbitals[orbital][-1]=='V']
        # O_orbitals=V_orbitals
        orbitals=O_orbitals
        for center in centers:
            arounds=self.Data.connections(center)
            self.N=len(arounds) # 如果是sp2碳，则需要计算法向量方向的键级，如果是sp碳，则需要计算HOMO方向的键级和与HOMO垂直方向的键级
            orderSum=0 # 原子周围键级之和
            orderSum2=0
            for around in arounds:
                bondVector=self.Data.atomPos(around)-self.Data.atomPos(center)
                if self.N==3:
                    normal=self.get_Normal(center, around)
                    bondOrder=self.get_order(center, around, O_orbitals, normal,fontTag='BO')
                    orderSum+=bondOrder
                if self.N==2 or self.N==4:
                    # 从上到下找到与键轴垂直的方向的轨道作为投影方向
                    atomPos=self.Data.atomPos(center).reshape(3,1)
                    aroundPos=self.Data.atomPos(around)
                    paras=self.Data.atoms[center].basis
                    for orbital in O_orbitals[::-1]:
                        ts=self.Data.atoms[center].pLayersTs(orbital)
                        maxPos,maxValue=utils.get_extraValue(atomPos, paras, ts, 'max')
                        # print(maxPos,maxValue)
                        homoDirection=(maxPos-atomPos).flatten()
                        if np.linalg.norm(homoDirection)==0:
                            continue
                        # print(f'{homoDirection=}')
                        angle=utils.vector_angle(homoDirection, bondVector)
                        # print(f'{orbital=},{angle=}')
                        if angle==0.5:
                            break
                    if angle==0.5:
                        print(f'{homoDirection=}')
                        homoOrder=self.get_order(center, around, O_orbitals, homoDirection,fontTag='BO1')
                        cDirection=np.cross(homoDirection, bondVector)
                        # print(f'{cDirection=}')
                        cOrder=self.get_order(center, around, O_orbitals, cDirection,fontTag='BO2')
                    else:
                        homoOrder=cOrder=0
                    orderSum+=homoOrder
                    orderSum2+=cOrder
                    
            FV=2-orderSum
            self.program.logWindow.insert('end',f'{center+1},FV:{FV:.4f}\n','FV')
            if self.N==2:
                self.program.logWindow.insert('end',f'{center+1},FV:{2-orderSum2:.4f}\n','FV')

    def formatPrint(self,contents:List[str],number:int,length:int):
        '''
        将列表内容格式化打印
        contents:要打印的内容
        num:每行打印的数量
        len:打印每个元素的长度
        '''
        for i in range(0,len(contents),number):
            string=''.join([each.rjust(length) for each in contents[i:i+number]])
            self.program.logWindow.insert('end',f'{string}\n')
